import cv2
import numpy as np
import os
from pathlib import Path

def process_image(input_path, output_path):
    # Load image
    img = cv2.imread(str(input_path))
    if img is None:
        print(f"Failed to load {input_path}")
        return

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define range for green color
    # Typical green screen range
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    # Create mask
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert mask to get the clouds
    mask_inv = cv2.bitwise_not(mask)

    # Remove watermark (bottom right corner)
    # Based on the preview, the watermark "veo3ai.io" is roughly at the bottom right
    h, w = img.shape[:2]
    # Mask out a rectangle for the watermark
    # Approximate coordinates: bottom 10% and right 20%
    watermark_h = int(h * 0.92)
    watermark_w = int(w * 0.85)
    mask_inv[watermark_h:, watermark_w:] = 0

    # Smooth the mask to get anti-aliased edges
    mask_inv = cv2.GaussianBlur(mask_inv, (3, 3), 0)

    # Create 4-channel image (BGRA)
    b, g, r = cv2.split(img)
    bgra = cv2.merge([b, g, r, mask_inv])

    # Save output
    cv2.imwrite(str(output_path), bgra)
    print(f"Processed: {output_path.name}")

def main():
    input_dir = Path(r"d:\rasimlar")
    output_dir = input_dir / "processed"
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    images = list(input_dir.glob("*.png"))
    print(f"Found {len(images)} images to process.")

    for img_path in images:
        output_path = output_dir / img_path.name
        process_image(img_path, output_path)

if __name__ == "__main__":
    main()
