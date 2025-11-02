"""Overlay image generator for layout JSON.

Draws bounding boxes with class labels and confidence values on page
images. Uses distinct colors per block type and optional label legend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont


PALETTE = {
  "title": (0, 102, 204),
  "heading": (0, 153, 255),
  "paragraph": (0, 153, 0),
  "list_item": (0, 204, 102),
  "table": (204, 102, 0),
  "figure": (204, 0, 0),
  "equation": (153, 0, 153),
  "caption": (102, 102, 102),
  "footer": (153, 153, 153),
  "header": (153, 153, 153),
}


def _color_for(block_type: str) -> Tuple[int, int, int]:
  return PALETTE.get(block_type, (0, 0, 0))


def draw_overlays(
  image_path: Path,
  page_json: Dict[str, Any],
  out_path: Path,
) -> None:
  img = Image.open(image_path).convert("RGB")
  draw = ImageDraw.Draw(img)
  width_px = page_json.get("width_px", img.width)
  height_px = page_json.get("height_px", img.height)

  try:
    font = ImageFont.load_default()
  except Exception:
    font = None  # type: ignore

  for block in page_json.get("blocks", []):
    btype = block.get("type", "unknown")
    label = btype
    if block.get("level"):
      label += f"/{block['level']}"
    if block.get("conf") is not None:
      label += f" ({block['conf']:.2f})"

    x0, y0, x1, y1 = block.get("bbox", [0, 0, 0, 0])
    # convert normalized bbox to pixel coords
    rx0 = int(x0 * width_px)
    ry0 = int(y0 * height_px)
    rx1 = int(x1 * width_px)
    ry1 = int(y1 * height_px)
    color = _color_for(btype)
    draw.rectangle([(rx0, ry0), (rx1, ry1)], outline=color, width=2)
    if font:
      tw, th = draw.textsize(label, font=font)
      draw.rectangle([(rx0, ry0 - th - 2), (rx0 + tw + 4, ry0)], fill=color)
      draw.text((rx0 + 2, ry0 - th - 1), label, fill=(255, 255, 255), font=font)

  out_path.parent.mkdir(parents=True, exist_ok=True)
  img.save(out_path.as_posix(), format="PNG")


