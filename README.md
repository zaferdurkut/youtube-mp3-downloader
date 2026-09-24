# Youtube Downloader
Download a single YouTube video or a whole playlist as mp3, m4a or mp4, from a small local web UI or the command line. Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

- Songs get their cover art and artist / title tags embedded.
- File names are cleaned up: `Cengiz Özkan - Değme Felek I Official Music Video © 2015 Kalan Müzik` becomes `Cengiz Özkan - Değme Felek.mp3`.
- Already downloaded videos are skipped on the next run (tracked per format).
- Files are saved to `~/Downloads` by default.

## Requirements
Python 3.10+ and ffmpeg. On Mac OS (for other operating systems, see the ffmpeg docs):

```
brew install ffmpeg
```

## Usage
The Makefile creates the virtualenv and installs the dependencies on first use, so there's no setup step.

### Web UI
```
make ui
```
Opens http://127.0.0.1:8000. Pick single video or playlist and a format, paste the link and download. The library at the bottom lists the files in the output folder: click a song to play it, or a video to watch it. The output folder can be changed from the UI and is remembered in `settings.json`.

**Temizle** deletes what interrupted downloads leave behind (`.part` / `.ytdl` files, per-format parts like `Song.f140.m4a`, and covers or source audio next to a finished song). It only matches names yt-dlp produces, skips files changed in the last 10 minutes, and lists the files for confirmation first, so it is safe to use on `~/Downloads`.

Only one download runs at a time; reloading the page or opening a second tab reconnects to the running download. **Durdur** stops it and removes the half-downloaded files of the song in progress; songs that already finished are kept.

### Command line
```
make download URL="https://www.youtube.com/playlist?list=PLAYLIST_ID"
```
Options:

| Option | Meaning |
| --- | --- |
| `FORMAT=mp3\|m4a\|mp4` | Output format (default `mp3`) |
| `LIMIT=10` | Only the first N items of a playlist |
| `SINGLE=1` | Only the video, even if the link also has `list=` |
| `OUT=~/Music/YouTube` | Output folder (default `~/Downloads`) |

Or call the script directly: `python downloader.py --help`.

### Other commands
```
make test      # run the tests
make update    # update yt-dlp, try this first when downloads start failing
make clean     # remove the virtualenv
```
