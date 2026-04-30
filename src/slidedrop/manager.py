from __future__ import annotations

from pathlib import Path

from .models import FileStatus, QueueItem
from .scanner import FileScanner


class ConversionManager:
    def __init__(self, scanner: FileScanner | None = None) -> None:
        self.scanner = scanner or FileScanner()
        self.items: list[QueueItem] = []
        self._known_sources: set[Path] = set()

    def add_paths(self, paths: list[str | Path]) -> list[QueueItem]:
        added: list[QueueItem] = []
        for item in self.scanner.scan_paths(paths):
            if item.source_path in self._known_sources:
                continue
            self._known_sources.add(item.source_path)
            self.items.append(item)
            added.append(item)
        return added

    def remove_ids(self, item_ids: set[str]) -> list[QueueItem]:
        removed: list[QueueItem] = []
        remaining: list[QueueItem] = []
        for item in self.items:
            if item.item_id in item_ids:
                removed.append(item)
                self._known_sources.discard(item.source_path)
            else:
                remaining.append(item)
        self.items = remaining
        return removed

    def clear(self) -> None:
        self.items.clear()
        self._known_sources.clear()

    def convertable_items(self) -> list[QueueItem]:
        return [item for item in self.items if item.status in {FileStatus.PENDING, FileStatus.FAILED}]

    def first_output_dir(self) -> Path | None:
        for item in self.items:
            if item.output_pdf:
                return item.output_pdf.parent
        for item in self.items:
            return item.output_dir
        return None
