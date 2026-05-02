from PIL import Image
import os
from pathlib import Path

def convert_to_webp():
    input_dir = Path(r"d:\rasimlar\processed")
    output_dir = Path(r"d:\rasimlar\webp_anim")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    images = sorted(list(input_dir.glob("*.png")))
    print(f"Found {len(images)} images to convert to WebP.")

    total_old_size = 0
    total_new_size = 0

    for img_path in images:
        try:
            # Open PNG
            with Image.open(img_path) as img:
                # New filename
                new_filename = img_path.stem + ".webp"
                output_path = output_dir / new_filename
                
                if output_path.exists():
                    print(f"Skipping {new_filename} (already exists)")
                    continue
                
                # Save as WebP with transparency and optimized quality
                # method=4 is faster than 6 while still providing good compression
                img.save(output_path, "WEBP", quality=80, method=4)
                
                old_size = img_path.stat().st_size
                new_size = output_path.stat().st_size
                
                total_old_size += old_size
                total_new_size += new_size
                
                print(f"Converted {img_path.name} ({old_size/1024:.1f}KB) -> {new_filename} ({new_size/1024:.1f}KB)")
        except Exception as e:
            print(f"Error converting {img_path.name}: {e}")

    print("\n" + "="*30)
    print(f"Total original size: {total_old_size / (1024*1024):.2f} MB")
    print(f"Total WebP size: {total_new_size / (1024*1024):.2f} MB")
    print(f"Reduction: {100 - (total_new_size/total_old_size * 100):.1f}%")
    print("="*30)

if __name__ == "__main__":
    convert_to_webp()
