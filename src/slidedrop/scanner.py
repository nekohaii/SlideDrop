from __future__ import annotations

from pathlib import Path

from .config import PDF_OUTPUT_FOLDER_NAME, SUPPORTED_EXTENSIONS
from .models import QueueItem


class FileScanner:
    @staticmethod
    def is_powerpoint_file(path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS

    @staticmethod
    def normalize_path(path: str | Path) -> Path:
        return Path(path).expanduser().resolve()

    def scan_file(self, path: str | Path) -> QueueItem | None:
        source = self.normalize_path(path)
        if not self.is_powerpoint_file(source):
            return None
        return QueueItem(source_path=source, output_dir=source.parent)

    def scan_folder(self, path: str | Path) -> list[QueueItem]:
        folder = self.normalize_path(path)
        if not folder.is_dir():
            return []

        output_dir = folder / PDF_OUTPUT_FOLDER_NAME
        items: list[QueueItem] = []
        for source in sorted(folder.rglob("*")):
            if self.is_powerpoint_file(source):
                items.append(
                    QueueItem(
                        source_path=source.resolve(),
                        output_dir=output_dir,
                        discovered_from_folder=True,
                    )
                )
        return items

    def scan_paths(self, paths: list[str | Path]) -> list[QueueItem]:
        items: list[QueueItem] = []
        seen: set[Path] = set()

        for raw_path in paths:
            path = self.normalize_path(raw_path)
            found = self.scan_folder(path) if path.is_dir() else [self.scan_file(path)]
            for item in found:
                if item is None or item.source_path in seen:
                    continue
                seen.add(item.source_path)
                items.append(item)

        return items
