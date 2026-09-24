"""Download logic shared by the CLI (downloader.py) and the web UI (app.py)."""
import os
import re
from dataclasses import dataclass, field

import yt_dlp
from yt_dlp.postprocessor import PostProcessor
from yt_dlp.utils import DownloadCancelled

from titles import clean_title

DEFAULT_OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")

# Each format keeps its own archive, so a song saved as mp3 can still be fetched as mp4.
# Archives are hidden files so they don't clutter a shared folder like ~/Downloads.
FORMATS = {
    "mp3": {
        "archive": ".youtube_downloaded_mp3.txt",
        "opts": {"format": "bestaudio/best"},
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
        ],
    },
    "m4a": {
        "archive": ".youtube_downloaded_m4a.txt",
        "opts": {"format": "bestaudio[ext=m4a]/bestaudio/best"},
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
    },
    "mp4": {
        "archive": ".youtube_downloaded_mp4.txt",
        "opts": {
            # Prefer H.264: AV1/VP9 won't play in QuickTime or on older devices
            "format": "bv*[vcodec^=avc1]+ba[ext=m4a]/bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
            "merge_output_format": "mp4",
        },
        "postprocessors": [],
    },
}
# yt-dlp colors its messages when started from a terminal
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
ARCHIVE_SKIP_RE = re.compile(
    r"\[download\] (?:[\w-]+: )?(.*) has already been recorded in the archive"
)


@dataclass
class DownloadResult:
    downloaded: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    failed: list = field(default_factory=list)
    cancelled: bool = False


class CleanTitlePP(PostProcessor):
    """Rewrite the title to "Artist - Song" before the filename and tags are built."""

    def run(self, info):
        artist, song = clean_title(info.get("title") or "")
        if artist:
            info["artist"] = artist
            info["track"] = song
            info["title"] = f"{artist} - {song}"
        else:
            info["title"] = song
        return [], info


class _Logger:
    def __init__(self, result, emit):
        self.result = result
        self.emit = emit

    def debug(self, msg):
        match = ARCHIVE_SKIP_RE.search(ANSI_RE.sub("", msg))
        if match:
            # The archive check runs before CleanTitlePP, so clean the title here too
            artist, song = clean_title(match.group(1))
            title = f"{artist} - {song}" if artist else song
            self.result.skipped.append(title)
            self.emit({"type": "skipped", "title": title})

    def warning(self, msg):
        pass

    def error(self, msg):
        msg = ANSI_RE.sub("", msg).removeprefix("ERROR: ")
        self.result.failed.append(msg)
        self.emit({"type": "error", "message": msg})


def _position(info, limit):
    index = info.get("playlist_index")
    total = info.get("n_entries") or info.get("playlist_count")
    if total and limit:
        total = min(total, limit)
    return index, total


def download(url, output_folder=DEFAULT_OUTPUT_FOLDER, limit=None, fmt="mp3", single=False,
             on_event=None, cancel=None):
    """Download url (a video or playlist) as fmt files (see FORMATS) with cover art and tags.

    single downloads only the video even when the URL also points at a playlist.
    cancel is an optional threading.Event: setting it stops after the current step and
    removes the unfinished files of the item in progress.
    on_event is called with dicts describing progress: progress, converting,
    done, skipped, error and a final finished event.
    """
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format {fmt!r}, choose one of {', '.join(FORMATS)}")
    config = FORMATS[fmt]
    emit = on_event or (lambda event: None)
    result = DownloadResult()
    os.makedirs(output_folder, exist_ok=True)
    # Files of the item in progress, removed if the download is stopped half way
    unfinished = set()

    def check_cancel(*_, **__):
        if cancel is not None and cancel.is_set():
            raise DownloadCancelled("Download stopped")

    def track(info, *paths):
        unfinished.update(path for path in paths if path)
        unfinished.update(t["filepath"] for t in info.get("thumbnails") or [] if t.get("filepath"))

    def progress_hook(d):
        check_cancel()
        info = d.get("info_dict", {})
        track(info, d.get("filename"), d.get("tmpfilename"))
        index, total = _position(info, limit)
        if d["status"] == "downloading":
            size = d.get("total_bytes") or d.get("total_bytes_estimate")
            percent = round(d.get("downloaded_bytes", 0) * 100 / size, 1) if size else None
            emit({"type": "progress", "title": info.get("title"), "index": index,
                  "total": total, "percent": percent})

    def postprocessor_hook(d):
        check_cancel()
        track(d["info_dict"], d["info_dict"].get("filepath"))
        if d["status"] == "started" and d["postprocessor"] in ("ExtractAudio", "Merger"):
            emit({"type": "converting", "title": d["info_dict"].get("title")})

    def post_hook(filepath):
        unfinished.clear()
        result.downloaded.append(filepath)
        emit({"type": "done", "title": os.path.splitext(os.path.basename(filepath))[0],
              "path": filepath})

    ydl_opts = {
        **config["opts"],
        "download_archive": os.path.join(output_folder, config["archive"]),
        "outtmpl": {
            "default": os.path.join(output_folder, "%(title)s.%(ext)s"),
            # An empty template stops yt-dlp from saving the playlist's own cover image
            "pl_thumbnail": "",
        },
        "writethumbnail": True,
        "postprocessors": [
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            *config["postprocessors"],
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
        ],
        "noplaylist": single,
        # Runs before each video, so a stop request is noticed between items too
        "match_filter": check_cancel,
        "color": "no_color",
        "ignoreerrors": True,
        "noprogress": True,
        "logger": _Logger(result, emit),
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "post_hooks": [post_hook],
    }
    if limit:
        ydl_opts["playlistend"] = limit

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(CleanTitlePP(), when="pre_process")
            ydl.download([url])
    except (DownloadCancelled, KeyboardInterrupt):
        result.cancelled = True
        for path in unfinished - set(result.downloaded):
            for leftover in (path, path + ".ytdl"):
                if os.path.isfile(leftover):
                    os.remove(leftover)

    emit({"type": "finished", "downloaded": len(result.downloaded),
          "skipped": len(result.skipped), "failed": result.failed,
          "cancelled": result.cancelled})
    return result
