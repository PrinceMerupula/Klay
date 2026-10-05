from urllib.parse import urlparse

import yt_dlp

from klay.dependencies import get_deno_path, get_ffmpeg_path


class DownloadCanceled(Exception):
    pass


def get_base_options() -> dict:
    options = {}

    deno_path = get_deno_path()

    if deno_path is not None:
        options["js_runtimes"] = {
            "deno": {
                "path": deno_path,
            }
        }

    return options

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
    download_mode="Video + Audio",
    max_height=None,
    audio_format="Original",
) -> str | None:
    options = get_base_options()

    ffmpeg_path = get_ffmpeg_path()

    if ffmpeg_path is not None:
        options["ffmpeg_location"] = ffmpeg_path

    final_filepath = None

    def capture_final_filepath(data):
        nonlocal final_filepath

        if data.get("status") != "finished":
            return

        info = data.get("info_dict", {})
        filepath = info.get("filepath")

        if filepath:
            final_filepath = filepath

    options["postprocessor_hooks"] = [
        capture_final_filepath,
    ]

    if progress_hook is not None:
        options["progress_hooks"] = [progress_hook]

    if output_directory is not None:
        options["paths"] = {
            "home": output_directory,
        }

    if download_mode == "Video + Audio":
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

        if audio_format == "MP3":
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        elif audio_format == "M4A":
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ]

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    return final_filepath

def get_media_info(url: str) -> dict:
    options = get_base_options()

    options.update({
        "quiet": True,
        "skip_download": True,
    })

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=False,
        )

    return info