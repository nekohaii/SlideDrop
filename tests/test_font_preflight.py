import zipfile
from pathlib import Path

from slidedrop.services.font_preflight import missing_fonts_for_presentation


def test_missing_fonts_detects_unknown_faces(tmp_path: Path, monkeypatch) -> None:
    pptx = tmp_path / "deck.pptx"
    slide_xml = """<?xml version="1.0"?>
<a:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <a:cSld><a:spTree>
    <a:sp>
      <a:txBody>
        <a:p><a:r><a:rPr latin="TotallyMissingFontZZ"/></a:r></a:p>
      </a:txBody>
    </a:sp>
  </a:spTree></a:cSld>
</a:sld>
"""
    with zipfile.ZipFile(pptx, "w") as zf:
        zf.writestr("ppt/slides/slide1.xml", slide_xml.encode("utf-8"))

    monkeypatch.setattr(
        "slidedrop.services.font_preflight._installed_font_names_lowercase",
        lambda: {"arial"},
    )

    missing = missing_fonts_for_presentation(pptx)
    assert "TotallyMissingFontZZ" in missing
