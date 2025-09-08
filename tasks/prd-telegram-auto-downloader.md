# Product Requirements Document: Telegram Auto Downloader

## Introduction/Overview
A desktop automation tool that monitors a user-defined screen region for Telegram download states and automatically clicks on undownloaded media files. The tool provides real-time visual feedback by overlaying detection boxes on identified images and automatically scrolls through content based on download completion rates.

## Goals
1. Automate the media download process in Telegram Desktop application
2. Provide visual feedback for detected download states in real-time
3. Minimize manual intervention for bulk media downloads
4. Support cross-platform operation (Linux, Windows, Mac)
5. Offer customizable automation parameters for different use cases

## User Stories
1. **As a Telegram user**, I want to select a screen region containing media files so that the tool can monitor only the relevant area
2. **As a Telegram user**, I want to see visual indicators of detected images so that I know the tool is working correctly
3. **As a Telegram user**, I want the tool to automatically click on undownloaded files so that I don't have to manually click each one
4. **As a Telegram user**, I want the tool to automatically scroll when most files are downloaded so that I can process large media collections
5. **As a power user**, I want to customize scroll speed and click intervals so that I can optimize for my internet speed and system

## Functional Requirements

### Core Detection
1. The system must allow users to select a rectangular screen region via drag-and-drop
2. The system must detect three image states with 90% accuracy:
   - Not downloaded (`/home/apic/python/telegram_downloader/images/not_download.jpg`)
   - Downloading (`/home/apic/python/telegram_downloader/images/downloading.jpg`)
   - Downloaded (`/home/apic/python/telegram_downloader/images/downloaded.jpg`)
3. The system must use a combination of template matching, feature matching, and pixel comparison for robust detection

### Visual Feedback
4. The system must display a transparent overlay window showing the selected region
5. The system must draw bounding boxes around detected images in real-time
6. The system must use different colors for different download states (e.g., red for not downloaded, yellow for downloading, green for downloaded)

### Automation Logic
7. The system must automatically click on "not downloaded" images
8. The system must calculate the percentage of downloaded images relative to total detected images
9. The system must scroll down when downloaded images exceed 80% of total images
10. The system must stop scrolling when downloaded images are less than 20% of total images
11. The system must allow users to configure scroll amount and speed
12. The system must allow users to configure click intervals and delays

### User Interface
13. The system must provide Start/Stop buttons for automation control
14. The system must display current statistics (total images, downloaded, downloading, not downloaded)
15. The system must provide settings panel for:
    - Scroll speed (pixels per scroll)
    - Scroll delay (milliseconds between scrolls)
    - Click delay (milliseconds between clicks)
    - Detection threshold (matching accuracy percentage)
16. The system must show status notifications for important events

### Platform Support
17. The system must run on Linux, Windows, and macOS
18. The system must not require administrative privileges for basic operation

## Non-Goals (Out of Scope)
1. This tool will NOT download files directly from Telegram servers
2. This tool will NOT bypass Telegram's security or authentication
3. This tool will NOT work with Telegram Web or mobile versions (only Desktop)
4. This tool will NOT handle video previews or non-image media detection
5. This tool will NOT provide batch file management after download
6. This tool will NOT integrate with Telegram's API

## Design Considerations

### UI Framework Selection
Given the segmentation fault issues with PySide/Tkinter and the need for overlay capabilities:
- **Recommended**: Python with OpenCV + lightweight overlay system using `pygame` or `pyglet`
- **Alternative 1**: C++ with Qt (robust but complex)
- **Alternative 2**: Electron with screen capture APIs (cross-platform but resource-heavy)

### Visual Design
- Overlay window should be semi-transparent (adjustable opacity)
- Bounding boxes should be clearly visible but not obstruct content
- Control panel should be minimal and movable
- Status indicators should use intuitive colors

## Technical Considerations

### Dependencies
- Image processing: OpenCV for detection and matching
- Screen capture: Platform-specific libraries (mss for Python, or native APIs)
- GUI: Lightweight overlay framework
- Automation: PyAutoGUI or platform-specific automation libraries

### Performance
- Detection should run at minimum 5 FPS for responsive feedback
- Click actions should have configurable delays to avoid overwhelming Telegram
- Memory usage should be optimized for long-running sessions

### Error Handling
- Gracefully handle screen resolution changes
- Detect when Telegram window is minimized or hidden
- Provide clear error messages for common issues

## Success Metrics
1. Successfully detect and click on 95% of visible "not downloaded" images
2. Reduce manual download time by at least 80%
3. Maintain stable operation for sessions longer than 1 hour
4. Cross-platform compatibility with consistent behavior
5. User-reported satisfaction with automation accuracy

## Open Questions
1. Should the tool support multiple Telegram windows simultaneously?
2. Is there a need for keyboard shortcuts for quick start/stop?
3. Should download history be logged for later review?
4. What should happen if Telegram becomes unresponsive?
5. Should there be a "safe mode" with slower, more careful clicking?
6. Is there a preferred maximum scroll speed to avoid detection issues?