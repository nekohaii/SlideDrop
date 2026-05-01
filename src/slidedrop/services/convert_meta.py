from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


META_SUFFIX = ".slidedrop-meta.json"


@dataclass
class ConvertMetaRecord:
    version: int
    source_sha256: str
    source_size: int


def meta_path_for_pdf(output_pdf: Path) -> Path:
    return output_pdf.with_name(output_pdf.name + META_SUFFIX)


def load_meta(output_pdf: Path) -> ConvertMetaRecord | None:
    path = meta_path_for_pdf(output_pdf)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return ConvertMetaRecord(
            version=int(raw["version"]),
            source_sha256=str(raw["source_sha256"]),
            source_size=int(raw["source_size"]),
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def save_meta(output_pdf: Path, source_sha256: str, source_size: int) -> None:
    path = meta_path_for_pdf(output_pdf)
    payload = {
        "version": 1,
        "source_sha256": source_sha256,
        "source_size": source_size,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def meta_matches(record: ConvertMetaRecord, source_sha256: str, source_size: int) -> bool:
    return record.version == 1 and record.source_sha256 == source_sha256 and record.source_size == source_size
