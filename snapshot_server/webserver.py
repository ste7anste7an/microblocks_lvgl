from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import datetime
from PIL import Image
import struct
import sys


display="st7789"

if display=="st7789":
    width = 280               # width of your framebuffer
    height = 240              # height of your framebuffer
else:
    width = 320               # width of your framebuffer
    height = 240              # height of your framebuffer

def convert_to_png(raw_data,png_filename):
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
    img.save(png_filename)
    print(f"✅ Saved PNG: {png_filename}")


    
class SimpleHTTPUploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No content")
            return

        # Read raw bytes
        raw_data = self.rfile.read(content_length)
        print(len(raw_data))
        # Save to current directory as "upload.bin"
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        png_filename = "lvgl_snapshot_"+date_time_str+".png"
        convert_to_png(raw_data,png_filename)
        print(f"✅ Received {len(raw_data)} bytes, saved as {png_filename}")

        # Send HTTP response
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"File uploaded successfully")

if __name__ == "__main__":
    server_address = ('', 8000)  # Listen on all interfaces, port 8000
    httpd = HTTPServer(server_address, SimpleHTTPUploadHandler)
    print("Server running on http://0.0.0.0:8000")
    httpd.serve_forever()
