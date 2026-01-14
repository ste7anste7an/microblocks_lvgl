from PIL import Image
import struct

# File parameters
raw_file = "lvgl_snapshot_2025-10-25_17-45-28.bin"   # The raw binary uploaded
png_file = "snapshot.png"
width = 280               # width of your framebuffer
height = 240              # height of your framebuffer

# Read raw data
with open(raw_file, "rb") as f:
    raw_data = f.read()

# Convert RGB565 to RGB888
pixels = []
for i in range(0, len(raw_data), 2):
    if i+1 >= len(raw_data):
        break
    # Unpack 16-bit value
    val = raw_data[i] | (raw_data[i+1] << 8)
    r = ((val >> 11) & 0x1F) << 3
    g = ((val >> 5) & 0x3F) << 2
    b = (val & 0x1F) << 3
    pixels.append((r, g, b))

# Create image
img = Image.new("RGB", (width, height))
img.putdata(pixels)
img.save(png_file)
print(f"✅ Saved PNG: {png_file}")
