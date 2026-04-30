import sys
from pathlib import Path


APP_NAME = "SlideDrop"
APP_VERSION = "0.1.0"
if sys.platform == "darwin":
    DEFAULT_LIBREOFFICE_PATH = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
else:
    DEFAULT_LIBREOFFICE_PATH = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
SUPPORTED_EXTENSIONS = {".ppt", ".pptx"}
PDF_OUTPUT_FOLDER_NAME = "pdf"

# LibreOffice Impress PDF filter tuning is intentionally conservative in v1.
# Keep this separate so verified export options can be added later.
EXPERIMENTAL_HIGH_QUALITY_FILTER = "impress_pdf_Export"
