import pytest

from core import DownloadResult, _Logger

GREEN, BLUE, RED, RESET = "\x1b[0;32m", "\x1b[0;94m", "\x1b[0;31m", "\x1b[0m"


def archive_message(video_id, title):
    # What yt-dlp logs when started from a terminal, with color codes
    return (f"[download] {GREEN}{video_id}{RESET}: {BLUE}{title}{RESET} "
            "has already been recorded in the archive")


@pytest.mark.parametrize(
    "video_id, title, expected",
    [
        ("N5EXFq8jP6o", "Cengiz Özkan - Değme Felek I Official Music Video © 2015 Kalan Müzik",
         "Cengiz Özkan - Değme Felek"),
        ("-KmnOncGQzo", "Musa Eroğlu & Cem Adrian - Yolun Sonu Görünüyor",
         "Musa Eroğlu & Cem Adrian - Yolun Sonu Görünüyor"),
        ("n-cSwuPKO24", "Grup Abdal - Şifa İstemem Balından [ Ozanca © 2013 Kalan Müzik ]",
         "Grup Abdal - Şifa İstemem Balından"),
    ],
)
def test_skipped_titles_ignore_colors(video_id, title, expected):
    events = []
    result = DownloadResult()
    _Logger(result, events.append).debug(archive_message(video_id, title))
    assert events == [{"type": "skipped", "title": expected}]
    assert result.skipped == [expected]


def test_errors_ignore_colors():
    events = []
    result = DownloadResult()
    _Logger(result, events.append).error(f"{RED}ERROR:{RESET} [youtube] rIlwGH44biM: Private video")
    assert result.failed == ["[youtube] rIlwGH44biM: Private video"]
    assert events == [{"type": "error", "message": "[youtube] rIlwGH44biM: Private video"}]
