"""LangGraph graph assembly.

Responsibilities:
- Define the high-level graph: planner → page_vision (fan-out) → composer → reviewer.
- Manage concurrency and provider-specific semaphores.
- Expose a callable/async interface consumed by `api.py`.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.io import create_temp_dir
from ..utils.images import RenderedPage, render_pdf_to_images, pdf_num_pages
from ..loaders.pptx import render_pptx_to_images
from ..loaders.docx import render_docx_to_images
from ..layout.validate import build_default_validator
from ..types import DocumentMetadata, PageMetadata
from .page_vision import run_page_vision
from .reviewer import review_page, needs_reask
from .composer import compose_outputs
from .planner import plan
from ..utils.overlays import draw_overlays
from ..utils.cost import should_abort_budget


async def run_pipeline(config: Dict[str, Any]) -> Dict[str, Any]:
  """Run the end-to-end pipeline and return artifacts."""
  input_path = Path(config["path"]).resolve()
  dpi = int(config.get("dpi", 180))
  pages_spec: Optional[str] = config.get("pages_spec")
  model_id = config["llm"]
  temperature = config.get("llm_params", {}).get("temperature", 0.0)
  provider_concurrency = config.get("provider_concurrency")
  save_overlays = bool(config.get("save_overlays"))
  save_intermediate = bool(config.get("save_intermediate"))
  cost_per_page_usd = float(config.get("cost_per_page_usd", 0.0))
  budget_usd = config.get("budget_usd")

  selected_pages: Optional[List[int]] = None
  if input_path.suffix.lower() == ".pdf" and pages_spec:
    total = pdf_num_pages(input_path)
    sel: List[int] = []
    for part in pages_spec.split(","):
      part = part.strip()
      if not part:
        continue
      if "-" in part:
        s, e = part.split("-", 1)
        a, b = int(s), int(e)
        if a > b:
          a, b = b, a
        sel.extend([p for p in range(a, b + 1) if 1 <= p <= total])
      else:
        p = int(part)
        if 1 <= p <= total:
          sel.append(p)
    selected_pages = sorted(set(sel))

  tmp = create_temp_dir()
  rendered: List[RenderedPage] = []
  suffix = input_path.suffix.lower()
  if suffix == ".pdf":
    rendered = render_pdf_to_images(input_path, dpi, tmp, selected_pages)
  elif suffix == ".pptx":
    slides = render_pptx_to_images(input_path, dpi, tmp)
    rendered = [
      RenderedPage(
        index0=s.index0,
        image_path=s.image_path,
        width_px=s.width_px,
        height_px=s.height_px,
        text=s.text,
      )
      for s in slides
    ]
  elif suffix == ".docx":
    pages = render_docx_to_images(input_path, dpi, tmp)
    rendered = [
      RenderedPage(
        index0=p.index0,
        image_path=p.image_path,
        width_px=p.width_px,
        height_px=p.height_px,
        text=p.text,
      )
      for p in pages
    ]
  else:
    rendered = []

  # Load schema validator from packaged resources
  validator = build_default_validator()

  # Run vision for each page with optional provider semaphore
  semaphore = None
  if isinstance(provider_concurrency, int) and provider_concurrency > 0:
    semaphore = asyncio.Semaphore(provider_concurrency)
  tasks = [
    run_page_vision(
      rp.image_path,
      model_id,
      rp.width_px,
      rp.height_px,
      temperature,
      reask=False,
      semaphore=semaphore,
    )
    for rp in rendered
  ]
  pages_json: List[Dict[str, Any]] = await asyncio.gather(*tasks)
  current_spend = cost_per_page_usd * len(pages_json)

  # Validate pages and collect errors (non-blocking for MVP)
  for idx, page in enumerate(pages_json):
    errs = review_page(page, validator)
    if needs_reask(errs):
      if should_abort_budget(current_spend, budget_usd):
        break
      # Targeted re-ask once per page for MVP
      page = await run_page_vision(
        rendered[idx].image_path,
        model_id,
        rendered[idx].width_px,
        rendered[idx].height_px,
        temperature,
        reask=True,
        semaphore=semaphore,
      )
      # Re-validate
      errs2 = review_page(page, validator)
      pages_json[idx] = page if len(errs2) <= len(errs) else pages_json[idx]
      current_spend += cost_per_page_usd
      if should_abort_budget(current_spend, budget_usd):
        break

  # Fallback: inject plain-text blocks when LLM returns empty content
  for idx, rp in enumerate(rendered):
    if idx >= len(pages_json):
      break
    page = pages_json[idx]
    blocks = page.get("blocks") or []
    has_text = any((block.get("text") or "").strip() for block in blocks)
    fallback_text = (rp.text or "").strip()
    if (not has_text) and fallback_text:
      page.setdefault("blocks", []).append(
        {
          "id": f"fallback-{idx+1}",
          "type": "paragraph",
          "bbox": [0.0, 0.0, 1.0, 1.0],
          "text": fallback_text,
          "conf": None,
        }
      )
      blocks = page["blocks"]
    if not page.get("page_number"):
      page["page_number"] = idx + 1
    if not page.get("width_px"):
      page["width_px"] = rp.width_px
    if not page.get("height_px"):
      page["height_px"] = rp.height_px
    pages_json[idx] = page

  # Compose outputs
  composed = compose_outputs(pages_json)

  overlays_dir_path: Optional[Path] = None
  if save_overlays:
    overlays_dir_path = tmp / "overlays"
    for rp, page in zip(rendered, pages_json):
      out = overlays_dir_path / f"page-{page['page_number']:04d}.png"
      try:
        draw_overlays(rp.image_path, page, out)
      except Exception:
        pass

  intermediate_dir_path: Optional[Path] = None
  if save_intermediate:
    intermediate_dir_path = tmp / "intermediate"
    intermediate_dir_path.mkdir(parents=True, exist_ok=True)
    for page in pages_json:
      page_path = intermediate_dir_path / f"page-{page['page_number']:04d}.json"
      try:
        with page_path.open("w", encoding="utf-8") as f:
          json.dump(page, f, indent=2)
      except Exception:
        pass

  metadata = _build_metadata(pages_json)

  return {
    "pages": pages_json,
    "markdown": composed["markdown"],
    "text": composed["text"],
    "overlays_dir": overlays_dir_path.as_posix() if overlays_dir_path else None,
    "intermediate_dir": intermediate_dir_path.as_posix() if intermediate_dir_path else None,
    "metadata": metadata.model_dump() if metadata else None,
  }


def _build_metadata(pages: List[Dict[str, Any]]) -> DocumentMetadata:
  page_meta: List[PageMetadata] = []
  blocks_total = 0
  tables_total = 0
  for page in pages:
    blocks = page.get("blocks", []) or []
    block_count = len(blocks)
    table_count = sum(1 for b in blocks if b.get("type") == "table")
    blocks_total += block_count
    tables_total += table_count
    preview_text = ""
    for block in blocks:
      text = (block.get("text") or "").strip()
      if text:
        preview_text = text[:200]
        break
    page_meta.append(
      PageMetadata(
        page_number=page.get("page_number", len(page_meta) + 1),
        block_count=block_count,
        table_count=table_count,
        text_preview=preview_text,
      )
    )
  return DocumentMetadata(
    page_count=len(page_meta),
    blocks_total=blocks_total,
    table_total=tables_total,
    pages=page_meta,
  )


