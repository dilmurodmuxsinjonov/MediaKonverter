import shutil
from pathlib import Path

def extend_animation():
    processed_dir = Path(r"d:\rasimlar\processed")
    
    # Original range: 00024 to 00127
    start_orig = 24
    end_orig = 127
    
    # New sequence starts at 128
    current_new_index = 128
    
    # Iterate from 127 down to 24
    for i in range(end_orig, start_orig - 1, -1):
        orig_filename = f"{i:05d}.png"
        new_filename = f"{current_new_index:05d}.png"
        
        orig_path = processed_dir / orig_filename
        new_path = processed_dir / new_filename
        
        if orig_path.exists():
            shutil.copy2(orig_path, new_path)
            print(f"Copied {orig_filename} to {new_filename}")
            current_new_index += 1
        else:
            print(f"Warning: {orig_filename} not found.")

if __name__ == "__main__":
    extend_animation()
