"""Planner node.

Responsibilities:
- Inspect input file, detect type, and gather page/slide counts.
- Decide DPI and prepare a page processing queue.
- Emit planner metadata consumed by PageVision and downstream nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class PageTask:
  index0: int
  source_path: Path
  dpi: int


def plan(input_path: Path, dpi: int, pages: Optional[List[int]] = None) -> List[PageTask]:
  """Plan page tasks for the given input (PDF-only for now)."""
  tasks: List[PageTask] = []
  if pages:
    for p in pages:
      tasks.append(PageTask(index0=p - 1, source_path=input_path, dpi=dpi))
  return tasks


