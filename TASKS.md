# Tasks

## Priority: P0 (MVP Usability)

- Package skeleton: `pyproject.toml`, `layoutscribe/` with `api.py`, `cli.py`, `config.py`, `types.py`
- Minimal runnable CLI: `layoutscribe parse <file>` with stub outputs
- Formal JSON Schema validation wired into reviewer step
- Examples: `examples/` inputs and expected outputs
- Provider setup docs completeness and `.env` example validation

## Priority: P1 (Quality & Reliability)

- Reviewer re-ask policy implementation (thresholds, retries, budget checks)
- Overlay generation for sampled pages
- Basic tests: schema validation, golden markdown, fake provider
- Bench harness: tiny dataset run with MLflow logging
- Security: ephemeral temp dirs, `--save-intermediate` gate

## Priority: P2 (Ecosystem & DX)

- CI: lint (ruff/black), tests, wheel build
- Docs site (MkDocs/Docusaurus) and GH Pages publish
- Provider matrix expansion (Azure, Anthropic, Google)
- Caching keyed by page image hash + prompt version
- Issue/PR templates, CODEOWNERS

## Stretch

- Rich table reconstruction options
- Hosted service wrapper (optional)
- Visualization tool for layout JSON

## Tracking & Status

- Use GitHub Projects or Issues to track these tasks
- Link commits/PRs to tasks for traceability

