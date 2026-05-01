from pathlib import Path

from slidedrop.services.convert_meta import load_meta, meta_matches, meta_path_for_pdf, save_meta
from slidedrop.services.hashing import sha256_file


def test_meta_roundtrip_matches(tmp_path: Path) -> None:
    src = tmp_path / "src.pptx"
    src.write_bytes(b"abc")
    pdf = tmp_path / "deck.pdf"
    pdf.write_bytes(b"dummy")

    sha = sha256_file(src)
    size = src.stat().st_size

    save_meta(pdf, sha, size)

    assert meta_path_for_pdf(pdf).exists()
    record = load_meta(pdf)
    assert record is not None
    assert meta_matches(record, sha, size)
