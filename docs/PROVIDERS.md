# Providers via LiteLLM (Reference)

## Initial target
- `openai/gpt-4o` or `openai/o4-mini` (or Azure equivalents)

## Next
- `anthropic/claude-3.5-sonnet`
- `google/gemini-1.5-pro`

## Notes
- Keep temperature low (0–0.2) for consistent JSON.
- Apply provider-specific concurrency semaphores to avoid 429s.
- Capture token usage/cost if provider exposes it.

## Recommended Settings (early guidance)

- OpenAI: temperature 0, `--parallel-pages 6`, provider concurrency 6
- Anthropic: temperature 0–0.2, provider concurrency 3
- Google: temperature 0–0.2, provider concurrency 3

Document model-specific constraints (image size, context) before public release.
