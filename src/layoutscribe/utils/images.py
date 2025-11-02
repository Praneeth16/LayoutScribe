"""Image rendering helpers.

Responsibilities:
- Provide PDF/PPTX/DOCX to image rendering utilities with DPI.
- Avoid OCR; rendering only. Downstream vision handled by LLM via LiteLLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..exceptions import RenderingError


@dataclass(frozen=True)
class RenderedPage:
  index0: int
  image_path: Path
  width_px: int
  height_px: int
  text: str = ""


def render_pdf_to_images(
  path: Path, dpi: int, temp_dir: Path, selected_pages: Optional[List[int]] = None
) -> List[RenderedPage]:
  """Render a PDF into page images at the given DPI using PyMuPDF.

  selected_pages: 1-based page indices to render; if None, render all pages.
  """
  try:
    import fitz  # PyMuPDF
  except Exception as exc:  # pragma: no cover
    raise RenderingError("PyMuPDF (fitz) is required to render PDFs") from exc

  try:
    doc = fitz.open(path.as_posix())
  except Exception as exc:  # pragma: no cover
    raise RenderingError(f"Failed to open PDF: {path}") from exc

  rendered: List[RenderedPage] = []
  pages_iter = (
    [p - 1 for p in selected_pages if 1 <= p <= len(doc)] if selected_pages else range(len(doc))
  )
  for i in pages_iter:
    page = doc.load_page(i)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    out_path = temp_dir / f"page-{i+1:04d}.png"
    pix.save(out_path.as_posix())
    rendered.append(
      RenderedPage(
        index0=i,
        image_path=out_path,
        width_px=pix.width,
        height_px=pix.height,
        text=(page.get_text("text") or "").strip(),
      )
    )
  doc.close()
  return rendered


def pdf_num_pages(path: Path) -> int:
  try:
    import fitz  # PyMuPDF
  except Exception as exc:  # pragma: no cover
    raise RenderingError("PyMuPDF (fitz) is required to inspect PDFs") from exc
  try:
    doc = fitz.open(path.as_posix())
    n = len(doc)
    doc.close()
    return n
  except Exception as exc:  # pragma: no cover
    raise RenderingError(f"Failed to open PDF: {path}") from exc


def export_office_to_pdf(path: Path) -> Path:
  """Export a PPTX/DOCX file to PDF via a headless tool.

  Placeholder implementation returning the input path unchanged.
  """
  return path


