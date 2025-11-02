# Configuration & Environment

## Required (depending on provider)
- `OPENAI_API_KEY` (OpenAI)
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` (Azure OpenAI)
- `ANTHROPIC_API_KEY` (Anthropic)
- `GOOGLE_API_KEY` (Google Gemini)

## Optional
- `LAYOUTSCRIBE_DPI` (default 180)
- `LAYOUTSCRIBE_MAX_CONCURRENCY` (default 6)
- `LAYOUTSCRIBE_PROVIDER_CONCURRENCY_OPENAI` (default 6)
- `LAYOUTSCRIBE_PROVIDER_CONCURRENCY_ANTHROPIC` (default 3)
- `LAYOUTSCRIBE_PROVIDER_CONCURRENCY_GOOGLE` (default 3)
- `LAYOUTSCRIBE_MLFLOW_TRACKING_URI` (if not using local)
- `LAYOUTSCRIBE_BUDGET_USD` (cost cap per run)

## Configuration Precedence
1. Function args
2. Env vars
3. Package defaults

## Secrets
- Never commit keys.
- Prefer `.env` locally; CI via secrets store.

## .env Example

```
# Provider keys
OPENAI_API_KEY=sk-...

# LayoutScribe defaults
LAYOUTSCRIBE_DPI=180
LAYOUTSCRIBE_MAX_CONCURRENCY=6
LAYOUTSCRIBE_PROVIDER_CONCURRENCY_OPENAI=6
LAYOUTSCRIBE_BUDGET_USD=0.50

# MLflow (optional)
LAYOUTSCRIBE_MLFLOW_TRACKING_URI=http://localhost:5000
```
