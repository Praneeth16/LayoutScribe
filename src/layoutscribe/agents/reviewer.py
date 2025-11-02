"""Reviewer node.

Responsibilities:
- Validate page-level JSON against the formal schema and geometry rules.
- Perform overlap and coverage checks and decide on targeted re-asks.
- Aggregate page outputs into final document artifacts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from jsonschema import Draft202012Validator

from ..layout.validate import geometry_checks


def review_page(page: Dict[str, Any], validator: Draft202012Validator) -> List[str]:
  errs: List[str] = []
  for error in validator.iter_errors(page):
    errs.append(error.message)
  errs.extend(geometry_checks(page.get("blocks", [])))
  return errs


def needs_reask(errors: List[str]) -> bool:
  if not errors:
    return False
  # Trigger re-ask on schema invalidation or overlap issues
  return any("overlap" in e.lower() or "required" in e.lower() or "bbox" in e.lower() for e in errors)


