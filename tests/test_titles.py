import pytest

from titles import clean_title


@pytest.mark.parametrize(
    "title, expected",
    [
        (
            "Cengiz Özkan - Değme Felek I Official Music Video © 2015 Kalan Müzik",
            ("Cengiz Özkan", "Değme Felek"),
        ),
        (
            "Grup Abdal - Şifa İstemem Balından [ Ozanca © 2013 Kalan Müzik ]",
            ("Grup Abdal", "Şifa İstemem Balından"),
        ),
        (
            "Orhan Ölmez ft. Canan Çal - Yar Ağladı Ben Ağladım ｜ Mehmet'in Gezegeni",
            ("Orhan Ölmez ft. Canan Çal", "Yar Ağladı Ben Ağladım"),
        ),
        (
            "Engin Nurşani-VERİN BENİM SEVDİĞİMİ-Canlı",
            ("Engin Nurşani", "VERİN BENİM SEVDİĞİMİ (Canlı)"),
        ),
        (
            "Selçuk Balcı - Gel Sar Beni (Çimen Gözlüm)",
            ("Selçuk Balcı", "Gel Sar Beni (Çimen Gözlüm)"),
        ),
        (
            "Musa Eroğlu & Cem Adrian - Yolun Sonu Görünüyor",
            ("Musa Eroğlu & Cem Adrian", "Yolun Sonu Görünüyor"),
        ),
        ("Artist - Song (Official Video)", ("Artist", "Song")),
        ("Artist - Song [HD]", ("Artist", "Song")),
        ("Artist - Song (Lyrics)", ("Artist", "Song")),
        ("Jay-Z - Empire State Of Mind", ("Jay-Z", "Empire State Of Mind")),
        ("Now I Know - Song Title", ("Now I Know", "Song Title")),
        ("Ahmet Kaya | Kum Gibi", ("Ahmet Kaya", "Kum Gibi")),
        ("Artist - Song (Radio Edit)", ("Artist", "Song (Radio Edit)")),
        ("Me at the zoo", (None, "Me at the zoo")),
    ],
)
def test_clean_title(title, expected):
    assert clean_title(title) == expected


def test_never_returns_empty():
    assert clean_title("Official Video") == (None, "Official Video")
