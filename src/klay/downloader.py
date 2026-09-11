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
    max_height=None,
) -> None:
    options = {}

    if progress_hook is not None:
        options["progress_hooks"] = [progress_hook]

    if output_directory is not None:
        options["paths"] = {
            "home": output_directory,
        }

    if download_mode == "Best Quality":
        if max_height is None:
            options["format"] = (
                "bestvideo+bestaudio/best"
            )
        else:
            options["format"] = (
                f"bestvideo[height<={max_height}]"
                f"+bestaudio/"
                f"best[height<={max_height}]"
            )

    elif download_mode == "Video Only":
        if max_height is None:
            options["format"] = (
                "bestvideo[ext=webm]/bestvideo"
            )
        else:
            options["format"] = (
                f"bestvideo[ext=webm]"
                f"[height<={max_height}]/"
                f"bestvideo[height<={max_height}]"
            )

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
        info = ydl.extract_info(
            url,
            download=False,
        )

    return info