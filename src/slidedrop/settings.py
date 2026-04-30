from dataclasses import dataclass
from pathlib import Path


@dataclass
class SessionSettings:
    last_used_folder: Path | None = None
    high_quality_pdf: bool = False
    open_output_when_finished: bool = False
