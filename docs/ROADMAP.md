# Roadmap

## MVP (Weekend)
- LLM-only parsing for PDF.
- Minimal PPTX/DOCX via headless export to images.
- OpenAI provider via LiteLLM.
- JSON schema + Markdown composer.
- MLflow tracing.
- Micro-benchmark run with DocLayNet/PubLayNet samples.

## Next (Week 1–2)
- Add **Azure OpenAI**, **Claude**, **Gemini** providers.
- Tiling strategy for dense pages; zoom-in re-asks for uncertain regions.
- Table structure improvement (header inference, colspan/rowspan hints).
- CLI polish: budgets, provider concurrency flags.
- Basic overlays artifact (bbox visualization) for debugging.

## Later
- Rich table reconstruction options.
- Language-aware features (but still LLM-only).
- Hosted service wrapper (optional).
