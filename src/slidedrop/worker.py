from __future__ import annotations

import threading
from collections.abc import Callable, Sequence

from .converter import LibreOfficeConverter
from .models import FileStatus, QueueItem


ProgressCallback = Callable[[QueueItem, int, int], None]
LogCallback = Callable[[str], None]
DoneCallback = Callable[[int, int], None]


class ConversionWorker:
    def __init__(
        self,
        items: Sequence[QueueItem],
        converter: LibreOfficeConverter,
        high_quality: bool,
        on_progress: ProgressCallback,
        on_log: LogCallback,
        on_done: DoneCallback,
    ) -> None:
        self.items = list(items)
        self.converter = converter
        self.high_quality = high_quality
        self.on_progress = on_progress
        self.on_log = on_log
        self.on_done = on_done
        self._thread: threading.Thread | None = None
        self._cancel_requested = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._thread = threading.Thread(target=self._run, name="SlideDropConversionWorker", daemon=True)
        self._thread.start()

    def cancel(self) -> None:
        self._cancel_requested.set()

    def _run(self) -> None:
        total = len(self.items)
        success_count = 0
        failure_count = 0

        for index, item in enumerate(self.items, start=1):
            if self._cancel_requested.is_set():
                self.on_log("Conversion cancelled.")
                break

            item.status = FileStatus.CONVERTING
            item.message = "Converting"
            self.on_progress(item, index - 1, total)
            self.on_log(f"Converting: {item.source_path}")

            result = self.converter.convert(item, high_quality=self.high_quality)
            if result.success:
                item.status = FileStatus.DONE
                item.output_pdf = result.output_pdf
                item.message = result.message
                success_count += 1
                self.on_log(result.message)
            else:
                item.status = FileStatus.FAILED
                item.message = result.message
                failure_count += 1
                self.on_log(f"Failed: {item.source_path.name} - {result.message}")

            if result.stderr:
                self.on_log(f"LibreOffice stderr: {result.stderr}")
            elif result.stdout:
                self.on_log(f"LibreOffice: {result.stdout}")

            self.on_progress(item, index, total)

        self.on_done(success_count, failure_count)
