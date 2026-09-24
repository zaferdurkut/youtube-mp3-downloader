# Youtube Downloader
Youtube single or multiple (playlist) song downloader with mp3 output type, built on [yt-dlp](https://github.com/yt-dlp/yt-dlp).

`youtube_dl` is no longer maintained and can't extract videos from YouTube anymore, so this project uses `yt-dlp` (an actively maintained fork with the same API).

## Installation
ffmpeg is required for the mp3 conversion. On Mac OS (for other operating systems, see the ffmpeg docs):

```
brew install ffmpeg
```

Create and activate a virtualenv
```
python3 -m venv venv
source venv/bin/activate
```
Install the dependencies
```
pip install -r requirements.txt
```
YouTube changes often; if downloads start failing, update yt-dlp first:
```
pip install -U "yt-dlp[default]"
```
## Usage
Quote the URL so the shell doesn't interpret `&`:
```
python downloader.py --output_folder downloaded_songs --url "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```
Already downloaded songs are recorded in `<output_folder>/downloaded_songs.txt` and skipped on the next run.
