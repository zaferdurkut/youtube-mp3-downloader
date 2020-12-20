from moviepy.editor import *

from utils import find_paths

MP4_BASE_PATH = "downloaded"
MP4_BASE_SUFFIX = ".mp4"

def convert_mp4_to_mp3(mp4_path: str, mp3_path: str) -> bool:
    try:
        videoClip = VideoFileClip(mp4_path)
        audioClip = videoClip.audio
        audioClip.write_audiofile(mp3_path)
        audioClip.close()
        videoClip.close()
    except Exception as exc:
        print(exc)
    finally:
        return True


files = find_paths(directory=MP4_BASE_PATH, stipe=MP4_BASE_SUFFIX)

for file in files:
    mp3_path = "mp3/" + file[:-1] + "3"
    result = convert_mp4_to_mp3(mp3_path=mp3_path, mp4_path=file)
    print(result)


