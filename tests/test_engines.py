from pathlib import Path

from slidedrop.engines.libreoffice import LibreOfficeStrategy
from slidedrop.engines.mock import MockStrategy
from slidedrop.models import QueueItem


def test_mock_strategy_success_creates_non_empty_pdf(tmp_path: Path) -> None:
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"PK")
    item = QueueItem(source_path=source, output_dir=tmp_path / "pdf")

    result = MockStrategy().convert(item)

    assert result.success is True
    assert result.output_pdf is not None
    assert result.output_pdf.exists()
    assert result.output_pdf.stat().st_size > 0


def test_mock_strategy_failure_does_not_create_pdf(tmp_path: Path) -> None:
    source = tmp_path / "deck.pptx"
    source.write_bytes(b"PK")
    item = QueueItem(source_path=source, output_dir=tmp_path / "pdf")

    result = MockStrategy(should_fail=True).convert(item)

    assert result.success is False
    assert result.output_pdf is None


def test_invalid_pdf_cleanup_removes_empty_files(tmp_path: Path) -> None:
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(b"")

    LibreOfficeStrategy._delete_invalid_pdf(pdf)

    assert not pdf.exists()
