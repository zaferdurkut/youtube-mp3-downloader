import argparse
import sys

import yt_dlp

from utils import create_directory, MyLogger, my_hook


parser = argparse.ArgumentParser(description="Youtube Mp3 Downloader")
parser.add_argument(
    "--output_folder",
    metavar="output_folder",
    default="downloaded_songs",
    type=str,
    help="Output folder in project",
)

parser.add_argument(
    "--url", metavar="url", required=True, type=str, help="Requested URL"
)

args = parser.parse_args()

if args.url is None:
    print("URL is required")
    sys.exit()


DIRECTORY_NAME = args.output_folder

create_directory(DIRECTORY_NAME)

ydl_opts = {
    "format": "bestaudio/best",
    "download_archive": "{DIRECTORY_NAME}/downloaded_songs.txt".format(
        DIRECTORY_NAME=DIRECTORY_NAME
    ),
    "outtmpl": "{DIRECTORY_NAME}/%(title)s.%(ext)s".format(
        DIRECTORY_NAME=DIRECTORY_NAME
    ),
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "quiet": False,
    "ignoreerrors": True,
    "logger": MyLogger(),
    "progress_hooks": [my_hook],
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # info = ydl.extract_info(
    #     args.url,
    #     download=False,
    # )
    try:
        ydl.download([args.url])
    except yt_dlp.utils.DownloadError as exc:
        print(exc)
