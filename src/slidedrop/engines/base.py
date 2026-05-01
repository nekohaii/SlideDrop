from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..models import QueueItem


@dataclass
class ConversionResult:
    success: bool
    output_pdf: Path | None
    message: str
    stdout: str = ""
    stderr: str = ""


class DependencyMissingError(RuntimeError):
    pass


class ConversionEngine(Protocol):
    def validate(self) -> tuple[bool, str]:
        ...

    def convert(self, item: QueueItem) -> ConversionResult:
        ...
