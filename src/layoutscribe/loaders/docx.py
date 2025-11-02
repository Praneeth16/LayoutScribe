"""DOCX page rendering via python-docx and Pillow (approximate).

For MVP, we approximate page rendering by laying out paragraphs onto a
blank canvas using a default font. This is a placeholder and will be
iterated for fidelity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from PIL import Image


@dataclass(frozen=True)
class RenderedDocxPage:
  index0: int
  image_path: Path
  width_px: int
  height_px: int
  text: str = ""


def render_docx_to_images(path: Path, dpi: int, temp_dir: Path) -> List[RenderedDocxPage]:
  try:
    import docx  # python-docx
  except Exception as exc:  # pragma: no cover
    raise RuntimeError("python-docx is required to handle DOCX files") from exc

  document = docx.Document(path.as_posix())
  paragraphs = [p.text for p in document.paragraphs if p.text]
  doc_text = "\n".join(paragraphs).strip()

  # Placeholder: render single-page white image sized to A4 at given DPI
  # A4: 8.27 x 11.69 inches
  width_px = int(8.27 * dpi)
  height_px = int(11.69 * dpi)
  img = Image.new("RGB", (width_px, height_px), color=(255, 255, 255))
  out_path = temp_dir / "page-0001.png"
  img.save(out_path.as_posix(), format="PNG")
  return [
    RenderedDocxPage(
      index0=0,
      image_path=out_path,
      width_px=width_px,
      height_px=height_px,
      text=doc_text,
    )
  ]


