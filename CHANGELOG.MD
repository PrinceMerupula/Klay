# Changelog

## Unreleased

## v0.0.17 - Persistent preferences and logical defaults

### Added
- QSettings used for persistent user preferences
- QStandardPaths used to set default download directory (user Downloads folder)
- If a standard Downloads location can't be found/resolved, defaults to home directory
- Restores previous selected download mode, audio format, and download folder

### Altered
- Downloads will default to the Downloads folder if possible unless changed by the user
- Download options will restore correct on/off states based on saved download mode

## v0.0.16 - Download cancellation

### Added
 - Now able to cancel an active download
 - Thread-safe cancellation requests between GUI and background download worker
 - Separate handler for canceled downloads so user cancellation isn't reported as a failure
 - Cancel button that's only available to click while a download is ongoing
 
### Altered
- Download controls return to default after download is canceled

### Notes
- .part files are kept on system, which means retrying a cancellation will continue where it was last (might be revisited in the future)
- Cancellation handled properly rather than via a forcible termination of the download thread

## v0.0.15 - Audio output format + conversion

### Added 
- Audio output format selection for audio only downloads
- MP3 and M4A conversion through yt-dlp via FFmpeg
- Download controls are now context-aware and will be grayed out when inapplicable

### Altered
- Renamed "Best Quality" to "Video + Audio" for clarity
- Audio format selection disabled for video downlad modes
- Video resolution selection disabled for audio download mode

## v0.0.14 - Selectable video quality

### Added
- Selectable video quality based on resolutions after media analysis
- Quality options populated from available formats in yt-dlp
- "Best available" downloads maximum quality available

### Altered
- Selected video quality now passed to yt-dlp through download worker 
- Best Quality and Video Only modes download based on maximum selected resolution
- Audio Only mode ignores video settings

### Notes
- Simplify resolution options in the future (can remove things like 90p since they'd likely never be used)
- Improve UI and remove video resolutions from audio only mode in future

## v0.0.13 - Download mode selection

### Added
- Download mode selection
- Best Quality - video w/ audio
- Video Only - video w/o audio.
- Audio Only - just audio

### Altered
- Selected download mode now passed through the download worker to yt-dlp
- Video Only downloads prefer WebM video streams - mp4 downloads were bugged (will be investigated in a later version)

### Notes 
- Need to look into file type issues, will likely need to work directly with ffmpeg

## v0.0.12 - Save location picker

### Added
- Native folder picker allows user to select where the download will be saved to
- Displays currently selected download location
- Cchosen output directory passed to yt-dlp

### Altered
- Downloads occur in wherever the user selects, instead of the default app location
- Canceling the folder picker keeps the previously selected download location

## v0.0.11 - Richer metadata preview

### Added
- Richer media metadata preview after analysis
- Shows:
-  Media title
-  Uploader/channel name
-  media duration
-  Best available video resolution

### Altered
- Metadata preview no longer only shows title, 3 additional details now shown

## v0.0.10 - Background metadata analysis

### Added
- Qt worker thread that does metadata analysis in background
- Analysis worker to retrieve media info w/o blocking interface
- Signals return metadata and analysis failures to main GUI
- During metadata retrieval, show that the analysis is occurring by displaying an "Analyzing" status

### Altered
- Media analysis won't block the main GUI thread while analysis occurs
- Analyze button disabled during analysis

## v0.0.9 - Media metadata preview

### Added
- Media metadata extracted using yt-dlp
- Analyze button allows for the URL to be inspected before the download
- Detected media title shown in GUI (additional information to be implemented in a future version)
- Failed metadata analysis results in a user-facing error popup

### Altered
- Altered progress bar, rollback updates are visible once again due to bug in previous implementation (will be fixed in a future version)

## v0.0.8 - Download progress bar

### Added
- yt-dlp reports download progress
- Progress updates from background worker to GUI
- GUI shows a progress for active downloads
- Progress bar ignores rollback updates due to multi-stream downloads

## v0.0.7 - Background downloading 

### Added
- Processing downloads in the background via Qt threads
- Download worker runs yt-dlp without blocking interface
- Download successes and failures shown on main window
- Download button disabled while download is active (multiple concurrent downloads likely to be added at a later time)
- User-facing notif when a download is successful
- Protecting against closing app while download is ongoing

### Altered
- yt-dlp downloads don't block main GUI thread 

## v0.0.6 - Basic URL validation and error handling

### Added
- Basic HTTP and HTTPS URL validation
- Validation for empty input
- Warning dialogs for missing or malformed URLs
- Error handling for failed yt-dlp downloads

## v0.0.5 - End-to-end downloading

### Added
- Connected main interface to downloader module
- Added basic end-to-end media downloading from Download button
- URL input passed directly to yt-dlp and downloaded

## v0.0.4 - yt-dlp Addition

### Added
- Yt-dlp added as an app dependency
- Created a separate downloader.py to handle downloads
- Very basic downloading done through yt-dlp Python API (not through window, integration to be added later)

## v0.0.3 - Basic download interface

### Added
- Extremely simple download interface with an input field for the URL and a button to Download
- Made an initial 'MainWindow' class to manage interface
- Download button interaction for reading the entered URL (will be greatly modified in future versions)

## v0.0.2 - First window

### Added
- Initial PySide6 app entry point
- Very basic resizable app window
- 'klay' command launches the window

## v0.0.1 - Project setup

### Added
- Initial project structure
- 'pyproject.toml' project config
- PySide6 dependency installed
- 'src/klay' package structure
- Editable dev installation

## v0.0.0
- Initialized repository
