import os
import time

from core import find_leftovers

LEFTOVERS = [
    "Song A.webm.part",
    "Song A.webm.ytdl",
    "Song B.f140.m4a",
    "Song B.f137.mp4.part",
    "Song B.f251-1.webm.part-Frag3",
    "Song C.temp.mp4",
    "Song D.jpg",  # cover left next to Song D.mp3
    "Song D.webm",  # source left next to Song D.mp3
    "Song E.webp",  # cover left next to Song E.mp4
]

KEEP = [
    "Song D.mp3",
    "Song E.mp4",
    "Song F.m4a",
    "Holiday.jpg",  # a photo with no matching song
    "Talk.webm",  # a video with no matching song
    "archive.zip.part",  # a browser download, not yt-dlp
    "notes.txt",
    ".youtube_downloaded_mp3.txt",
    ".DS_Store",
]


def make(folder, names, age):
    for name in names:
        path = folder / name
        path.write_bytes(b"x" * 10)
        old = time.time() - age
        os.utime(path, (old, old))


def test_finds_only_yt_dlp_leftovers(tmp_path):
    make(tmp_path, LEFTOVERS + KEEP, age=3600)
    assert [name for name, _ in find_leftovers(tmp_path)] == sorted(LEFTOVERS)


def test_skips_recently_modified_files(tmp_path):
    # Could still be in use by a running download
    make(tmp_path, ["Song D.mp3"], age=3600)
    make(tmp_path, ["Song A.webm.part", "Song D.jpg"], age=60)
    assert find_leftovers(tmp_path) == []


def test_reports_sizes(tmp_path):
    make(tmp_path, ["Song A.webm.part"], age=3600)
    assert find_leftovers(tmp_path) == [("Song A.webm.part", 10)]


def test_missing_folder(tmp_path):
    assert find_leftovers(tmp_path / "nope") == []
