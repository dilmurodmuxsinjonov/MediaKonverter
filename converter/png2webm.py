"""
Media Konverter (Desktop)
PNG/ZIP → WebM | Video → PNG (ZIP) | Video → WebM
Ishga tushirish: python png2webm.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import zipfile
import shutil
import tempfile
import json
from pathlib import Path


class MediaConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Konverter")
        self.root.geometry("620x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b0b0f")

        # Try to set icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

        # State
        self.png_files = []
        self.video_path = None
        self.temp_dir = None
        self.output_path = None
        self.is_converting = False
        self.mode = "png2webm"  # png2webm | video2png | video2webm

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        self.build_ui()

    def configure_styles(self):
        bg = "#0b0b0f"
        card = "#1a1a28"
        border = "#2a2a40"
        accent = "#6366f1"
        text = "#f0f0ff"
        muted = "#8888aa"

        self.style.configure("TFrame", background=bg)
        self.style.configure("Card.TFrame", background=card)
        self.style.configure("TLabel", background=bg, foreground=text, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=bg, foreground=text, font=("Segoe UI", 16, "bold"))
        self.style.configure("Sub.TLabel", background=bg, foreground=muted, font=("Segoe UI", 9))
        self.style.configure("CardTitle.TLabel", background=card, foreground=text, font=("Segoe UI", 10, "bold"))
        self.style.configure("CardSub.TLabel", background=card, foreground=muted, font=("Segoe UI", 9))
        self.style.configure("Result.TLabel", background=bg, foreground=text, font=("Segoe UI", 10))

        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=border, background=accent, thickness=12, borderwidth=0,
        )

    def build_ui(self):
        main = ttk.Frame(self.root, padding=24)
        main.pack(fill="both", expand=True)
        self.main_frame = main

        # Title
        ttk.Label(main, text="🎬 Media Konverter", style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(main, text="PNG, ZIP, Video → WebM / PNG konvertatsiya", style="Sub.TLabel").pack(pady=(0, 16))

        # --- File Selection (4 buttons) ---
        file_frame = ttk.Frame(main)
        file_frame.pack(fill="x", pady=(0, 4))

        row1 = ttk.Frame(file_frame)
        row1.pack(fill="x", pady=(0, 4))

        self.make_btn(row1, "📁 PNG tanlash", self.select_pngs, "#1a1a28").pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.make_btn(row1, "📦 ZIP tanlash", self.select_zip, "#1a1a28").pack(side="left", expand=True, fill="x", padx=(3, 0))

        row2 = ttk.Frame(file_frame)
        row2.pack(fill="x")

        self.make_btn(row2, "🎥 Video → PNG (ZIP)", self.select_video_to_png, "#1a2828").pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.make_btn(row2, "🎥 Video → WebM", self.select_video_to_webm, "#1a2828").pack(side="left", expand=True, fill="x", padx=(3, 0))

        self.file_label = ttk.Label(main, text="Hech qanday fayl tanlanmagan", style="Sub.TLabel")
        self.file_label.pack(pady=(6, 12))

        # --- Settings ---
        settings_frame = ttk.Frame(main, style="Card.TFrame", padding=14)
        settings_frame.pack(fill="x", pady=(0, 10))
        self.settings_frame = settings_frame

        ttk.Label(settings_frame, text="⚙️ Sozlamalar", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        # FPS
        fps_row = ttk.Frame(settings_frame, style="Card.TFrame")
        fps_row.pack(fill="x", pady=(0, 6))
        ttk.Label(fps_row, text="FPS:", style="CardSub.TLabel").pack(side="left")
        self.fps_label = ttk.Label(fps_row, text="30", style="CardTitle.TLabel")
        self.fps_label.pack(side="right")

        self.fps_var = tk.IntVar(value=30)
        self.fps_scale = tk.Scale(
            settings_frame, from_=1, to=120, orient="horizontal",
            variable=self.fps_var, command=self.on_fps_change,
            bg="#1a1a28", fg="#f0f0ff", troughcolor="#2a2a40",
            highlightthickness=0, sliderrelief="flat", bd=0,
            activebackground="#6366f1", font=("Segoe UI", 1)
        )
        self.fps_scale.pack(fill="x", pady=(0, 6))

        # Quality
        qual_row = ttk.Frame(settings_frame, style="Card.TFrame")
        qual_row.pack(fill="x", pady=(0, 6))
        ttk.Label(qual_row, text="Sifat:", style="CardSub.TLabel").pack(side="left")
        self.quality_var = tk.StringVar(value="medium")
        qual_btns = ttk.Frame(qual_row, style="Card.TFrame")
        qual_btns.pack(side="right")
        for val, label in [("low", "Past"), ("medium", "O'rta"), ("high", "Yuqori")]:
            rb = tk.Radiobutton(
                qual_btns, text=label, variable=self.quality_var, value=val,
                bg="#1a1a28", fg="#f0f0ff", selectcolor="#6366f1",
                activebackground="#1a1a28", activeforeground="#f0f0ff",
                font=("Segoe UI", 9), indicatoron=0, padx=12, pady=3,
                relief="flat", cursor="hand2"
            )
            rb.pack(side="left", padx=2)

        # Resolution
        res_row = ttk.Frame(settings_frame, style="Card.TFrame")
        res_row.pack(fill="x", pady=(0, 4))
        ttk.Label(res_row, text="Ruxsat:", style="CardSub.TLabel").pack(side="left")
        self.resolution_var = tk.StringVar(value="original")
        res_btns = ttk.Frame(res_row, style="Card.TFrame")
        res_btns.pack(side="right")
        for val, label in [("4320", "4K"), ("2160", "2K"), ("1080", "1080p"), ("original", "Asl"), ("720", "720p"), ("480", "480p")]:
            rb = tk.Radiobutton(
                res_btns, text=label, variable=self.resolution_var, value=val,
                bg="#1a1a28", fg="#f0f0ff", selectcolor="#6366f1",
                activebackground="#1a1a28", activeforeground="#f0f0ff",
                font=("Segoe UI", 9), indicatoron=0, padx=8, pady=3,
                relief="flat", cursor="hand2"
            )
            rb.pack(side="left", padx=1)

        # Info label
        self.duration_label = ttk.Label(settings_frame, text="", style="CardSub.TLabel")
        self.duration_label.pack(anchor="w", pady=(4, 0))

        # --- Progress ---
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main, variable=self.progress_var, maximum=100,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(0, 4))

        self.progress_label = ttk.Label(main, text="", style="Sub.TLabel")
        self.progress_label.pack(pady=(0, 10))

        # --- Action Button ---
        self.btn_convert = tk.Button(
            main, text="▶  Boshlash", command=self.start_action,
            bg="#6366f1", fg="white", activebackground="#4f46e5", activeforeground="white",
            font=("Segoe UI", 12, "bold"), relief="flat", padx=20, pady=10,
            cursor="hand2", state="disabled"
        )
        self.btn_convert.pack(fill="x", pady=(0, 6))

        # --- Result ---
        self.result_frame = ttk.Frame(main)
        self.result_label = ttk.Label(self.result_frame, text="", style="Result.TLabel")
        self.result_label.pack()

        self.btn_open = tk.Button(
            self.result_frame, text="📂 Papkani ochish", command=self.open_output_folder,
            bg="#10b981", fg="white", activebackground="#059669", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=6, cursor="hand2"
        )

    def make_btn(self, parent, text, cmd, bg="#1a1a28"):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=bg, fg="#f0f0ff", activebackground="#2a2a40", activeforeground="#f0f0ff",
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=7, cursor="hand2"
        )

    # ============ FILE SELECTION ============

    def select_pngs(self):
        files = filedialog.askopenfilenames(
            title="PNG fayllarni tanlang",
            filetypes=[("PNG fayllar", "*.png")]
        )
        if files:
            self.mode = "png2webm"
            self.video_path = None
            self.png_files = sorted(files)
            self.file_label.config(text=f"✅ {len(self.png_files)} ta PNG → WebM")
            self.btn_convert.config(state="normal", text="▶  WebM ga aylantirish")
            self.update_duration()

    def select_zip(self):
        zip_path = filedialog.askopenfilename(
            title="ZIP faylni tanlang",
            filetypes=[("ZIP fayllar", "*.zip")]
        )
        if zip_path:
            self.mode = "png2webm"
            self.video_path = None
            self.cleanup_temp()
            self.temp_dir = tempfile.mkdtemp(prefix="conv_")
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    count = 0
                    for member in z.namelist():
                        if member.endswith('/') or member.startswith('__'):
                            continue
                        basename = os.path.basename(member)
                        if basename.lower().endswith('.png'):
                            data = z.read(member)
                            with open(os.path.join(self.temp_dir, basename), 'wb') as out:
                                out.write(data)
                            count += 1
                if count == 0:
                    messagebox.showwarning("Ogohlantirish", "ZIP ichida PNG topilmadi!")
                    return
                self.png_files = sorted(
                    [os.path.join(self.temp_dir, f) for f in os.listdir(self.temp_dir) if f.lower().endswith('.png')]
                )
                self.file_label.config(text=f"✅ {count} ta PNG (ZIP) → WebM")
                self.btn_convert.config(state="normal", text="▶  WebM ga aylantirish")
                self.update_duration()
            except Exception as e:
                messagebox.showerror("Xatolik", f"ZIP xatosi:\n{e}")

    def select_video_to_png(self):
        path = filedialog.askopenfilename(
            title="Video faylni tanlang",
            filetypes=[("Video fayllar", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv")]
        )
        if path:
            self.mode = "video2png"
            self.video_path = path
            self.png_files = []
            name = os.path.basename(path)
            self.file_label.config(text=f"🎥 {name} → PNG (ZIP)")
            self.btn_convert.config(state="normal", text="▶  PNG ga ajratish (ZIP)")
            self.update_video_info()

    def select_video_to_webm(self):
        path = filedialog.askopenfilename(
            title="Video faylni tanlang",
            filetypes=[("Video fayllar", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv")]
        )
        if path:
            self.mode = "video2webm"
            self.video_path = path
            self.png_files = []
            name = os.path.basename(path)
            self.file_label.config(text=f"🎥 {name} → WebM")
            self.btn_convert.config(state="normal", text="▶  WebM ga aylantirish")
            self.update_video_info()

    # ============ INFO UPDATES ============

    def on_fps_change(self, val):
        self.fps_label.config(text=str(int(float(val))))
        self.update_duration()

    def update_duration(self):
        if self.png_files:
            fps = self.fps_var.get()
            duration = len(self.png_files) / fps
            self.duration_label.config(text=f"📐 {duration:.1f} sek | {len(self.png_files)} kadr | {fps} FPS")

    def update_video_info(self):
        """Get video duration and frame count using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", self.video_path
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            info = json.loads(result.stdout)
            duration = float(info.get("format", {}).get("duration", 0))
            # Find video stream
            for s in info.get("streams", []):
                if s.get("codec_type") == "video":
                    fps_str = s.get("r_frame_rate", "30/1")
                    num, den = fps_str.split("/")
                    vid_fps = round(int(num) / int(den))
                    total_frames = int(duration * vid_fps)
                    self.duration_label.config(
                        text=f"📐 {duration:.1f} sek | ~{total_frames} kadr | {vid_fps} FPS (asl)"
                    )
                    break
        except:
            self.duration_label.config(text="📐 Video ma'lumotlari olinmadi")

    # ============ ACTIONS ============

    def start_action(self):
        if self.is_converting:
            return

        if self.mode == "png2webm":
            self.start_png2webm()
        elif self.mode == "video2png":
            self.start_video2png()
        elif self.mode == "video2webm":
            self.start_video2webm()

    def start_png2webm(self):
        if not self.png_files:
            return
        output = filedialog.asksaveasfilename(
            title="WebM faylni saqlash",
            defaultextension=".webm",
            filetypes=[("WebM video", "*.webm")],
            initialfile="animation.webm"
        )
        if not output:
            return
        self.output_path = output
        self.begin_conversion(target=self.run_png2webm)

    def start_video2png(self):
        if not self.video_path:
            return
        output = filedialog.asksaveasfilename(
            title="ZIP faylni saqlash",
            defaultextension=".zip",
            filetypes=[("ZIP fayl", "*.zip")],
            initialfile="frames.zip"
        )
        if not output:
            return
        self.output_path = output
        self.begin_conversion(target=self.run_video2png)

    def start_video2webm(self):
        if not self.video_path:
            return
        output = filedialog.asksaveasfilename(
            title="WebM faylni saqlash",
            defaultextension=".webm",
            filetypes=[("WebM video", "*.webm")],
            initialfile="output.webm"
        )
        if not output:
            return
        self.output_path = output
        self.begin_conversion(target=self.run_video2webm)

    def begin_conversion(self, target):
        self.is_converting = True
        self.btn_convert.config(state="disabled", text="⏳ Jarayonda...")
        self.progress_var.set(0)
        self.progress_label.config(text="Tayyorlanmoqda...")
        self.result_frame.pack_forget()
        threading.Thread(target=target, daemon=True).start()

    # ============ CONVERSION ENGINES ============

    def run_png2webm(self):
        """PNG sequence → WebM"""
        try:
            work_dir = tempfile.mkdtemp(prefix="conv_work_")
            total = len(self.png_files)

            for i, src in enumerate(self.png_files, start=1):
                dst = os.path.join(work_dir, f"{i:05d}.png")
                shutil.copy2(src, dst)
                self.root.after(0, self.update_progress, int(i / total * 30), f"Fayllar: {i}/{total}")

            quality_map = {"low": 40, "medium": 32, "high": 20}
            crf = quality_map.get(self.quality_var.get(), 32)
            fps = self.fps_var.get()

            res = self.resolution_var.get()
            if res != "original":
                vfilter = f"scale=-2:{int(res)}:flags=lanczos,format=yuva420p"
            else:
                vfilter = "format=yuva420p"

            cmd = [
                "ffmpeg", "-y", "-framerate", str(fps),
                "-i", os.path.join(work_dir, "%05d.png"),
                "-vf", vfilter,
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                "-auto-alt-ref", "0", "-crf", str(crf), "-b:v", "0",
                self.output_path
            ]

            self.run_ffmpeg_cmd(cmd, total, 30)
            shutil.rmtree(work_dir, ignore_errors=True)
            self.finish_with_size()

        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def run_video2png(self):
        """Video → PNG frames → ZIP"""
        try:
            work_dir = tempfile.mkdtemp(prefix="conv_frames_")
            fps = self.fps_var.get()

            # Resolution
            res = self.resolution_var.get()
            vf_parts = []
            if res != "original":
                vf_parts.append(f"scale=-2:{int(res)}:flags=lanczos")

            cmd = ["ffmpeg", "-y", "-i", self.video_path]
            if vf_parts:
                cmd += ["-vf", ",".join(vf_parts)]
            cmd += ["-r", str(fps), os.path.join(work_dir, "%05d.png")]

            self.root.after(0, self.update_progress, 10, "Kadrlar chiqarilmoqda...")

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, encoding='utf-8', errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            process.wait()

            if process.returncode != 0:
                err = process.stderr.read()
                self.root.after(0, self.show_error, err[:300])
                return

            # Count frames
            frames = sorted(Path(work_dir).glob("*.png"))
            total = len(frames)
            self.root.after(0, self.update_progress, 50, f"{total} ta kadr chiqarildi, ZIP yaratilmoqda...")

            # Create ZIP
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(frames):
                    zf.write(f, f.name)
                    if i % 10 == 0:
                        pct = 50 + int((i / total) * 45)
                        self.root.after(0, self.update_progress, pct, f"ZIP: {i}/{total}")

            shutil.rmtree(work_dir, ignore_errors=True)

            output_size = os.path.getsize(self.output_path)
            input_size = os.path.getsize(self.video_path)

            self.root.after(0, self.show_result_custom,
                f"✅ {total} ta PNG kadr → ZIP ({self.format_size(output_size)})")

        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def run_video2webm(self):
        """Video → WebM (VP9) with FPS control"""
        try:
            quality_map = {"low": 40, "medium": 32, "high": 20}
            crf = quality_map.get(self.quality_var.get(), 32)
            target_fps = self.fps_var.get()

            # Build video filter chain
            vf_parts = []

            # Resolution scaling
            res = self.resolution_var.get()
            if res != "original":
                vf_parts.append(f"scale=-2:{int(res)}:flags=lanczos")

            # FPS change: remap timestamps so all frames play at target_fps
            # setpts=N/FPS/TB assigns each frame a new timestamp
            vf_parts.append(f"setpts=N/{target_fps}/TB")

            cmd = [
                "ffmpeg", "-y", "-i", self.video_path,
                "-vf", ",".join(vf_parts),
                "-r", str(target_fps),
                "-c:v", "libvpx-vp9",
                "-crf", str(crf), "-b:v", "0",
                "-an",  # audio removed since speed changes
                self.output_path
            ]

            # Get approximate total frames for progress
            total_frames = self.get_video_frames()
            self.run_ffmpeg_cmd(cmd, total_frames, 5)
            self.finish_with_size()

        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    # ============ HELPERS ============

    def get_video_frames(self):
        """Get approximate frame count from video."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", self.video_path
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            info = json.loads(result.stdout)
            duration = float(info.get("format", {}).get("duration", 10))
            for s in info.get("streams", []):
                if s.get("codec_type") == "video":
                    fps_str = s.get("r_frame_rate", "30/1")
                    num, den = fps_str.split("/")
                    return int(duration * int(num) / int(den))
            return int(duration * 30)
        except:
            return 100

    def run_ffmpeg_cmd(self, cmd, total_frames, start_pct):
        """Run FFmpeg and track progress."""
        self.root.after(0, self.update_progress, start_pct, "FFmpeg ishlayapti...")

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, encoding='utf-8', errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        for line in process.stderr:
            line = line.strip()
            if "frame=" in line:
                try:
                    part = line.split("frame=")[1].split()[0]
                    frame_num = int(part)
                    pct = start_pct + int((frame_num / max(total_frames, 1)) * (95 - start_pct))
                    self.root.after(0, self.update_progress, min(pct, 95), f"Kodlash: {frame_num} kadr")
                except:
                    pass

        process.wait()
        if process.returncode != 0:
            err = process.stderr.read() if process.stderr else "Noma'lum xatolik"
            raise RuntimeError(err[:300])

    def finish_with_size(self):
        """Show result with file sizes."""
        output_size = os.path.getsize(self.output_path)
        if self.video_path:
            input_size = os.path.getsize(self.video_path)
        else:
            input_size = sum(os.path.getsize(f) for f in self.png_files)
        reduction = round(100 - (output_size / max(input_size, 1) * 100), 1)
        self.root.after(0, self.show_result, input_size, output_size, reduction)

    def update_progress(self, value, text):
        self.progress_var.set(value)
        self.progress_label.config(text=text)

    def show_result(self, input_size, output_size, reduction):
        self.progress_var.set(100)
        self.progress_label.config(text="✅ Tayyor!")
        self.is_converting = False
        self.btn_convert.config(state="normal", text="▶  Boshlash")
        self.result_label.config(
            text=f"📥 {self.format_size(input_size)}  →  📤 {self.format_size(output_size)}  |  📉 {reduction}%"
        )
        self.result_frame.pack(fill="x", pady=(4, 0))
        self.btn_open.pack(pady=(6, 0))

    def show_result_custom(self, text):
        self.progress_var.set(100)
        self.progress_label.config(text="✅ Tayyor!")
        self.is_converting = False
        self.btn_convert.config(state="normal", text="▶  Boshlash")
        self.result_label.config(text=text)
        self.result_frame.pack(fill="x", pady=(4, 0))
        self.btn_open.pack(pady=(6, 0))

    def show_error(self, error):
        self.progress_label.config(text="❌ Xatolik!")
        self.is_converting = False
        self.btn_convert.config(state="normal", text="▶  Boshlash")
        messagebox.showerror("Xatolik", f"Xatolik:\n{error}")

    def open_output_folder(self):
        if self.output_path:
            os.startfile(os.path.dirname(self.output_path))

    def cleanup_temp(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None

    @staticmethod
    def format_size(size):
        if size < 1024: return f"{size} B"
        if size < 1048576: return f"{size / 1024:.1f} KB"
        if size < 1073741824: return f"{size / 1048576:.1f} MB"
        return f"{size / 1073741824:.1f} GB"

    def on_close(self):
        self.cleanup_temp()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaConverterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
