from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConversionOptions:
    """Per-run options passed into conversion engines."""

    timeout_seconds: int = 300
    skip_if_unchanged: bool = False
    export_notes_pages: bool = False
    impress_pdf_extra_properties: dict[str, object] = field(default_factory=dict)
