from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import io
import time
from PIL import Image
import struct

# ---- Configure your display resolution ----
DISPLAY = "st7789"

if DISPLAY == "st7789":
    WIDTH = 280
    HEIGHT = 240
else:
    WIDTH = 320
    HEIGHT = 240

EXPECTED_BYTES = WIDTH * HEIGHT * 2  # RGB565

# ---- Global latest frame storage + notify mechanism ----
_latest_png = None          # bytes
_latest_frame_id = 0        # increment on each upload
_lock = threading.Lock()
_cond = threading.Condition(_lock)


def rgb565_to_png_bytes(raw_data: bytes, width: int, height: int) -> bytes:
    """
    Convert little-endian RGB565 framebuffer to PNG (RGB888) bytes.
    raw_data must be width*height*2 bytes.
    """
    if len(raw_data) < width * height * 2:
        raise ValueError(f"Not enough data: got {len(raw_data)} bytes, expected {width*height*2}")

    # Convert to RGB888
    # Build an RGB bytearray: 3 bytes per pixel
    rgb = bytearray(width * height * 3)

    # Iterate 16-bit little-endian pixels
    # struct.iter_unpack is reasonably fast and avoids manual index math on raw bytes
    i = 0
    for (val,) in struct.iter_unpack("<H", raw_data[:width * height * 2]):
        r = ((val >> 11) & 0x1F) << 3
        g = ((val >> 5) & 0x3F) << 2
        b = (val & 0x1F) << 3

        rgb[i] = r
        rgb[i + 1] = g
        rgb[i + 2] = b
        i += 3

    img = Image.frombytes("RGB", (width, height), bytes(rgb))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


INDEX_HTML = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>LVGL Live View</title>
  <style>
    body {{ font-family: sans-serif; margin: 16px; }}
    .row {{ display: flex; gap: 16px; align-items: flex-start; }}
    #img {{ border: 1px solid #ccc; image-rendering: pixelated; }}
    .meta {{ color: #444; }}
    .ok {{ color: #0a0; }}
    .bad {{ color: #a00; }}
  </style>
</head>
<body>
  <h2>LVGL Live View ({WIDTH}×{HEIGHT})</h2>

  <div class="row">
    <div>
      <img id="img" width="{WIDTH}" height="{HEIGHT}" alt="waiting for frames..." />
    </div>
    <div class="meta">
      <div>Status: <span id="status" class="bad">disconnected</span></div>
      <div>Last frame id: <span id="fid">-</span></div>
      <div>Last update: <span id="ts">-</span></div>
      <div style="margin-top:12px;">
        Tip: keep this tab open, then POST frames to <code>/upload</code>
      </div>
    </div>
  </div>

<script>
(function() {{
  const img = document.getElementById('img');
  const status = document.getElementById('status');
  const fid = document.getElementById('fid');
  const ts = document.getElementById('ts');

  function setStatus(ok, text) {{
    status.textContent = text;
    status.className = ok ? 'ok' : 'bad';
  }}

  // SSE: server pushes "frame id" whenever a new upload arrives
  const es = new EventSource('/events');

  es.onopen = () => setStatus(true, 'connected');

  es.onerror = () => {{
    setStatus(false, 'disconnected (retrying...)');
  }};

  es.addEventListener('frame', (ev) => {{
    const id = ev.data || '0';
    fid.textContent = id;
    ts.textContent = new Date().toLocaleTimeString();

    // Cache-bust with frame id so browser always fetches new PNG
    img.src = '/latest.png?frame=' + encodeURIComponent(id);
  }});

  // If page loads after frames exist, try to load once anyway
  img.src = '/latest.png?frame=init_' + Date.now();
}})();
</script>
</body>
</html>
"""


class LiveViewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith("/latest.png"):
            with _lock:
                png = _latest_png

            if not png:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"No frame yet")
                return

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Length", str(len(png)))
            self.end_headers()
            self.wfile.write(png)
            return

        if self.path.startswith("/events"):
            # Server-Sent Events: keep connection open and notify on new frames
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            # Send a comment to establish the stream
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()

            # Track last seen frame id per client
            with _cond:
                last = _latest_frame_id

            try:
                while True:
                    with _cond:
                        _cond.wait(timeout=15.0)  # keepalive interval
                        current = _latest_frame_id

                    # keepalive ping
                    self.wfile.write(b": ping\n\n")

                    if current != last:
                        last = current
                        msg = f"event: frame\ndata: {current}\n\n".encode("utf-8")
                        self.wfile.write(msg)

                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return

        # Not found
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not found")

    def do_POST(self):
        # Receive raw RGB565 frame on /upload
        if self.path != "/upload":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"POST to /upload")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No content")
            return

        raw_data = self.rfile.read(content_length)

        # Optional sanity check; you can relax this if you sometimes send different sizes
        if len(raw_data) != EXPECTED_BYTES:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(
                f"Bad size: got {len(raw_data)} bytes, expected {EXPECTED_BYTES}\n".encode("utf-8")
            )
            return

        try:
            png = rgb565_to_png_bytes(raw_data, WIDTH, HEIGHT)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Convert failed: {e}\n".encode("utf-8"))
            return

        with _cond:
            global _latest_png, _latest_frame_id
            _latest_png = png
            _latest_frame_id += 1
            _cond.notify_all()

        # Respond OK
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")


if __name__ == "__main__":
    addr = ("", 8000)
    httpd = ThreadingHTTPServer(addr, LiveViewHandler)
    print("Server running:")
    print("  Viewer:  http://0.0.0.0:8000/")
    print("  Upload:  POST http://0.0.0.0:8000/upload")
    httpd.serve_forever()
