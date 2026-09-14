import shutil


def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None