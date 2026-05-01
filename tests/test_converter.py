from pathlib import Path
from unittest.mock import MagicMock, patch

import subprocess

from slidedrop.engines.libreoffice import LibreOfficeStrategy
from slidedrop.engines.options import ConversionOptions
from slidedrop.models import QueueItem


def test_libreoffice_strategy_uses_popen_success(tmp_path: Path) -> None:
    soffice = tmp_path / "soffice.exe"
    soffice.write_text("stub", encoding="utf-8")

    src = tmp_path / "deck.pptx"
    src.write_bytes(b"dummy")

    out_dir = tmp_path / "pdf"
    item = QueueItem(source_path=src, output_dir=out_dir)
    expected_pdf = out_dir / "deck.pdf"

    mock_proc = MagicMock()
    mock_proc.returncode = 0

    def _communicate(timeout=None):
        out_dir.mkdir(parents=True, exist_ok=True)
        expected_pdf.write_bytes(b"%PDF\n")
        return "ok", ""

    mock_proc.communicate.side_effect = _communicate

    with patch.object(LibreOfficeStrategy, "validate", return_value=(True, "ok")), patch(
        "slidedrop.engines.libreoffice.subprocess.Popen",
        return_value=mock_proc,
    ):
        engine = LibreOfficeStrategy(soffice)
        result = engine.convert(item, ConversionOptions(timeout_seconds=30))

    assert result.success is True
    assert result.output_pdf == expected_pdf
    assert expected_pdf.stat().st_size > 0


def test_libreoffice_strategy_timeout_returns_failure(tmp_path: Path) -> None:
    soffice = tmp_path / "soffice.exe"
    soffice.write_text("stub", encoding="utf-8")

    src = tmp_path / "deck.pptx"
    src.write_bytes(b"x")

    item = QueueItem(source_path=src, output_dir=tmp_path / "pdf")

    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = subprocess.TimeoutExpired("cmd", timeout=1)

    with patch.object(LibreOfficeStrategy, "validate", return_value=(True, "ok")), patch(
        "slidedrop.engines.libreoffice.subprocess.Popen",
        return_value=mock_proc,
    ):
        engine = LibreOfficeStrategy(soffice)
        result = engine.convert(item, ConversionOptions(timeout_seconds=1))

    assert result.success is False
    assert "Timed out" in result.message
