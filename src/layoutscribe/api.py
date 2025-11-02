"""Public async API entrypoints.

Responsibilities:
- Expose high-level async functions for parsing documents, matching the
  API contract in `docs/API_SPEC.md`.
- Translate user-facing parameters into internal config and agent graph
  execution.
- Return Pydantic models (ParsedDocument).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .agents.graph import run_pipeline
from .types import ParsedDocument, DocumentLayout, DocumentMetadata
from .utils.io import export_outputs


async def parse(
  path: str,
  outputs: List[str],
  llm: str,
  llm_params: Optional[Dict[str, Any]] = None,
  dpi: int = 180,
  parallel_pages: int = 6,
  trace_mlflow: bool = False,
  provider_concurrency: Optional[int] = None,
  budget_usd: Optional[float] = None,
  pages_spec: Optional[str] = None,
  save_overlays: bool = False,
  save_intermediate: bool = False,
  cost_per_page_usd: float = 0.02,
  output_dir: Optional[Path] = None,
) -> ParsedDocument:
  config: Dict[str, Any] = {
    "path": path,
    "outputs": outputs,
    "llm": llm,
    "llm_params": llm_params or {"temperature": 0},
    "dpi": dpi,
    "parallel_pages": parallel_pages,
    "trace_mlflow": trace_mlflow,
    "provider_concurrency": provider_concurrency,
    "budget_usd": budget_usd,
    "pages_spec": pages_spec,
    "save_overlays": save_overlays or trace_mlflow,
    "save_intermediate": save_intermediate,
    "cost_per_page_usd": cost_per_page_usd,
  }
  artifacts = await run_pipeline(config)
  
  markdown = artifacts.get("markdown") if "markdown" in outputs else None
  text = artifacts.get("text") if "text" in outputs else None
  layout_json = DocumentLayout(pages=[]) if "layout_json" in outputs else None
  if layout_json and artifacts.get("pages"):
    layout_json = DocumentLayout.model_validate({"pages": artifacts["pages"]})
  metadata = None
  if artifacts.get("metadata"):
    metadata = DocumentMetadata.model_validate(artifacts["metadata"])
  overlays_dir = artifacts.get("overlays_dir") if "layout_json" in outputs else None
  intermediate_dir = artifacts.get("intermediate_dir") if save_intermediate else None
  parsed = ParsedDocument(
    markdown=markdown,
    text=text,
    layout_json=layout_json,
    overlays_dir=overlays_dir,
    intermediate_dir=intermediate_dir,
    metadata=metadata,
  )

  if output_dir:
    manifest = export_outputs(
      parsed,
      outputs=outputs,
      target_dir=Path(output_dir),
      save_overlays=save_overlays,
      save_intermediate=save_intermediate,
    )
    parsed.artifact_paths = manifest

  return parsed


