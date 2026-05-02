// State
let selectedFiles = [];
let sessionId = null;
let quality = 'medium';

// Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileCount = document.getElementById('fileCount');
const totalSize = document.getElementById('totalSize');
const fpsRange = document.getElementById('fpsRange');
const fpsValue = document.getElementById('fpsValue');
const durationPreview = document.getElementById('durationPreview');
const startConvert = document.getElementById('startConvert');
const progressPercent = document.getElementById('progressPercent');
const progressStatus = document.getElementById('progressStatus');
const downloadBtn = document.getElementById('downloadBtn');
const convertAgain = document.getElementById('convertAgain');

// --- STEP NAVIGATION ---
function showStep(stepId) {
    document.querySelectorAll('.step-card').forEach(s => {
        s.style.display = 'none';
        s.classList.remove('active');
    });
    const step = document.getElementById(stepId);
    if (step) {
        step.style.display = 'block';
        setTimeout(() => step.classList.add('active'), 10);
    }
}

// --- DRAG & DROP ---
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    const allFiles = Array.from(files);
    const pngFiles = allFiles.filter(f => f.name.toLowerCase().endsWith('.png'));
    const zipFiles = allFiles.filter(f => f.name.toLowerCase().endsWith('.zip'));

    selectedFiles = [...pngFiles, ...zipFiles];
    selectedFiles.sort((a, b) => a.name.localeCompare(b.name));

    if (selectedFiles.length === 0) {
        alert('PNG yoki ZIP fayllar topilmadi!');
        return;
    }

    const total = selectedFiles.reduce((sum, f) => sum + f.size, 0);
    
    if (zipFiles.length > 0) {
        fileCount.textContent = zipFiles.length + ' ZIP';
    } else {
        fileCount.textContent = pngFiles.length;
    }
    
    totalSize.textContent = formatSize(total);
    fileInfo.style.display = 'grid';

    // Auto-advance to settings after a moment
    setTimeout(() => {
        showStep('step-settings');
        updateDuration();
    }, 800);
}

// --- SETTINGS ---
fpsRange.addEventListener('input', () => {
    fpsValue.textContent = fpsRange.value;
    updateDuration();
});

document.querySelectorAll('.q-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.q-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        quality = btn.dataset.quality;
    });
});

function updateDuration() {
    const fps = parseInt(fpsRange.value);
    const frames = selectedFiles.length;
    const seconds = (frames / fps).toFixed(1);
    durationPreview.textContent = `${seconds}s (${frames} kadr, ${fps} FPS)`;
}

// --- UPLOAD & CONVERT ---
startConvert.addEventListener('click', async () => {
    startConvert.disabled = true;
    startConvert.classList.add('loading');
    startConvert.querySelector('span').textContent = 'Yuklanmoqda...';

    // Upload files
    const formData = new FormData();
    selectedFiles.forEach(f => formData.append('files', f));

    try {
        const uploadRes = await fetch('/upload', { method: 'POST', body: formData });
        const uploadData = await uploadRes.json();

        if (!uploadRes.ok) {
            alert(uploadData.error || 'Yuklashda xatolik');
            resetConvertBtn();
            return;
        }

        sessionId = uploadData.session_id;

        // Start conversion
        const convertRes = await fetch('/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                fps: parseInt(fpsRange.value),
                quality: quality
            })
        });

        if (!convertRes.ok) {
            alert('Konvertatsiyada xatolik');
            resetConvertBtn();
            return;
        }

        // Show progress
        showStep('step-progress');
        pollProgress();

    } catch (err) {
        alert('Tarmoq xatosi: ' + err.message);
        resetConvertBtn();
    }
});

function resetConvertBtn() {
    startConvert.disabled = false;
    startConvert.classList.remove('loading');
    startConvert.querySelector('span').textContent = 'Konvertatsiyani boshlash';
}

// --- PROGRESS POLLING ---
async function pollProgress() {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/progress/${sessionId}`);
            const data = await res.json();

            const progress = data.progress || 0;
            progressPercent.textContent = progress + '%';

            if (data.status === 'done') {
                clearInterval(interval);
                progressPercent.textContent = '100%';
                progressStatus.textContent = 'Tugallandi!';

                setTimeout(() => showResult(data), 800);
            } else if (data.status === 'error') {
                clearInterval(interval);
                progressStatus.textContent = 'Xatolik yuz berdi';
                alert('FFmpeg xatosi: ' + data.error);
            }
        } catch (e) {
            // Keep polling
        }
    }, 800);
}

function showResult(data) {
    showStep('step-result');

    document.getElementById('resultInputSize').textContent = formatSize(data.input_size);
    document.getElementById('resultOutputSize').textContent = formatSize(data.output_size);
    document.getElementById('resultReduction').textContent = data.reduction + '%';

    downloadBtn.href = `/download/${sessionId}`;
}

// --- CONVERT AGAIN ---
convertAgain.addEventListener('click', () => {
    selectedFiles = [];
    sessionId = null;
    fileInfo.style.display = 'none';
    fileInput.value = '';
    resetConvertBtn();
    showStep('step-upload');
});

// --- UTILS ---
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}
