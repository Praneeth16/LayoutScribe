"""Validation helpers.

Responsibilities:
- Validate page/block structures against the canonical JSON Schema.
- Perform geometry checks: bbox ranges, overlap thresholds, coverage heuristics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator
import json
from importlib import resources


def load_schema(schema_path: Path) -> Dict[str, Any]:
  with schema_path.open("r", encoding="utf-8") as f:
    return Draft202012Validator.check_schema(__import__("json").load(f)) or __import__(
      "json"
    ).load(schema_path.open("r", encoding="utf-8"))


def validate_page(page: Dict[str, Any], validator: Draft202012Validator) -> List[str]:
  errors: List[str] = []
  for error in validator.iter_errors(page):
    errors.append(error.message)
  return errors


def build_validator(schema_path: Path) -> Draft202012Validator:
  with schema_path.open("r", encoding="utf-8") as f:
    schema = json.load(f)
  Draft202012Validator.check_schema(schema)
  return Draft202012Validator(schema)


def build_default_validator() -> Draft202012Validator:
  """Load the packaged default schema via importlib.resources."""
  schema_file = resources.files("layoutscribe.schema").joinpath("layout_page.schema.json")
  with schema_file.open("r", encoding="utf-8") as f:
    schema = json.load(f)
  Draft202012Validator.check_schema(schema)
  return Draft202012Validator(schema)


def iou(b1: List[float], b2: List[float]) -> float:
  x0 = max(b1[0], b2[0])
  y0 = max(b1[1], b2[1])
  x1 = min(b1[2], b2[2])
  y1 = min(b1[3], b2[3])
  inter_w = max(0.0, x1 - x0)
  inter_h = max(0.0, y1 - y0)
  inter = inter_w * inter_h
  if inter == 0:
    return 0.0
  area1 = max(0.0, b1[2] - b1[0]) * max(0.0, b1[3] - b1[1])
  area2 = max(0.0, b2[2] - b2[0]) * max(0.0, b2[3] - b2[1])
  union = area1 + area2 - inter
  if union <= 0:
    return 0.0
  return inter / union


def geometry_checks(blocks: List[Dict[str, Any]], overlap_iou_threshold: float = 0.3) -> List[str]:
  errs: List[str] = []
  for b in blocks:
    x0, y0, x1, y1 = b.get("bbox", [0, 0, 0, 0])
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
      errs.append(f"invalid bbox range for block {b.get('id')}")
  for i in range(len(blocks)):
    for j in range(i + 1, len(blocks)):
      if iou(blocks[i]["bbox"], blocks[j]["bbox"]) > overlap_iou_threshold:
        errs.append(
          f"overlap above threshold between {blocks[i].get('id')} and {blocks[j].get('id')}"
        )
  return errs


