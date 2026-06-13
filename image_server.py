"""
The Fractured Orbit — Scene Image Panel Server
Serves a browser panel that auto-refreshes with the latest DALL-E generated image.
Run alongside main.py: python image_server.py
Then open http://localhost:8081 in a browser beside the terminal.
"""
from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import uvicorn

GENERATED_DIR = Path(__file__).parent / "generated"
LATEST_PATH = GENERATED_DIR / "latest.png"
PLACEHOLDER_PATH = Path(__file__).parent / "assets" / "placeholder.png"

app = FastAPI()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>The Fractured Orbit — Scene Panel</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #000;
      color: #ccc;
      font-family: 'Courier New', monospace;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
    }
    header {
      width: 100%;
      padding: 10px 20px;
      background: #0a0a0a;
      border-bottom: 1px solid #1a3a3a;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: #00ffcc; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }
    header span { color: #00ffcc; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; }
    .subtitle { color: #444; font-size: 11px; margin-left: auto; }
    #scene-wrap {
      flex: 1;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      position: relative;
    }
    #scene-img {
      max-width: 100%;
      max-height: calc(100vh - 80px);
      border: 1px solid #1a3a3a;
      border-radius: 4px;
      transition: opacity 0.4s ease;
      display: block;
    }
    #scene-img.fading { opacity: 0; }
    #loading {
      position: absolute;
      color: #00ffcc44;
      font-size: 12px;
      letter-spacing: 3px;
      display: none;
    }
    footer {
      width: 100%;
      padding: 6px 20px;
      background: #0a0a0a;
      border-top: 1px solid #1a3a3a;
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: #333;
    }
  </style>
</head>
<body>
  <header>
    <div class="dot"></div>
    <span>The Fractured Orbit &mdash; Scene Panel</span>
    <span class="subtitle" id="ts">—</span>
  </header>
  <div id="scene-wrap">
    <span id="loading">GENERATING SCENE...</span>
    <img id="scene-img" src="/image?t=0" alt="Scene"/>
  </div>
  <footer>
    <span>ISS TARTARUS &middot; KEPLER-452</span>
    <span id="status">LIVE</span>
  </footer>

  <script>
    let lastMod = 0;

    async function checkForNewImage() {
      try {
        const res = await fetch('/image-meta');
        const data = await res.json();
        if (data.modified > lastMod && data.modified > 0) {
          lastMod = data.modified;
          const img = document.getElementById('scene-img');
          const loading = document.getElementById('loading');
          img.classList.add('fading');
          loading.style.display = 'block';
          await new Promise(r => setTimeout(r, 400));
          img.src = '/image?t=' + Date.now();
          img.onload = () => {
            img.classList.remove('fading');
            loading.style.display = 'none';
            document.getElementById('ts').textContent = new Date().toLocaleTimeString();
          };
        }
      } catch(e) {}
    }

    // Poll every 2 seconds
    setInterval(checkForNewImage, 2000);
    checkForNewImage();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_PAGE)


@app.get("/image")
async def get_image():
    if LATEST_PATH.exists():
        return FileResponse(str(LATEST_PATH), media_type="image/png")
    # Return a tiny black pixel as placeholder
    import base64
    black_pixel = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return Response(content=black_pixel, media_type="image/png")


@app.get("/image-meta")
async def image_meta():
    if LATEST_PATH.exists():
        return {"modified": LATEST_PATH.stat().st_mtime, "exists": True}
    return {"modified": 0, "exists": False}


if __name__ == "__main__":
    GENERATED_DIR.mkdir(exist_ok=True)
    print("  Scene Panel: http://localhost:8081")
    print("  Open this in a browser beside your terminal.")
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="warning")
