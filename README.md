# MediaKonverter 🎬

A professional tool to convert transparent PNG sequences into high-quality **WebM** videos while fully preserving alpha channel transparency.

## 📥 Download
You can download the ready-to-use Windows installer from the **[Releases](https://github.com/dilmurodmuxsinjonov/MediaKonverter/releases)** page.

1. Go to the **Releases** section.
2. Download `MediaKonverter_Setup.exe`.
3. Run the installer and follow the instructions.

## 🌟 Features
- **Batch Processing**: Handle hundreds of PNG files or ZIP archives simultaneously.
- **Alpha Channel Support**: Maintains full transparency in the output WebM video.
- **Modern UI**: Sleek, intuitive, and responsive interface featuring a premium Glassmorphism design.
- **High Performance**: Powered by FFmpeg for rapid and efficient conversion.
- **Quality Control**: Custom settings for frame rate (FPS) and video quality levels.

## 🛠 Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
- **Core Engine**: FFmpeg

## 🚀 Development Setup

1. **Install Dependencies:**
   ```bash
   pip install flask
   ```

2. **Run the Application:**
   ```bash
   python converter/app.py
   ```

3. **Access in Browser:**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure
- `converter/`: Main Flask application and UI assets.
- `uploads/`: Temporary storage for uploaded files.
- `output/`: Storage for generated WebM videos.

## 📝 Author
Created by [Dilmurod].
