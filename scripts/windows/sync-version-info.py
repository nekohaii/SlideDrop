#!/usr/bin/env python3
"""Regenerate packaging/windows/version_info.txt from slidedrop.version.__version__."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))
    from slidedrop.version import __version__

    parts = [int(segment) for segment in __version__.split(".")]
    while len(parts) < 4:
        parts.append(0)
    major, minor, patch, build = parts[0], parts[1], parts[2], parts[3]
    dotted_file = f"{major}.{minor}.{patch}.{build}"

    target = root / "packaging" / "windows" / "version_info.txt"
    output = (
        "# UTF-8\nVSVersionInfo(\n"
        "  ffi=FixedFileInfo(\n"
        f"    filevers=({major}, {minor}, {patch}, {build}),\n"
        f"    prodvers=({major}, {minor}, {patch}, {build}),\n"
        "    mask=0x3f,\n"
        "    flags=0x0,\n"
        "    OS=0x40004,\n"
        "    fileType=0x1,\n"
        "    subtype=0x0,\n"
        "    date=(0, 0)\n"
        "  ),\n"
        "  kids=[\n"
        "    StringFileInfo([\n"
        "      StringTable(\n"
        "        '040904B0',\n"
        "        [\n"
        "          StringStruct('CompanyName', 'SlideDrop'),\n"
        "          StringStruct('FileDescription', 'SlideDrop PowerPoint to PDF Converter'),\n"
        f"          StringStruct('FileVersion', '{dotted_file}'),\n"
        "          StringStruct('InternalName', 'SlideDrop'),\n"
        "          StringStruct('OriginalFilename', 'SlideDrop.exe'),\n"
        "          StringStruct('ProductName', 'SlideDrop'),\n"
        f"          StringStruct('ProductVersion', '{dotted_file}')\n"
        "        ]\n"
        "      )\n"
        "    ]),\n"
        "    VarFileInfo([VarStruct('Translation', [1033, 1200])])\n"
        "  ]\n"
        ")\n"
    )
    target.write_text(output, encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
