# Benchmarks

## Datasets (micro-splits)
- **DocLayNet** — diverse docs with human layout labels.
- **PubLayNet** — standard layout categories (title, text, list, table, figure).
- **PubTables-1M (subset)** — table detection; light structure checks.
- **Synthetic Office Set** — 10 PPTX + 10 DOCX with known structure; export to PDF.

> We do not evaluate OCR accuracy in MVP (LLM-only, no OCR ground truth).

## Metrics
- **Layout detection**
  - IoU@0.5 / 0.75 / 0.9 per class
  - Macro precision/recall/F1
  - Coverage (%) & max-overlap penalties
- **Markdown structure**
  - Heading ladder correctness (strict/relaxed)
  - List preservation rate
  - Table shape accuracy (rows×cols) & header detection rate
- **Ops**
  - Latency per page & total
  - Token usage & cost (if available from provider)

## MLflow Logging
- Params: model id, dpi, concurrency, tiling, temperature.
- Metrics: the above.
- Artifacts: `layout.json`, `document.md`, sample page overlays.

## How to Run (planned)

```
python scripts/run_benchmark.py \
  --dataset doclaynet:tiny \
  --llm openai/gpt-4o \
  --dpi 180 \
  --parallel-pages 6 \
  --trace-mlflow
```
