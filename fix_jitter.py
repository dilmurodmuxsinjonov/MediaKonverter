import os
from pathlib import Path

def fix_jitter():
    # Directories
    processed_dir = Path(r"d:\rasimlar\processed")
    webp_dir = Path(r"d:\rasimlar\webp_anim")
    project_png = Path(r"c:\Users\Dilmurod\OneDrive\Desktop\test\loyiha\assets\png")
    project_webp = Path(r"c:\Users\Dilmurod\OneDrive\Desktop\test\loyiha\assets\webp")

    # The duplicate is at 00105.png / 00105.webp
    # We want to delete 105 and shift 106-208 down to 105-207
    
    target_dirs = [processed_dir, webp_dir, project_png, project_webp]
    
    for d in target_dirs:
        if not d.exists(): continue
        
        # 1. Delete 105
        f105 = d / "00105.png" if "png" in str(d).lower() or "processed" in str(d).lower() else d / "00105.webp"
        if f105.exists():
            f105.unlink()
            print(f"Deleted duplicate frame 105 in {d}")

        # 2. Shift 106-208 to 105-207
        ext = ".png" if "png" in str(d).lower() or "processed" in str(d).lower() else ".webp"
        for i in range(106, 209):
            old_file = d / f"{i:05d}{ext}"
            new_file = d / f"{i-1:05d}{ext}"
            if old_file.exists():
                if new_file.exists(): new_file.unlink()
                os.rename(old_file, new_file)
        
        print(f"Shifted frames in {d}")

if __name__ == "__main__":
    fix_jitter()
