"""Composer node.

Responsibilities:
- Convert page/block graphs into Markdown and plain text.
- Preserve reading order using normalized bounding boxes and block types.
- Handle basic tables and captions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..layout.compose import compose_markdown as _compose_markdown
from ..layout.compose import compose_text as _compose_text


def compose_outputs(pages: List[Dict[str, Any]]) -> Dict[str, str]:
  """Compose Markdown and plain text from page blocks."""
  markdown = _compose_markdown(pages)
  text = _compose_text(pages)
  return {"markdown": markdown, "text": text}


