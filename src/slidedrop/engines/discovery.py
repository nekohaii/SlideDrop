from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from ..config import DEFAULT_LIBREOFFICE_PATH


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def _bundled_candidates() -> list[Path]:
    root = _project_root()
    return [
        root / "resources" / "windows" / "libreoffice" / "program" / "soffice.exe",
        root / "resources" / "macos" / "LibreOffice.app" / "Contents" / "MacOS" / "soffice",
    ]


def _path_candidate() -> Path | None:
    executable = shutil.which("soffice") or shutil.which("soffice.exe")
    return Path(executable) if executable else None


def _windows_registry_candidates() -> list[Path]:
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:
        return []

    candidates: list[Path] = []
    keys = [
        r"SOFTWARE\LibreOffice\UNO\InstallPath",
        r"SOFTWARE\WOW6432Node\LibreOffice\UNO\InstallPath",
    ]
    for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for key_path in keys:
            try:
                with winreg.OpenKey(root_key, key_path) as key:
                    install_path, _ = winreg.QueryValueEx(key, "")
                    candidates.append(Path(install_path) / "soffice.exe")
            except OSError:
                continue
    return candidates


def discover_libreoffice(user_selected_path: Path | None = None) -> Path | None:
    candidates: list[Path | None] = [
        *_bundled_candidates(),
        user_selected_path,
        _path_candidate(),
        *_windows_registry_candidates(),
        DEFAULT_LIBREOFFICE_PATH,
    ]

    if sys.platform == "darwin":
        candidates.append(Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"))

    for candidate in candidates:
        if candidate and candidate.exists() and candidate.is_file():
            return candidate
    return None
