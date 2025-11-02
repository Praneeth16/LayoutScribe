# Development Plan (Weekend MVP)

## Day 1 — Skeleton & Contracts
- [ ] Create repo structure (folders & markdowns).
- [ ] Define **config map** and **env vars** (CONFIGURATION.md).
- [ ] Finalize **JSON schema** + **prompt rules** (PROMPTS_AND_SCHEMA.md).
- [ ] Write **LangGraph node responsibilities** (this file + ARCHITECTURE.md).
- [ ] Establish **API & CLI contracts** (API_SPEC.md, CLI_SPEC.md).
- [ ] Prepare **MLflow tracking plan** (TESTING_STRATEGY.md / BENCHMARKS.md).

## Day 2 — Providers & Bench Harness
- [ ] Choose first provider: **OpenAI GPT-4o / o4-mini** (or Azure).
- [ ] Draft provider matrix & LiteLLM model names (PROVIDERS.md).
- [ ] Document **rendering paths** for PDF/PPTX/DOCX (no OCR).
- [ ] Define **benchmark micro-splits** & metrics (BENCHMARKS.md).
- [ ] Fill **ROADMAP.md** with post-MVP steps.

## Acceptance Criteria (MVP)
- [ ] Parse a 10–20 page digital PDF: ≥95% pages produce valid layout JSON.
- [ ] Markdown preserves heading levels & lists on most pages (manual spot check).
- [ ] MLflow logs: params, tokens/cost (if available), latency per page, artifacts (layout.json, markdown.md).
- [ ] CLI runs with env-provided keys; no secrets in repo.

## Risks & Mitigations
- Dense pages → token blowups: use tiling; clamp context.
- Slide/page rendering fidelity: prefer headless LibreOffice → PDF → PNG.
- Rate limits: per-provider semaphores, backoff.
