const canvas = document.getElementById('animation-canvas');
const ctx = canvas.getContext('2d');
const video = document.getElementById('animation-video');
const animContainer = document.getElementById('animation-container');

const TOTAL_FRAMES = 207;
const DURATION = 2500; // 2.5 seconds

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

async function playAnimation(format) {
    const btn = event.target;
    const originalText = btn.innerText;
    btn.innerText = "Yuklanmoqda...";
    btn.disabled = true;

    if (format === 'video') {
        video.src = 'assets/video.webm';
        video.load();
        
        return new Promise((resolve) => {
            video.oncanplaythrough = () => {
                btn.innerText = originalText;
                btn.disabled = false;
                animContainer.style.display = 'block';
                canvas.style.display = 'none';
                video.style.display = 'block';
                
                video.play();
                
                video.onended = () => {
                    animContainer.style.display = 'none';
                    video.style.display = 'none';
                    resolve();
                };
            };
        });
    }

    const folder = format === 'png' ? 'assets/png' : 'assets/webp';
    const ext = format;
    const frames = [];
    const loadPromises = [];

    for (let i = 1; i <= TOTAL_FRAMES; i++) {
        const img = new Image();
        const promise = new Promise((resolve) => {
            img.onload = resolve;
            img.onerror = resolve;
        });
        img.src = `${folder}/${String(i).padStart(5, '0')}.${ext}`;
        frames.push(img);
        loadPromises.push(promise);
    }

    await Promise.all(loadPromises);
    
    btn.innerText = originalText;
    btn.disabled = false;
    animContainer.style.display = 'block';
    video.style.display = 'none';
    canvas.style.display = 'block';

    return new Promise((resolve) => {
        let currentFrame = 0;
        const startTime = performance.now();

        function render() {
            const now = performance.now();
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / DURATION, 1);
            
            currentFrame = Math.floor(progress * (TOTAL_FRAMES - 1));

            if (frames[currentFrame]) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const img = frames[currentFrame];
                if (img.complete && img.naturalWidth > 0) {
                    const imgRatio = img.width / img.height;
                    const canvasRatio = canvas.width / canvas.height;
                    let drawW, drawH, drawX, drawY;
                    if (canvasRatio > imgRatio) {
                        drawW = canvas.width; drawH = canvas.width / imgRatio;
                        drawX = 0; drawY = (canvas.height - drawH) / 2;
                    } else {
                        drawH = canvas.height; drawW = canvas.height * imgRatio;
                        drawX = (canvas.width - drawW) / 2; drawY = 0;
                    }
                    ctx.drawImage(img, drawX, drawY, drawW, drawH);
                }
            }

            if (progress < 1) {
                requestAnimationFrame(render);
            } else {
                setTimeout(() => {
                    animContainer.style.display = 'none';
                    resolve();
                }, 100);
            }
        }
        requestAnimationFrame(render);
    });
}

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

async function transitionToPage2() {
    await playAnimation('png');
    showPage('page2');
}

async function transitionToPage3() {
    await playAnimation('webp');
    showPage('page3');
}

async function transitionToPage4() {
    await playAnimation('video');
    showPage('page4');
}

function restart() {
    showPage('page1');
}
