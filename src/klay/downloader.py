from urllib.parse import urlparse

import yt_dlp


def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)

    return (
        parsed_url.scheme in ("http", "https")
        and bool(parsed_url.netloc)
    )

def download(
    url: str,
    progress_hook=None,
    output_directory=None,
    download_mode="Best Quality",
) -> None:
    options = {}

    if progress_hook is not None:
        options["progress_hooks"] = [progress_hook]

    if output_directory is not None:
        options["paths"] = {
            "home": output_directory,
        }

    if download_mode == "Best Quality":
        options["format"] = "bestvideo+bestaudio/best"

    elif download_mode == "Video Only":
        options["format"] = "bestvideo[ext=webm]/bestvideo"

    elif download_mode == "Audio Only":
        options["format"] = "bestaudio"

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

def get_media_info(url: str) -> dict:
    options = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)

    return info