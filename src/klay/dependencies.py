import shutil
import sys
from pathlib import Path


def get_bundled_binary_directory() -> Path | None:
    """Return the directory containing Klay's bundled external binaries."""
    if not getattr(sys, "frozen", False):
        return None

    return Path(sys._MEIPASS) / "bin"


def get_ffmpeg_path() -> str | None:
    """Return the path to FFmpeg, bundled or installed on PATH."""
    binary_directory = get_bundled_binary_directory()

    if binary_directory is not None:
        executable = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
        path = binary_directory / executable

        if path.is_file():
            return str(path)

        return None

    return shutil.which("ffmpeg")


def get_ffprobe_path() -> str | None:
    """Return the path to FFprobe, bundled or installed on PATH."""
    binary_directory = get_bundled_binary_directory()

    if binary_directory is not None:
        executable = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"
        path = binary_directory / executable

        if path.is_file():
            return str(path)

        return None

    return shutil.which("ffprobe")


def get_deno_path() -> str | None:
    """Return the path to Deno, bundled or installed on PATH."""
    binary_directory = get_bundled_binary_directory()

    if binary_directory is not None:
        executable = "deno.exe" if sys.platform == "win32" else "deno"
        path = binary_directory / executable

        if path.is_file():
            return str(path)

        return None

    return shutil.which("deno")


def is_ffmpeg_available() -> bool:
    return get_ffmpeg_path() is not None
