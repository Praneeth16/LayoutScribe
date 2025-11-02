# Architecture

## High-Level Flow
1. **Planner**  
   - Detect file type; count pages/slides; choose DPI.
   - Build page queue with metadata.

2. **Rendering**  
   - PDF → PNG via PyMuPDF; PPTX/DOCX → PNG via python-pptx/python-docx placeholders.
   - Collect per-page text (when available) for fallback.

3. **PageVision (async fan-out)**  
   - Send page image + strict instruction to a vision LLM via LiteLLM.
   - Expect schema-conformant JSON blocks: `{id, type, bbox[0..1], text, level?, conf, table?}`.

4. **Reviewer (validate / re-ask)**  
   - JSON Schema validation, bbox normalization checks, overlap (IoU) and coverage.
   - On violations: issue targeted **re-ask** with explicit fixes; respect budget guard.

5. **Fallback Injection**  
   - If a page is still empty after re-ask, inject a single paragraph block using the rendered page text to avoid blank Markdown.

6. **Composer**  
   - Convert validated blocks → **Markdown** + **plain text** using reading order heuristics; basic tables.

7. **Artifacts & Tracing**  
   - Save `document.md`, `document.txt`, `layout.json`, optional overlays and intermediate JSON.
   - Optionally log parameters, metrics, and artifacts to **MLflow**.

## Modules (Current)
```
src/
  layoutscribe/
    api.py                 # Async public entrypoints
    cli.py                 # CLI wrapper
    config.py              # Pydantic settings
    types.py               # Pydantic models (Block, PageLayout, ParsedDocument)
    llm/
      router.py            # LiteLLM provider routing
      prompts.py           # JSON schema & instruction templates
    agents/
      graph.py             # Orchestration: planner → page_vision → reviewer → composer
      planner.py
      page_vision.py
      composer.py
      reviewer.py
    layout/
      compose.py           # JSON → Markdown/Text
      validate.py          # Schema & geometry checks
    tracing/
      mlflow_logger.py     # Run params, metrics, artifacts
    loaders/
      pptx.py              # PPTX → images (with extracted slide text)
      docx.py              # DOCX → images (with extracted doc text)
    utils/
      images.py            # Rendering, DPI, tiling helpers (no OCR)
      io.py                # Paths, temp dirs, artifact saves
      backoff.py           # Retry policies
      cost.py              # Token/cost accounting (optional)
      overlays.py          # Bounding-box overlay visualizations
    schema/
      layout_page.schema.json
```

## Data Contracts
- See **PROMPTS_AND_SCHEMA.md** for JSON schema.
- BBoxes normalized: `[x0, y0, x1, y1]` with `0 ≤ x0 < x1 ≤ 1`, `0 ≤ y0 < y1 ≤ 1`.
- Block `type ∈ {title, heading, paragraph, list_item, table, figure, equation, caption, footer, header}`.

## Concurrency & Retries
- Async batch per page with a provider-specific semaphore.
- Retry: exponential backoff + jitter on 429/5xx/timeouts.
- Hard budget guard (optional) to cap spend per run.

## Control Flow (Mermaid)

```
flowchart TD
  A[Planner] --> B[Render pages → PNG]
  B --> C[PageVision (async via LiteLLM)]
  C --> D[Validate: schema + geometry]
  D -->|invalid| C2[Re-ask with targeted hints]
  D -->|valid| E[Fallback inject text if empty]
  C2 --> D
  E --> F[Compose Markdown/Text]
  F --> G[Artifacts (md, txt, json, overlays, intermediate)]
```

## Prompt Contract (Summary)
- Extract ALL visible text; preserve reading order.
- Return ONLY JSON; no prose/markdown.
- Normalize bboxes `[x0,y0,x1,y1]` to [0,1].
- Headings include `level` (1–6). Tables include `rows`.
- No hallucinations; only text present in the image.

## Boundaries
- **Out of scope (0.1)**: OCR engines, handwriting, complex table reconstruction (rowspan/colspan), translation.
