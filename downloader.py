import argparse
import sys

import youtube_dl

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
    "logger": MyLogger(),
    "progress_hooks": [my_hook],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # info = ydl.extract_info(
    #     args.url,
    #     download=False,
    # )
    ydl.download([args.url])
