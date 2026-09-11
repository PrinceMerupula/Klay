from urllib.parse import urlparse

import yt_dlp


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)

    return (
        parsed_url.scheme in ("http", "https")
        and bool(parsed_url.netloc)
    )


def download(url: str) -> None:
    options = {}

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])