"""Add third-party notices and license texts to a built Klay package.

Usage: python packaging/collect_licenses.py dist/Klay
"""
import shutil
import ssl
import sys
import sysconfig
from importlib.metadata import distribution, version
from pathlib import Path

PACKAGING_DIRECTORY = Path(__file__).parent
LICENSE_FILE_KEYWORDS = ("license", "copying", "notice")

BUNDLED_PACKAGES = {
    "brotli": "MIT",
    "certifi": "MPL-2.0",
    "charset-normalizer": "MIT",
    "idna": "BSD-3-Clause",
    "packaging": "Apache-2.0 OR BSD-2-Clause",
    "pycryptodomex": "BSD-2-Clause and public domain",
    "pyinstaller": "GPL-2.0-or-later with bootloader exception",
    "requests": "Apache-2.0",
    "setuptools": "MIT",
    "urllib3": "MIT",
    "websockets": "BSD-3-Clause",
    "yt-dlp": "Unlicense",
    "yt-dlp-ejs": "Unlicense, MIT, and ISC",
}


def copy_package_licenses(package: str, destination: Path) -> None:
    license_files = [
        file
        for file in distribution(package).files or []
        if ".dist-info" in file.parts[0]
        and any(keyword in file.name.lower() for keyword in LICENSE_FILE_KEYWORDS)
    ]

    if not license_files:
        raise FileNotFoundError(f"No license file found for {package}")

    destination.mkdir(parents=True)

    for file in license_files:
        shutil.copy(file.locate(), destination / file.name)


def find_python_license() -> Path:
    candidates = [
        Path(sys.base_prefix) / "LICENSE.txt",
        Path(sysconfig.get_path("stdlib", vars={"base": sys.base_prefix})) / "LICENSE.txt",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError("Python license file not found")


def main() -> None:
    package_directory = Path(sys.argv[1])
    licenses_directory = package_directory / "licenses"

    shutil.copytree(PACKAGING_DIRECTORY / "licenses", licenses_directory)
    shutil.copy(find_python_license(), licenses_directory / "Python-LICENSE.txt")

    for package in BUNDLED_PACKAGES:
        copy_package_licenses(package, licenses_directory / "python-packages" / package)

    python_packages = "\n".join(
        f"{package} {version(package)} - {license_name}"
        for package, license_name in BUNDLED_PACKAGES.items()
    )

    pyside6_version = version("PySide6")
    major, minor, *_ = pyside6_version.split(".")

    notices = (PACKAGING_DIRECTORY / "THIRD_PARTY_NOTICES.txt").read_text(encoding="utf-8")

    for placeholder, value in {
        "{klay_version}": version("klay"),
        "{pyside6_version}": pyside6_version,
        "{qt_series}": f"{major}.{minor}",
        "{python_version}": sys.version.split()[0],
        "{openssl_version}": ssl.OPENSSL_VERSION.split()[1],
        "{python_packages}": python_packages,
    }.items():
        notices = notices.replace(placeholder, value)

    (package_directory / "THIRD_PARTY_NOTICES.txt").write_text(notices, encoding="utf-8")


if __name__ == "__main__":
    main()
