import threading
from pathlib import Path

from slidedrop.engines.options import ConversionOptions
from slidedrop.models import FileStatus, QueueItem
from slidedrop.worker import ConversionWorker

from tests.support.mock_strategy import MockStrategy


def test_conversion_worker_invokes_converter(tmp_path: Path) -> None:
    src = tmp_path / "deck.pptx"
    src.write_bytes(b"PK")
    item = QueueItem(source_path=src, output_dir=tmp_path / "pdf")

    done = threading.Event()
    summary: dict[str, int] = {}

    def on_progress(item: QueueItem, current: int, total: int) -> None:
        _ = item, current, total

    def on_log(text: str) -> None:
        _ = text

    def on_done(success: int, failed: int) -> None:
        summary["success"] = success
        summary["failed"] = failed
        done.set()

    worker = ConversionWorker(
        items=[item],
        converter=MockStrategy(),
        on_progress=on_progress,
        on_log=on_log,
        on_done=on_done,
        conversion_options=ConversionOptions(),
    )
    worker.start()
    assert done.wait(timeout=3)

    assert summary["success"] == 1
    assert summary["failed"] == 0
    assert item.status == FileStatus.DONE
    assert item.output_pdf is not None
