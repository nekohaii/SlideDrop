from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

_FONT_ATTR_RE = re.compile(rb'''(?:latin|ea|cs)="([^"]+)"''')


def _installed_font_names_lowercase() -> set[str]:
    names: set[str] = set()
    if sys.platform == "win32":
        fonts_dir = Path(os.getenv("WINDIR", r"C:\Windows")) / "Fonts"
        if fonts_dir.is_dir():
            for p in fonts_dir.iterdir():
                if p.is_file():
                    names.add(p.stem.lower())
    else:
        fc_list = shutil.which("fc-list")
        if fc_list:
            try:
                completed = subprocess.run(
                    [fc_list],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                for line in (completed.stdout or "").splitlines():
                    if ":" in line:
                        font_name = line.split(":", 1)[1].strip().split(":")[0].strip()
                        names.add(font_name.lower())
            except OSError:
                pass
    return names


def extract_font_requests_from_pptx(path: Path) -> set[str]:
    fonts: set[str] = set()
    try:
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if not info.filename.endswith(".xml"):
                    continue
                if not (
                    info.filename.startswith("ppt/")
                    or info.filename.startswith("ppt/slides/")
                    or info.filename.startswith("ppt/slideLayouts/")
                    or info.filename.startswith("ppt/slideMasters/")
                ):
                    continue
                try:
                    data = zf.read(info.filename)
                except OSError:
                    continue
                for match in _FONT_ATTR_RE.finditer(data):
                    raw = match.group(1).decode("utf-8", errors="ignore").strip()
                    if raw:
                        fonts.add(raw)
    except (OSError, zipfile.BadZipFile):
        return set()
    return fonts


def missing_fonts_for_presentation(path: Path) -> list[str]:
    """Return likely-missing font face names for .pptx; empty for .ppt or unknown."""
    if path.suffix.lower() != ".pptx":
        return []
    requested = extract_font_requests_from_pptx(path)
    if not requested:
        return []
    installed = _installed_font_names_lowercase()
    missing: list[str] = []
    for font in sorted(requested, key=str.casefold):
        key = font.lower()
        if key in installed:
            continue
        stem_hit = any(key in installed_name or installed_name in key for installed_name in installed)
        if stem_hit:
            continue
        missing.append(font)
    return missing
