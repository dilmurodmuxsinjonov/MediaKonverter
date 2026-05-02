import os
from pathlib import Path

def reindex_images():
    processed_dir = Path(r"d:\rasimlar\processed")
    
    # Get all PNG files and sort them by name
    images = sorted(list(processed_dir.glob("*.png")))
    
    print(f"Found {len(images)} images to re-index.")
    
    for idx, img_path in enumerate(images, start=1):
        new_filename = f"{idx:05d}.png"
        new_path = processed_dir / new_filename
        
        # Use os.rename
        try:
            os.rename(img_path, new_path)
            print(f"Renamed {img_path.name} to {new_filename}")
        except Exception as e:
            print(f"Error renaming {img_path.name}: {e}")

if __name__ == "__main__":
    reindex_images()
