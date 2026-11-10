# Klay
A simple desktop application built on [yt-dlp] (https://github.com/yt-dlp/yt-dlp) for downloading video and audio from YouTube (and other websites).

## Download

Get the newest version from the [Releases page] (https://github.com/PrinceMerupula/Klay/releases). 
Klay currently supports the following version(s):
- Windows 11 (x86-64)

## Installation

1. Download the file from the Releases page
2. Extract the ZIP file
3. Run 'Klay.exe'

Keep the '_internal' folder next to 'Klay.exe', as Klay will not start otherwise.

Klay is not yet code-signed. As a result, Windows will likely show a "Windows protected your PC" warning. 
Click **More info**, then click **Run anyway**

## Known Issues

- Links to a playlist may download every video in the playlist (options to download a singular video, specific videos, or the whole playlist will be added at a later time)
- Changes in YouTube may result in Klay no longer working
- Download bar does not reset to zero after a download is completed until the analysis is run

## License

Klay is licensed under the [MIT License] (LICENSE).

The Windows package also includes FFMpeg, Qt, and other software under their own licenses, listed in 'THIRD_PARTY_NOTICES.txt" inside the ZIP. The FFMpeg source code is available on the release page. 

## Current Milestone
v0.1.0 - First public release