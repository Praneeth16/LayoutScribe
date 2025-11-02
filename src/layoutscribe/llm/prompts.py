"""Prompt templates and schema hints.

Responsibilities:
- Define system and user prompts for PageVision and Reviewer.
- Include concise instructions enforcing the JSON schema contract.
- Provide re-ask templates referencing specific overlap/coverage issues.
"""

from __future__ import annotations


def page_vision_instruction(width_px: int, height_px: int) -> str:
  return f"""You are a precise document layout and text extraction assistant.

Analyze the provided page image and extract ALL visible text with its structure.

Return a JSON object with this exact schema:

{{
  "page_number": 1,
  "width_px": {width_px},
  "height_px": {height_px},
  "blocks": [
    {{
      "id": "b1",
      "type": "<one of: title, heading, paragraph, list_item, table, figure, equation, caption, footer, header>",
      "bbox": [x0, y0, x1, y1],
      "text": "extracted text here",
      "level": 1,
      "table": {{"rows": [["H1","H2"],["v1","v2"]]}},
      "conf": 0.95
    }}
  ]
}}

CRITICAL RULES:
1. Extract ALL visible text from the image - do not skip any text regions
2. bbox coordinates MUST be normalized [x0, y0, x1, y1] where 0 ≤ x0 < x1 ≤ 1, 0 ≤ y0 < y1 ≤ 1
3. For headings: include "level" (1-6) based on font size/weight
4. For tables: include "table" with "rows" array of string arrays
5. For list items: use type "list_item" for bulleted/numbered items
6. Preserve reading order (typically top-to-bottom, left-to-right)
7. Return ONLY valid JSON - no markdown, no prose, no explanations
8. Do not invent text - only include what you can see in the image
9. Each block MUST have: id (unique), type, bbox, and text (except for figure/equation where text is optional)
10. Use "title" for document titles, "heading" for section headers, "paragraph" for body text

Return the complete JSON now."""


def reviewer_reask_hint() -> str:
  return """
VALIDATION FAILED. Please fix:
- Ensure all bbox values are normalized (0-1 range)
- Reduce block overlaps (IoU should be ≤0.3 except caption+figure pairs)
- Cover ALL visible text regions - do not miss any text
- Ensure each block has required fields: id, type, bbox
- For headings: include "level" field
- For tables: include "table" field with valid "rows"

Return the corrected JSON."""


