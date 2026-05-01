# SlideDrop

SlideDrop is a local-first desktop utility that converts PowerPoint files
(`.ppt` and `.pptx`) to PDF using LibreOffice on the user's machine. Windows is
the primary supported platform today; macOS packaging is prepared as a separate
track.

Website: https://nekohaii.github.io/SlideDrop/

## Download

Download the latest Windows build from GitHub Releases:

https://github.com/nekohaii/SlideDrop/releases

Current package name:

```text
SlideDrop-windows-portable.zip
```

Unzip the package and run `SlideDrop.exe`.

## Features

- Convert individual PowerPoint files or entire folders.
- Recursively scans selected folders for `.ppt` and `.pptx` files.
- Prevents duplicate files in the queue.
- Converts in a background worker so the UI stays responsive.
- Writes folder-scan PDFs into a local `pdf` folder.
- Writes individually selected mixed-location PDFs beside their source files.
- Keeps files local; no cloud upload is used.

## Limitations

SlideDrop relies on LibreOffice Impress PDF export. It preserves static slide
visuals as closely as LibreOffice allows, but missing fonts may cause layout
changes or font substitution.

PDF is a static format. Animations, transitions, audio, video, and interactive
PowerPoint behavior are not preserved.

## LibreOffice

Development builds can use a system LibreOffice installation or a bundled
runtime placed in `resources/`.

The app checks for LibreOffice in this order:

1. Bundled resource paths.
2. Saved user settings.
3. The system `PATH`.
4. Standard platform install locations.

Commercial installers should bundle LibreOffice separately and include the
required LibreOffice notices. See `NOTICE.txt` and `resources/README.md`.

## Legal

This repository is source-visible but proprietary. See `LICENSE`.

LibreOffice is a third-party project and remains governed by its own licenses.
See `NOTICE.txt`.

## Developer Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Run the app from source:

```powershell
python run.py
```

Run tests:

```powershell
python -m pytest
```

## Windows Packaging

Recommended portable release build:

```powershell
.\scripts\windows\build.ps1
```

Output:

```text
release\windows\SlideDrop-windows-portable.zip
release\windows\SlideDrop-portable\SlideDrop.exe
```

## macOS Packaging

macOS packages must be built on macOS.

```bash
chmod +x scripts/macos/build-macos.sh
./scripts/macos/build-macos.sh
```

Output:

```text
release/macos/SlideDrop-macOS.zip
dist/macos/SlideDrop.app
```

Apple code signing and notarization should be added before public macOS sales.

## Project Layout

Platform-specific packaging files are intentionally separated:

```text
packaging/windows/
packaging/macos/
scripts/windows/
scripts/macos/
release/windows/
release/macos/
```

The GitHub Pages site lives in `docs/`.
