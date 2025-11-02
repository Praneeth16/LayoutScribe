# CLI Specification (No Code)

## Command
```
layoutscribe parse <input_path>   --llm <model_id>   --outputs markdown layout_json text   --dpi 180   --parallel-pages 6   --trace-mlflow
```

## Flags
- `--llm`: LiteLLM model id (e.g., `openai/gpt-4o`, `azure/gpt-4o`, `anthropic/claude-3.5-sonnet`, `google/gemini-1.5-pro`)
- `--outputs`: one or more of `markdown`, `text`, `layout_json` (repeat flag or use comma-separated list)
- `--output-dir`: where to save artifacts (default: `./artifacts/<basename>`)
- `--pages`: page selection (e.g., `1-3,7,10`)
- `--dpi`: render DPI (default 180)
- `--parallel-pages`: async concurrency cap (default 6)
- `--provider-concurrency`: override provider-specific semaphore
- `--trace-mlflow`: enable MLflow run (off by default)
- `--budget-usd`: stop if estimated cost exceeds budget
- `--save-overlays`: save bbox overlays for sampled pages
- `--save-intermediate`: persist intermediate JSON from PageVision
- `--cost-per-page-usd`: estimated cost per processed page (used for budget guard)
- `--preview-chars`: characters to display per preview in stdout (0 disables previews)
- `--format`: alias for `--outputs` (`all|markdown|text|layout_json`, accepts comma-separated aliases)
- `--quiet` / `--verbose`: control logging verbosity

## Exit Codes
- `0` success
- `2` validation error (schema/geometry)
- `3` provider error (auth/rate limit)
- `4` budget exceeded
- `5` rendering error (input unreadable/unsupported)

## Examples

```
# Parse a PDF to all formats with default model
layoutscribe parse ./samples/report.pdf \
  --llm openai/gpt-4o \
  --outputs markdown text layout_json \
  --output-dir ./artifacts/report

# Parse specific pages with budget cap and overlays
layoutscribe parse ./samples/slides.pdf \
  --llm openai/gpt-4o \
  --pages 1-3,7 \
  --budget-usd 0.50 \
  --save-overlays --trace-mlflow
```

## Output Artifacts (typical)

```
./artifacts/report/
  document.md
  document.txt
  layout.json
  overlays/
    page-0001.png
    page-0002.png
```

The CLI prints a summary (page count, block/table totals) and optional previews of the requested outputs in stdout for quick inspection.
