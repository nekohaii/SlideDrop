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
- Optional skip-if-unchanged conversions using a SHA-256 sidecar next to each PDF.
- Font preflight for `.pptx` warns when referenced fonts look missing before conversion starts.

## Automation (CLI and local API)

Install the package (`pip install -e .`), then use the `slidedrop` console script:

```powershell
slidedrop gui
```

Headless batch conversion prints one JSON line per source file:

```powershell
slidedrop convert .\deck.pptx .\incoming_folder --timeout 300 --skip-unchanged
```

Local JSON automation server (loopback only):

```powershell
slidedrop api --host 127.0.0.1 --port 8765
```

`POST /v1/convert` accepts JSON such as:

```json
{
  "paths": ["C:\\\\incoming\\\\deck.pptx"],
  "timeout": 300,
  "skip_if_unchanged": true,
  "export_notes": false,
  "pdf_extra": {}
}
```

Advanced `.pptx` tuning merges keys into LibreOffice `impress_pdf_Export` via `--pdf-extra-json` or `pdf_extra`.

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

## Supply chain and CI

- Dependabot watches pip and GitHub Actions updates (`.github/dependabot.yml`).
- Tests run on every push with a **65% coverage floor** on automation-tested modules (the GUI and local API entrypoints are excluded from that denominator; see `pyproject.toml`).
- Enable **branch protection** on `main` requiring the `Tests` workflow to pass before merges.
- GitHub Pages can deploy via `.github/workflows/pages.yml`. Choose **Pages → GitHub Actions** if you migrate away from branch `/docs` publishing.
- macOS `.app` builds run on GitHub-hosted runners via `.github/workflows/build-macos.yml`; Apple code signing and notarization still require developer certificates stored as repository secrets.

Pinned versions live in `requirements.txt`, `requirements-dev.txt`, and `pyproject.toml`. For hash-locked installs, generate a lock file with `pip-compile --generate-hashes` in your release environment.

Optional crash telemetry: set `SLIDEDROP_SENTRY_DSN` and install `sentry-sdk` if you want opt-in reporting.

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

Run tests (matches CI coverage gate):

```powershell
python -m pytest --cov=slidedrop --cov-fail-under=65
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

Inno Setup template (adjust paths after running `build.ps1`):

```text
packaging/windows/installer.iss
```

Windows SmartScreen warnings persist until you attach an Authenticode certificate; plan signing for mainstream consumer releases.

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
