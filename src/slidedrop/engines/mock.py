from __future__ import annotations

from pathlib import Path

from ..models import QueueItem
from .base import ConversionResult


class MockStrategy:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def validate(self) -> tuple[bool, str]:
        return True, "Mock conversion engine ready."

    def convert(self, item: QueueItem) -> ConversionResult:
        if self.should_fail:
            return ConversionResult(False, None, "Mock conversion failed.")

        item.output_dir.mkdir(parents=True, exist_ok=True)
        output_pdf = Path(item.output_dir) / f"{item.source_path.stem}.pdf"
        output_pdf.write_bytes(b"%PDF-1.4\n% SlideDrop mock PDF\n")
        return ConversionResult(True, output_pdf, f"Created {output_pdf}")
