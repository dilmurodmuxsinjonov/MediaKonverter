import os
import uuid
import subprocess
import shutil
import threading
import json
import zipfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Store conversion progress
conversions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Receive uploaded PNG or ZIP files and store them."""
    if 'files' not in request.files:
        return jsonify({'error': 'Fayllar topilmadi'}), 400

    files = request.files.getlist('files')

    # Create unique session folder
    session_id = str(uuid.uuid4())[:8]
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Check if a ZIP file was uploaded
    zip_files = [f for f in files if f.filename.lower().endswith('.zip')]
    png_files = [f for f in files if f.filename.lower().endswith('.png')]

    if zip_files:
        # Handle ZIP upload — extract PNGs from each ZIP
        for zf in zip_files:
            zip_path = os.path.join(upload_dir, 'temp.zip')
            zf.save(zip_path)
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    for member in z.namelist():
                        # Skip directories and hidden files
                        if member.endswith('/') or member.startswith('__'):
                            continue
                        basename = os.path.basename(member)
                        if basename.lower().endswith('.png'):
                            # Extract to upload dir with original name
                            data = z.read(member)
                            with open(os.path.join(upload_dir, basename), 'wb') as out:
                                out.write(data)
            finally:
                os.remove(zip_path)

    elif png_files:
        # Handle direct PNG uploads
        for f in png_files:
            f.save(os.path.join(upload_dir, f.filename))
    else:
        shutil.rmtree(upload_dir, ignore_errors=True)
        return jsonify({'error': 'PNG yoki ZIP fayllar topilmadi'}), 400

    # Rename all PNGs in sorted order
    all_pngs = sorted([f for f in os.listdir(upload_dir) if f.lower().endswith('.png')])

    if not all_pngs:
        shutil.rmtree(upload_dir, ignore_errors=True)
        return jsonify({'error': 'ZIP ichida PNG fayllar topilmadi'}), 400

    for i, fname in enumerate(all_pngs, start=1):
        new_name = f"{i:05d}.png"
        old_path = os.path.join(upload_dir, fname)
        new_path = os.path.join(upload_dir, new_name)
        if old_path != new_path:
            os.rename(old_path, new_path)

    return jsonify({
        'session_id': session_id,
        'file_count': len(all_pngs),
        'message': f'{len(all_pngs)} ta PNG fayl yuklandi'
    })

@app.route('/convert', methods=['POST'])
def convert():
    """Start conversion of uploaded PNGs to WebM."""
    data = request.get_json()
    session_id = data.get('session_id')
    fps = data.get('fps', 30)
    quality = data.get('quality', 'medium')  # low, medium, high
    remove_green = data.get('remove_green', False)

    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    if not os.path.exists(upload_dir):
        return jsonify({'error': 'Session topilmadi'}), 404

    # Map quality to CRF values (lower = better quality, bigger file)
    quality_map = {
        'low': 40,
        'medium': 32,
        'high': 20
    }
    crf = quality_map.get(quality, 32)

    output_name = f"{session_id}.webm"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)

    conversions[session_id] = {
        'status': 'processing',
        'progress': 0,
        'output_file': output_name
    }

    # Run conversion in background thread
    thread = threading.Thread(
        target=run_conversion,
        args=(session_id, upload_dir, output_path, fps, crf, remove_green)
    )
    thread.start()

    return jsonify({'message': 'Konvertatsiya boshlandi', 'session_id': session_id})

def run_conversion(session_id, input_dir, output_path, fps, crf, remove_green):
    """Run FFmpeg conversion in background."""
    try:
        # Count total frames
        total_frames = len(list(Path(input_dir).glob('*.png')))
        conversions[session_id]['total_frames'] = total_frames

        # Build ffmpeg command
        input_pattern = os.path.join(input_dir, '%05d.png')

        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', input_pattern,
            '-c:v', 'libvpx-vp9',
            '-pix_fmt', 'yuva420p',
            '-auto-alt-ref', '0',
            '-crf', str(crf),
            '-b:v', '0',
            '-progress', 'pipe:1',
            output_path
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Parse progress from ffmpeg
        for line in process.stdout:
            line = line.strip()
            if line.startswith('frame='):
                try:
                    frame_num = int(line.split('=')[1])
                    conversions[session_id]['progress'] = min(
                        int((frame_num / total_frames) * 100), 99
                    )
                except:
                    pass

        process.wait()

        if process.returncode == 0:
            # Get output file size
            output_size = os.path.getsize(output_path)
            # Get input total size
            input_size = sum(
                f.stat().st_size for f in Path(input_dir).glob('*.png')
            )

            conversions[session_id].update({
                'status': 'done',
                'progress': 100,
                'input_size': input_size,
                'output_size': output_size,
                'reduction': round(100 - (output_size / input_size * 100), 1)
            })
        else:
            stderr = process.stderr.read()
            conversions[session_id].update({
                'status': 'error',
                'error': stderr[:500]
            })

    except Exception as e:
        conversions[session_id].update({
            'status': 'error',
            'error': str(e)
        })
    finally:
        # Clean up uploaded files
        shutil.rmtree(input_dir, ignore_errors=True)

@app.route('/progress/<session_id>')
def progress(session_id):
    """Get conversion progress."""
    if session_id not in conversions:
        return jsonify({'error': 'Session topilmadi'}), 404
    return jsonify(conversions[session_id])

@app.route('/download/<session_id>')
def download(session_id):
    """Download the converted WebM file."""
    if session_id not in conversions:
        return jsonify({'error': 'Session topilmadi'}), 404

    info = conversions[session_id]
    if info['status'] != 'done':
        return jsonify({'error': 'Fayl hali tayyor emas'}), 400

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], info['output_file'])
    return send_file(output_path, as_attachment=True, download_name='animation_alpha.webm')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
