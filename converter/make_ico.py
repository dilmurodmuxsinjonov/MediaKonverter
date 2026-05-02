"""Convert PNG image to ICO format for desktop shortcut."""
from PIL import Image
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

img = Image.open(input_path).convert("RGBA")

# Create multiple sizes for ICO
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = []
for size in sizes:
    resized = img.resize(size, Image.LANCZOS)
    icons.append(resized)

icons[0].save(output_path, format="ICO", sizes=[(s, s) for s, _ in sizes], append_images=icons[1:])
print(f"ICO saved: {output_path}")
