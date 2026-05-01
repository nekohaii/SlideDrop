from __future__ import annotations

"""
Application naming, immutable defaults, and persisted session settings.

All user-adjustable values belong in SessionSettings / SettingsStore.
Install-path constants and supported formats live here alongside APP_NAME.
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .version import __version__ as APP_VERSION

APP_NAME = "SlideDrop"

if sys.platform == "darwin":
    DEFAULT_LIBREOFFICE_PATH = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
else:
    DEFAULT_LIBREOFFICE_PATH = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")

SUPPORTED_EXTENSIONS = {".ppt", ".pptx"}
PDF_OUTPUT_FOLDER_NAME = "pdf"

# LibreOffice Impress PDF filter tuning hook name for advanced callers.
EXPERIMENTAL_HIGH_QUALITY_FILTER = "impress_pdf_Export"


@dataclass
class SessionSettings:
    last_used_folder: Path | None = None
    libreoffice_path: Path | None = None
    open_output_when_finished: bool = False
    conversion_timeout_seconds: int = 300
    skip_if_unchanged: bool = False
    export_speaker_notes: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> SessionSettings:
        last_used_folder = data.get("last_used_folder")
        libreoffice_path = data.get("libreoffice_path")
        return cls(
            last_used_folder=Path(last_used_folder) if last_used_folder else None,
            libreoffice_path=Path(libreoffice_path) if libreoffice_path else None,
            open_output_when_finished=bool(data.get("open_output_when_finished", False)),
            conversion_timeout_seconds=int(data.get("conversion_timeout_seconds", 300)),
            skip_if_unchanged=bool(data.get("skip_if_unchanged", False)),
            export_speaker_notes=bool(data.get("export_speaker_notes", False)),
        )

    def to_dict(self) -> dict[str, str | bool | int | None]:
        data = asdict(self)
        data["last_used_folder"] = str(self.last_used_folder) if self.last_used_folder else None
        data["libreoffice_path"] = str(self.libreoffice_path) if self.libreoffice_path else None
        return data


def user_data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / APP_NAME


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or user_data_dir() / "settings.json"

    def load(self) -> SessionSettings:
        if not self.path.exists():
            return SessionSettings()
        try:
            return SessionSettings.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, TypeError):
            return SessionSettings()

    def save(self, settings: SessionSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(settings.to_dict(), indent=2), encoding="utf-8")
