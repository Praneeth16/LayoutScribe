"""PageVision node.

Responsibilities:
- Render a single page/slide to an image at the requested DPI.
- Call the configured vision LLM via LiteLLM with instructions and schema constraints.
- Return a page-level layout JSON structure (validated later by Reviewer).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ..llm.prompts import page_vision_instruction, reviewer_reask_hint
from ..llm.router import vision_json_call


async def run_page_vision(
  image_path: Path,
  model_id: str,
  width_px: int,
  height_px: int,
  temperature: float = 0.0,
  reask: bool = False,
  semaphore: Optional["asyncio.Semaphore"] = None,
) -> Dict[str, Any]:
  """Run the vision model on a page image and return layout JSON."""
  import asyncio

  with image_path.open("rb") as f:
    image_bytes = f.read()

  instruction = page_vision_instruction(width_px, height_px)
  if reask:
    instruction = instruction + "\n" + reviewer_reask_hint()

  if semaphore is not None:
    await semaphore.acquire()
  try:
    page_json = await vision_json_call(model_id, image_bytes, instruction, temperature)
  finally:
    if semaphore is not None:
      semaphore.release()
  return page_json


