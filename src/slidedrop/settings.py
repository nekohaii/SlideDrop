from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import APP_NAME


@dataclass
class SessionSettings:
    last_used_folder: Path | None = None
    libreoffice_path: Path | None = None
    open_output_when_finished: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "SessionSettings":
        last_used_folder = data.get("last_used_folder")
        libreoffice_path = data.get("libreoffice_path")
        return cls(
            last_used_folder=Path(last_used_folder) if last_used_folder else None,
            libreoffice_path=Path(libreoffice_path) if libreoffice_path else None,
            open_output_when_finished=bool(data.get("open_output_when_finished", False)),
        )

    def to_dict(self) -> dict[str, str | bool | None]:
        data = asdict(self)
        data["last_used_folder"] = str(self.last_used_folder) if self.last_used_folder else None
        data["libreoffice_path"] = str(self.libreoffice_path) if self.libreoffice_path else None
        return data


def user_data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif os.sys.platform == "darwin":
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
