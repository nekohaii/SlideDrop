from __future__ import annotations

from pathlib import Path

from slidedrop.engines.base import ConversionResult
from slidedrop.engines.options import ConversionOptions
from slidedrop.models import QueueItem


class MockStrategy:
    """Test-only engine; lives outside production package for frozen builds."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def validate(self) -> tuple[bool, str]:
        return True, "Mock conversion engine ready."

    def convert(self, item: QueueItem, options: ConversionOptions | None = None) -> ConversionResult:
        _ = options
        if self.should_fail:
            return ConversionResult(False, None, "Mock conversion failed.")

        item.output_dir.mkdir(parents=True, exist_ok=True)
        output_pdf = Path(item.output_dir) / f"{item.source_path.stem}.pdf"
        output_pdf.write_bytes(b"%PDF-1.4\n% SlideDrop mock PDF\n")
        return ConversionResult(True, output_pdf, f"Created {output_pdf}")
