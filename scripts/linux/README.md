# Linux / headless usage

SlideDrop is packaged primarily for Windows desktop users. On Linux you can still run
the conversion stack headlessly if LibreOffice (`soffice`) is installed:

```bash
python -m pip install -r requirements.txt
export PYTHONPATH=src
python -m slidedrop convert /path/to/file_or_folder --timeout 300
```

PyInstaller bundles for Linux are not produced by this repository yet; contributions
should mirror the Windows spec patterns under `packaging/windows`.
