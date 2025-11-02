"""Composition helpers.

Responsibilities:
- Convert validated layout JSON into Markdown and plain text.
- Provide formatting rules for headings, lists, tables, and captions.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def compose_markdown(pages: List[Dict[str, Any]]) -> str:
  """Compose Markdown from page blocks."""
  lines: List[str] = []
  for page in pages:
    blocks = page.get("blocks", []) or []
    sorted_blocks = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))
    for block in sorted_blocks:
      btype = block.get("type", "paragraph")
      text = (block.get("text") or "").strip()
      if btype == "title":
        lines.append(f"# {text}")
      elif btype == "heading":
        level = max(1, min(6, block.get("level", 1)))
        lines.append(f"{'#' * level} {text}")
      elif btype == "paragraph":
        if text:
          lines.append(text)
      elif btype == "list_item":
        lines.append(f"- {text}")
      elif btype == "table":
        table_rows = block.get("table", {}).get("rows", []) or []
        lines.extend(_table_to_markdown(table_rows))
      elif btype == "caption":
        lines.append(f"*{text}*")
      elif btype in {"footer", "header"}:
        if text:
          lines.append(f"_{text}_")
      else:
        if text:
          lines.append(text)
    lines.append("---")
  return "\n".join(_squash_blank(lines))


def compose_text(pages: List[Dict[str, Any]]) -> str:
  """Compose plain text from page blocks."""
  lines: List[str] = []
  for page in pages:
    blocks = page.get("blocks", []) or []
    sorted_blocks = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))
    for block in sorted_blocks:
      btype = block.get("type", "paragraph")
      if btype == "table":
        rows = block.get("table", {}).get("rows", []) or []
        for row in rows:
          lines.append(" | ".join(cell.strip() for cell in row))
      else:
        text = (block.get("text") or "").strip()
        if text:
          lines.append(text)
    lines.append("---")
  return "\n".join(_squash_blank(lines))


def _table_to_markdown(rows: List[List[str]]) -> List[str]:
  if not rows:
    return []
  header = rows[0]
  body = rows[1:] or []
  col_count = len(header)

  def _normalize(row: List[str]) -> List[str]:
    padded = row + [""] * max(0, col_count - len(row))
    return [cell.strip() for cell in padded[:col_count]]

  header_norm = _normalize(header)
  markdown_rows = ["| " + " | ".join(header_norm) + " |"]
  markdown_rows.append("| " + " | ".join(["---"] * col_count) + " |")
  for row in body:
    markdown_rows.append("| " + " | ".join(_normalize(row)) + " |")
  markdown_rows.append("")
  return markdown_rows


def _squash_blank(lines: Iterable[str]) -> List[str]:
  squashed: List[str] = []
  for line in lines:
    if not line:
      if squashed and not squashed[-1]:
        continue
      squashed.append("")
    else:
      squashed.append(line)
  # trim trailing blanks
  while squashed and not squashed[-1]:
    squashed.pop()
  return squashed


