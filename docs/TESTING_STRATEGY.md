# Testing Strategy (No Code)

## Levels
- **Contract tests**: validate JSON schema against sample model outputs.
- **Golden tests**: small synthetic Office docs → assert heading ladder, list items, table shapes.
- **Integration tests**: 3–5 pages per modality (PDF/PPTX/DOCX) → ensure non-empty blocks & valid bboxes.
- **Resilience tests**: simulate provider 429/5xx to ensure retries & backoff.

## What We Won’t Test (MVP)
- OCR text accuracy (not in scope).
- Full table structure fidelity beyond shape checks.

## Tooling
 - `pytest` / `pytest-asyncio`
 - JSON Schema validation using `jsonschema`

## How to Run (planned)

```
pytest -q

# Validate sample outputs against schema
python scripts/validate_schema.py examples/outputs/layout.json docs/schema/layout_page.schema.json
```
