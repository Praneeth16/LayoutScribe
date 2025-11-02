# LayoutScribe
LLM-powered layout &amp; text extraction for PDFs, slides, and Word docs


[![PyPI Version](https://img.shields.io/pypi/v/layoutscribe.svg)](https://pypi.org/project/layoutscribe/)
[![Python Versions](https://img.shields.io/pypi/pyversions/layoutscribe.svg)](https://pypi.org/project/layoutscribe/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**LLM-only, agentic parser** that converts **PDF / PPTX / DOCX** into clean **Markdown**, **plain text**, and **layout JSON (with normalized bounding boxes)**.  
Built with **LangGraph** (agent orchestration), **LiteLLM** (provider-agnostic multimodal calls), and **MLflow** (tracing).

> No OCR engines, no heuristic parsers. Rendering to images is allowed; all structure and text understanding is done by a **multimodal LLM**.

## Features
- Inputs: PDF, PPTX, DOCX (rendered pages/slides as images)
- Outputs:
  - Markdown (headings, lists, tables, captions)
  - Plain text
  - Layout JSON (`blocks` with `type`, `bbox[0..1]`, `text`, `conf`)
- Agentic pipeline: planner → page_vision (async) → reviewer (validate/re-ask) → composer
- Robustness:
  - Re-ask on schema/geometry violations (IoU/coverage checks)
  - Fallback injection when LLM returns empty content so Markdown is never blank
- Provider-agnostic via LiteLLM (OpenAI, Azure OpenAI, Claude, Gemini)
- MLflow tracing for params, metrics, artifacts

## Status
0.1 (alpha) released — see [CHANGELOG.md](CHANGELOG.md) and [docs/ROADMAP.md](docs/ROADMAP.md).


## Installation

Requires Python 3.10+.

```
pip install layoutscribe
```

Optional extras:

```
# Office file support (PPTX/DOCX rendering via python-pptx / python-docx)
pip install "layoutscribe[office]"

# Development tools (ruff, black, pytest)
pip install "layoutscribe[dev]"
```

Runtime notes:
- PDF rendering: PyMuPDF (included)
- PPTX/DOCX support: `python-pptx`, `python-docx` (install with `[office]`)

## Getting Started

Set provider keys as environment variables (see CONFIGURATION.md). Example `.env`:

```
OPENAI_API_KEY=sk-...
LAYOUTSCRIBE_DPI=180
```

## Quickstart

### CLI

```
layoutscribe parse ./samples/report.pdf \
  --llm openai/gpt-4o \
  --outputs markdown text layout_json \
  --output-dir ./artifacts/report \
  --dpi 180 --parallel-pages 6 --budget-usd 0.50
```

### Python API

```python
import asyncio
from layoutscribe.api import parse as ls_parse


async def main() -> None:
  doc = await ls_parse(
    path="samples/report.pdf",
    outputs=["markdown", "text", "layout_json"],
    llm="openai/gpt-4o",
    dpi=180,
    parallel_pages=6,
    budget_usd=0.50,
    save_intermediate=True,
  )
  print(doc.metadata)
  print(doc.markdown[:1000])


if __name__ == "__main__":
  asyncio.run(main())
```

### Outputs & Artifacts

```
./artifacts/report/
  document.md
  document.txt
  layout.json
  overlays/
    page-0001.png
    page-0002.png
  intermediate/
    page-0001.json
```

## Configuration

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for provider-specific env vars, defaults, and precedence. MLflow tracing is opt-in via `--trace-mlflow`.

### LiteLLM provider setup

LiteLLM reads provider keys from environment variables. Set only those you need:

```
# OpenAI
OPENAI_API_KEY=sk-...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...  
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/  
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Anthropic
ANTHROPIC_API_KEY=...

# Google (Gemini)
GOOGLE_API_KEY=...
```

Use `--llm` to pick a model via LiteLLM:

```
--llm openai/gpt-4o
--llm azure/<deployment_name>
--llm anthropic/claude-3.5-sonnet
--llm google/gemini-1.5-pro
```

Notes:
- For Azure, ensure the deployment name references a vision-capable model and that your endpoint/API version are set.
- Keep temperature low (0–0.2) for consistent JSON.
- Respect provider rate limits; we use retries with exponential backoff.

## Limitations (0.1)

- No OCR engines; relies entirely on a multimodal LLM
- Basic tables only (CSV-like); no complex rowspan/colspan recovery
- No handwriting support; language translation out of scope
- Confidence scores (if present) are heuristic and not calibrated

## Community & Support

- Open issues and discussions on GitHub
- For security concerns, follow SECURITY.md (use private advisories)

## License
Apache-2.0 (see LICENSE).
