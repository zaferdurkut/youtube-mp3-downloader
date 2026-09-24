"""Small local web UI for the downloader: python app.py, then open http://127.0.0.1:8000"""
import asyncio
import json
import os
import subprocess
import sys
import threading
import uuid
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from core import DEFAULT_OUTPUT_FOLDER, download

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".opus", ".ogg", ".wav", ".flac"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov"}

INDEX_HTML = Path(__file__).parent / "static" / "index.html"
# The folder picked in the UI survives restarts; OUTPUT_FOLDER only sets the default
SETTINGS_FILE = Path(os.environ.get("SETTINGS_FILE", Path(__file__).parent / "settings.json"))
DEFAULT_FOLDER = os.environ.get("OUTPUT_FOLDER", DEFAULT_OUTPUT_FOLDER)


def output_folder():
    try:
        return json.loads(SETTINGS_FILE.read_text())["output_folder"]
    except (OSError, ValueError, KeyError):
        return DEFAULT_FOLDER

app = FastAPI()
jobs = {}
# One download at a time: parallel jobs would race on the same archive file
busy = threading.Lock()
current_job = None


@app.middleware("http")
async def same_origin_only(request: Request, call_next):
    """Stop other websites open in the browser from starting downloads or opening Finder."""
    origin = request.headers.get("origin")
    if request.method != "GET" and origin and urlparse(origin).netloc != request.headers.get("host"):
        return JSONResponse({"detail": "Forbidden"}, status_code=403)
    return await call_next(request)


class Job:
    def __init__(self, request):
        self.id = uuid.uuid4().hex
        self.request = request
        self.events = []
        self.finished = False
        self.cancel = threading.Event()

    def emit(self, event):
        self.events.append(event)
        if event["type"] == "finished":
            self.finished = True


class DownloadRequest(BaseModel):
    url: str = Field(min_length=1)
    limit: int | None = Field(default=None, ge=1)
    format: Literal["mp3", "m4a", "mp4"] = "mp3"
    single: bool = False


def run_job(job, request):
    global current_job
    try:
        download(request.url, output_folder(), request.limit, request.format, request.single,
                 on_event=job.emit, cancel=job.cancel)
    except Exception as exc:  # keep the UI informed instead of hanging forever
        job.emit({"type": "error", "message": str(exc)})
        job.emit({"type": "finished", "downloaded": 0, "skipped": 0, "failed": [str(exc)]})
    finally:
        current_job = None
        busy.release()


@app.get("/")
def index():
    return FileResponse(INDEX_HTML)


class ConfigRequest(BaseModel):
    output_folder: str = Field(min_length=1)


@app.get("/api/config")
def config():
    return {"output_folder": output_folder(), "default_folder": DEFAULT_FOLDER}


@app.put("/api/config")
def update_config(request: ConfigRequest):
    folder = os.path.abspath(os.path.expanduser(request.output_folder.strip()))
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError as exc:
        raise HTTPException(400, f"Klasör oluşturulamadı: {exc.strerror}")
    SETTINGS_FILE.write_text(json.dumps({"output_folder": folder}, ensure_ascii=False))
    return {"output_folder": folder, "default_folder": DEFAULT_FOLDER}


@app.get("/api/downloads/current")
def running_download():
    """Lets a reloaded page or a second tab reattach to the running download."""
    if current_job is None:
        return {"id": None}
    return {"id": current_job.id, **current_job.request.model_dump()}


@app.post("/api/downloads")
def start_download(request: DownloadRequest):
    global current_job
    if not busy.acquire(blocking=False):
        raise HTTPException(409, "Zaten bir indirme sürüyor, bitmesini bekle")
    job = Job(request)
    jobs[job.id] = job
    current_job = job
    threading.Thread(target=run_job, args=(job, request), daemon=True).start()
    return {"id": job.id}


@app.post("/api/downloads/{job_id}/cancel")
def cancel_download(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Böyle bir indirme yok")
    job.cancel.set()
    return {"ok": True}


@app.post("/api/open-folder")
def open_folder():
    folder = output_folder()
    os.makedirs(folder, exist_ok=True)
    if sys.platform == "darwin":
        subprocess.Popen(["open", folder])
    elif sys.platform == "win32":
        os.startfile(folder)
    else:
        subprocess.Popen(["xdg-open", folder])
    return {"ok": True}


@app.get("/api/files")
def list_files():
    """Audio and video files in the output folder, newest first."""
    folder = Path(output_folder())
    if not folder.is_dir():
        return []
    files = []
    for path in folder.iterdir():
        ext = path.suffix.lower()
        if not path.is_file() or ext not in AUDIO_EXTENSIONS | VIDEO_EXTENSIONS:
            continue
        stat = path.stat()
        files.append({
            "name": path.name,
            "kind": "audio" if ext in AUDIO_EXTENSIONS else "video",
            "size": stat.st_size,
            "modified": stat.st_mtime,
        })
    return sorted(files, key=lambda f: f["modified"], reverse=True)


@app.get("/media/{name}")
def media(name: str):
    folder = Path(output_folder()).resolve()
    path = (folder / name).resolve()
    # Only serve files directly inside the output folder
    if path.parent != folder or not path.is_file():
        raise HTTPException(404, "Dosya bulunamadı")
    return FileResponse(path)


@app.get("/api/downloads/{job_id}/events")
async def job_events(job_id: str, last_event_id: int | None = Header(default=None)):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(404, "Böyle bir indirme yok")

    async def stream():
        # On reconnect the browser sends Last-Event-ID, so resume instead of replaying
        sent = last_event_id + 1 if last_event_id is not None else 0
        while True:
            while sent < len(job.events):
                data = json.dumps(job.events[sent], ensure_ascii=False)
                yield f"id: {sent}\ndata: {data}\n\n"
                sent += 1
            if job.finished and sent == len(job.events):
                return
            await asyncio.sleep(0.25)

    return StreamingResponse(stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
