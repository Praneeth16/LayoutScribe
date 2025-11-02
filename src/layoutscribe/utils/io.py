"""Filesystem and artifact I/O helpers.

Responsibilities:
- Manage temp directories, artifact output paths, and cleanup policies.
- Provide helpers for saving overlays and intermediate JSON when enabled.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List
import json
import tempfile
import shutil

if TYPE_CHECKING:
  from ..types import ParsedDocument


def ensure_dir(path: Path) -> Path:
  path.mkdir(parents=True, exist_ok=True)
  return path


def default_output_dir(input_path: Path) -> Path:
  base = input_path.stem
  return Path("artifacts") / base


def create_temp_dir(prefix: str = "layoutscribe_") -> Path:
  return Path(tempfile.mkdtemp(prefix=prefix))


def write_text(path: Path, content: str) -> None:
  ensure_dir(path.parent)
  with path.open("w", encoding="utf-8") as f:
    f.write(content)


def write_json(path: Path, data: dict) -> None:
  ensure_dir(path.parent)
  with path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


def parse_pages_spec(spec: str, total_pages: int) -> List[int]:
  pages: List[int] = []
  for part in spec.split(","):
    part = part.strip()
    if not part:
      continue
    if "-" in part:
      start_s, end_s = part.split("-", 1)
      start = int(start_s)
      end = int(end_s)
      if start > end:
        start, end = end, start
      for p in range(start, end + 1):
        if 1 <= p <= total_pages:
          pages.append(p)
    else:
      p = int(part)
      if 1 <= p <= total_pages:
        pages.append(p)
  # de-duplicate and sort
  return sorted(set(pages))


def export_outputs(
  doc: "ParsedDocument",
  outputs: List[str],
  target_dir: Path,
  save_overlays: bool = False,
  save_intermediate: bool = False,
) -> Dict[str, List[str]]:
  """Write selected outputs to disk and optionally export overlays/intermediate."""

  ensure_dir(target_dir)
  manifest: Dict[str, List[str]] = {"primary": [], "overlays": [], "intermediate": []}

  if "layout_json" in outputs and doc.layout_json is not None:
    layout_path = target_dir / "layout.json"
    data = doc.layout_json.model_dump() if hasattr(doc.layout_json, "model_dump") else doc.layout_json  # type: ignore[union-attr]
    write_json(layout_path, data)  # type: ignore[arg-type]
    manifest["primary"].append(layout_path.as_posix())

  if "markdown" in outputs and doc.markdown:
    md_path = target_dir / "document.md"
    write_text(md_path, doc.markdown)
    manifest["primary"].append(md_path.as_posix())

  if "text" in outputs and doc.text:
    txt_path = target_dir / "document.txt"
    write_text(txt_path, doc.text)
    manifest["primary"].append(txt_path.as_posix())

  overlay_sources: List[Path] = []
  if doc.overlays_dir:
    overlay_dir = Path(doc.overlays_dir)
    if overlay_dir.exists() and overlay_dir.is_dir():
      overlay_sources = sorted(overlay_dir.glob("*.png"))

  if overlay_sources:
    if save_overlays:
      overlays_target = target_dir / "overlays"
      ensure_dir(overlays_target)
      for src in overlay_sources:
        dest = overlays_target / src.name
        shutil.copy2(src, dest)
        manifest["overlays"].append(dest.as_posix())
    else:
      manifest["overlays"].extend(path.as_posix() for path in overlay_sources)

  intermediate_sources: List[Path] = []
  if doc.intermediate_dir:
    interm_dir = Path(doc.intermediate_dir)
    if interm_dir.exists() and interm_dir.is_dir():
      intermediate_sources = sorted(interm_dir.glob("*.json"))

  if intermediate_sources:
    if save_intermediate:
      intermediate_target = target_dir / "intermediate"
      ensure_dir(intermediate_target)
      for src in intermediate_sources:
        dest = intermediate_target / src.name
        shutil.copy2(src, dest)
        manifest["intermediate"].append(dest.as_posix())
    else:
      manifest["intermediate"].extend(path.as_posix() for path in intermediate_sources)

  return manifest


