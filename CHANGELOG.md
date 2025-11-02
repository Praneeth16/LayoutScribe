# Changelog

## [0.1.0a3] - 2025-11-02
### Added
- Vision prompt overhauled with explicit JSON contract, 10 rules, and examples.
- Fallback injection of rendered page text when LLM returns empty blocks.
- Overlays export for bounding boxes with labels/confidence.
- Packaging extras: `office` (pptx/docx), `dev` (ruff/black/pytest).
- CLI: `--save-intermediate`, `--preview-chars`, budget guard, provider concurrency.
- API: async `parse` returning Markdown/Text/Layout JSON and metadata.
- MLflow tracing (opt-in) for params, metrics, and artifacts.

### Fixed
- Packaged JSON Schema via `importlib.resources` (no filesystem paths).
- Resolved `asyncio` import availability in orchestrator.

### Changed
- README and docs updated for 0.1 alpha; links and installation instructions.

## [0.1.0] - MVP (Unreleased)
- Initial repo scaffolding, specs, and plans (no code).
