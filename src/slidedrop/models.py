from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from uuid import uuid4


class FileStatus(str, Enum):
    PENDING = "Pending"
    CONVERTING = "Converting"
    DONE = "Done"
    FAILED = "Failed"


@dataclass
class QueueItem:
    source_path: Path
    output_dir: Path
    discovered_from_folder: bool = False
    status: FileStatus = FileStatus.PENDING
    message: str = ""
    output_pdf: Path | None = None
    item_id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def file_name(self) -> str:
        return self.source_path.name
