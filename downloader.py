import argparse
import sys

from core import DEFAULT_OUTPUT_FOLDER, FORMATS, download

parser = argparse.ArgumentParser(description="Youtube Mp3 Downloader")
parser.add_argument(
    "--output_folder",
    metavar="output_folder",
    default=DEFAULT_OUTPUT_FOLDER,
    type=str,
    help=f"Output folder (default: {DEFAULT_OUTPUT_FOLDER})",
)

parser.add_argument(
    "--url", metavar="url", required=True, type=str, help="Requested URL"
)

parser.add_argument(
    "--limit",
    metavar="limit",
    type=int,
    default=None,
    help="Download only the first N songs of a playlist",
)

parser.add_argument(
    "--format",
    choices=list(FORMATS),
    default="mp3",
    help="Output format: mp3/m4a (audio) or mp4 (video)",
)

parser.add_argument(
    "--single",
    action="store_true",
    help="Download only the video even if the URL also has a playlist",
)


def print_event(event):
    kind = event["type"]
    if kind == "progress" and event["percent"] is not None:
        position = f"[{event['index']}/{event['total']}] " if event["index"] else ""
        print(f"\r{position}{event['title']} %{event['percent']:.0f}", end="", flush=True)
    elif kind == "converting":
        print(f"\r{event['title']} converting ...", end="", flush=True)
    elif kind == "done":
        print(f"\r\033[K✓ {event['title']}")
    elif kind == "skipped":
        print(f"↷ {event['title']} (already downloaded)")
    elif kind == "error":
        print(f"\r\033[K✕ {event['message']}")


def main():
    args = parser.parse_args()
    result = download(
        args.url, args.output_folder, args.limit, args.format, args.single, on_event=print_event
    )

    print(
        f"\nDownloaded: {len(result.downloaded)}, "
        f"already downloaded: {len(result.skipped)}, failed: {len(result.failed)}"
    )
    for message in result.failed:
        print(f"  ✕ {message}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())
