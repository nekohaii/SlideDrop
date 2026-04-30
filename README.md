# SlideDrop

SlideDrop is a local Windows desktop utility that converts PowerPoint files (`.ppt` and `.pptx`) to PDF using LibreOffice in headless mode. It runs fully offline and does not use cloud APIs.

SlideDrop uses a fixed-size 1040x750 utility window in v1. This avoids CustomTkinter's expensive live-resize redraws and keeps the conversion workflow visually stable.

## Quick Start

1. Install LibreOffice for Windows.
2. Confirm the LibreOffice executable exists, or update `DEFAULT_LIBREOFFICE_PATH` in `src/slidedrop/config.py`.

   Windows:

   ```text
   C:\Program Files\LibreOffice\program\soffice.exe
   ```

   macOS:

   ```text
   /Applications/LibreOffice.app/Contents/MacOS/soffice
   ```

3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Run the app:

   ```powershell
   python run.py
   ```

## How To Use

- Use **Select PowerPoint Files** to add individual `.ppt` or `.pptx` files.
- Use **Select Folder** to recursively scan a folder for PowerPoint files.
- Drag-and-drop files or folders into the drop zone when `tkinterdnd2` works on your Windows setup.
- Review the queue, then click **Convert to PDF** to start batch conversion.
- Use the checkboxes in the queue to select files, then use **Remove Selected** or **Clear List** to manage the queue.
- Use **Open Output Folder** from the success message after conversion.

For folder scans, SlideDrop writes PDFs to a `pdf` folder inside the selected folder. For individually selected files from mixed locations, SlideDrop writes each PDF beside its source file.

The queue is the main workspace. It shows the file name, parent folder, and conversion status in a lightweight native list. Full paths are intentionally de-emphasized to keep the review step readable, and inactive actions stay disabled until they are useful.

## PDF Fidelity Notes

SlideDrop relies on LibreOffice Impress PDF export to preserve slide size, orientation, fonts, spacing, images, and layout as closely as LibreOffice allows. Missing fonts on the system may cause layout changes or font substitution.

PDF is a static format. It keeps slide visuals, but it does not preserve PowerPoint animations, transitions, audio, video, or interactive media behavior.

The **High Quality PDF** checkbox is experimental in v1. Until LibreOffice Impress PDF filter options are verified, SlideDrop keeps the default conversion path for reliability.

## Windows Packaging

Install packaging dependencies:

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Recommended portable release build:

```powershell
.\scripts\windows\build.ps1
```

Output:

```text
release\windows\SlideDrop-windows-portable.zip
release\windows\SlideDrop-portable\SlideDrop.exe
```

Optional one-folder build:

```powershell
.\scripts\windows\build.ps1 -Mode OneFolder
```

Build both formats:

```powershell
.\scripts\windows\build.ps1 -Mode Both
```

The portable single-EXE build is the clearest v1 artifact to publish because users only see one file. The one-folder build is still useful for diagnostics and future installer work. If drag-and-drop breaks in a frozen Windows build, manual **Select PowerPoint Files** and **Select Folder** flows remain the supported v1 fallback.

For a polished distributable installer later, wrap the portable EXE or one-folder output with an installer tool such as InstallForge or Inno Setup. LibreOffice is not bundled, so the installer should either require LibreOffice or guide users to install it.

## macOS Packaging

macOS packages must be built on macOS. PyInstaller cannot reliably create a `.app` bundle from Windows.

On a Mac:

```bash
chmod +x scripts/macos/build-macos.sh
./scripts/macos/build-macos.sh
```

Output:

```text
release/macos/SlideDrop-macOS.zip
dist/macos/SlideDrop.app
```

The macOS build is intentionally separate from the Windows release output:

```text
release/windows/SlideDrop-windows-portable.zip
release/macos/SlideDrop-macOS.zip
```

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

For public distribution, Apple notarization and code signing should be added later so users do not see Gatekeeper warnings.

## GitHub Pages

The marketing/download page lives in `docs/`.

To enable it on GitHub:

1. Push the repository to GitHub.
2. Open **Settings > Pages**.
3. Set the source to **Deploy from a branch**.
4. Choose the main branch and `/docs` folder.
5. Save, then use the generated GitHub Pages URL.

The current page is static HTML/CSS and can be edited in:

```text
docs/index.html
docs/styles.css
```
