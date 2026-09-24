"""Turn noisy YouTube video titles into clean "Artist - Song" names."""
import re

# Words that mark a bracket group or title tail as noise rather than part of the song name
NOISE = r"\b(?:official|video|audio|lyrics?|klip|clip|hd|4k|müzik|music|records)\b|©|\(c\)"
NOISE_RE = re.compile(NOISE, re.IGNORECASE)

BRACKETS_RE = re.compile(r"\s*[\[(【]([^\])】]*)[\])】]")
# Everything from a copyright sign or an "Official ..." marker to the end
TAIL_RE = re.compile(
    r"\s*(?:©|\(c\)\s|official\b|video\s*klip|music\s*video|lyric\s*video).*$",
    re.IGNORECASE,
)
PIPE_RE = re.compile(r"\s*[|｜]\s*")
# " I " is often used as a pipe ("Song I Official Video"), but "I" is also a word,
# so only cut there when what follows is noise
LETTER_I_SEP_RE = re.compile(r"\s+I\s+(.*)$")
LIVE_SUFFIX_RE = re.compile(r"\s*[-–—]\s*(canlı|live)\s*$", re.IGNORECASE)
SPACED_DASH_RE = re.compile(r"\s+[-–—]\s+")
DASH_RE = re.compile(r"\s*[-–—]\s*")


def _clean(text):
    return re.sub(r"\s+", " ", text).strip(" -–—|｜")


def clean_title(title):
    """Return (artist, song). artist is None when the title has no "Artist - Song" form."""
    # After "Artist - Song" a pipe usually starts a channel/show name; otherwise it
    # separates artist and song ("Ahmet Kaya | Kum Gibi")
    head, *rest = PIPE_RE.split(title, maxsplit=1)
    text = head if rest and DASH_RE.search(head) else " - ".join([head, *rest])

    match = LETTER_I_SEP_RE.search(text)
    if match and NOISE_RE.search(match.group(1)):
        text = text[: match.start()]

    text = BRACKETS_RE.sub(
        lambda m: "" if NOISE_RE.search(m.group(1)) or not m.group(1).strip() else m.group(0),
        text,
    )
    text = TAIL_RE.sub("", text)
    text = LIVE_SUFFIX_RE.sub(lambda m: f" ({m.group(1)})", text)

    # Prefer a spaced dash so names like "Jay-Z - Song" keep their hyphen
    parts = SPACED_DASH_RE.split(text, maxsplit=1)
    if len(parts) == 1:
        parts = DASH_RE.split(text, maxsplit=1)

    if len(parts) == 2 and _clean(parts[0]) and _clean(parts[1]):
        return _clean(parts[0]), _clean(parts[1])
    return None, _clean(text) or title.strip()
