# Prompts & JSON Schema

## Page Schema (Formal)

See the canonical JSON Schema at: `docs/schema/layout_page.schema.json` (Draft 2020-12). LLM outputs must validate against this schema after each page.

### Types
`title | heading | paragraph | list_item | table | figure | equation | caption | footer | header`

### BBox Rules
- Normalized `[x0, y0, x1, y1]` in page coordinates.
- `0 ≤ x0 < x1 ≤ 1`, `0 ≤ y0 < y1 ≤ 1`.
- Min width/height 0.01 for text blocks unless tiny caption.

### Overlap & Coverage (Reviewer Policy)
- Avoid large overlaps (`IoU > 0.3`) except caption↔figure pairs.
- Aim for coverage of all visible text regions.
- If coverage is low or overlap is high, the Reviewer issues a targeted re-ask for the affected regions only.

## System Prompt (Outline)
The system/user instruction given to the vision model (summarized):

- You are a precise document layout and text extraction assistant.
- Return ONLY JSON (no prose/markdown) with fields: `page_number`, `width_px`, `height_px`, and `blocks`.
- Extract ALL visible text; preserve reading order (top→bottom, left→right).
- Normalize `bbox` to page coordinates in [0,1].
- Headings include `level` (1–6) based on prominence; lists use `list_item`; tables include `table.rows`.
- No hallucinations: only include text visible in the image.

Example skeleton:

```json
{
  "page_number": 1,
  "width_px": 1275,
  "height_px": 1650,
  "blocks": [
    {
      "id": "b1",
      "type": "heading",
      "bbox": [0.08, 0.05, 0.92, 0.11],
      "text": "Introduction",
      "level": 1,
      "conf": 0.95
    },
    {
      "id": "b2",
      "type": "table",
      "bbox": [0.10, 0.40, 0.90, 0.62],
      "text": "",
      "table": { "rows": [["A","B"],["1","2"]] },
      "conf": 0.90
    }
  ]
}
```

## Re-ask Prompt (Reviewer)
- Triggered on schema invalidation, high overlap, or low coverage.
- Contains explicit fixes to apply:
  - Normalize bbox ranges to [0,1]; reduce IoU ≤ 0.3 (except caption↔figure pairs).
  - Ensure all visible text regions are covered; add missing blocks.
  - Include required fields per block; add `level` for headings; `rows` for tables.
- Abort re-ask if budget guard indicates insufficient remaining budget.

## Fallback Policy
- If, after validation and a single re-ask, a page still contains no usable blocks, the system injects a fallback paragraph block with the page’s raw text (from renderer) to prevent blank Markdown output.
