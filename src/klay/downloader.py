import yt_dlp


def download(url: str) -> None:
    options = {}

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])