from pathlib import Path

from slidedrop.scanner import FileScanner


def test_scan_folder_finds_powerpoint_files(tmp_path: Path) -> None:
    (tmp_path / "deck.pptx").write_bytes(b"PK")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")

    items = FileScanner().scan_folder(tmp_path)

    assert [item.source_path.name for item in items] == ["deck.pptx"]
    assert items[0].output_dir == tmp_path / "pdf"


def test_scan_paths_deduplicates_same_file(tmp_path: Path) -> None:
    deck = tmp_path / "deck.ppt"
    deck.write_bytes(b"\xd0\xcf\x11\xe0")

    items = FileScanner().scan_paths([deck, deck])

    assert len(items) == 1
    assert items[0].source_path == deck.resolve()
