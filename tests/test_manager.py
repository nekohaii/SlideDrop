from pathlib import Path

from slidedrop.manager import ConversionManager


def test_manager_prevents_duplicate_queue_items(tmp_path: Path) -> None:
    deck = tmp_path / "deck.pptx"
    deck.write_bytes(b"PK")
    manager = ConversionManager()

    first = manager.add_paths([deck])
    second = manager.add_paths([deck])

    assert len(first) == 1
    assert second == []
    assert len(manager.items) == 1


def test_output_folder_prefers_created_pdf_parent(tmp_path: Path) -> None:
    deck = tmp_path / "deck.pptx"
    pdf = tmp_path / "out" / "deck.pdf"
    deck.write_bytes(b"PK")
    manager = ConversionManager()
    item = manager.add_paths([deck])[0]
    item.output_pdf = pdf

    assert manager.first_output_dir() == pdf.parent
