"""Token usage and cost accounting.

Responsibilities:
- Track token usage and estimate cost per page and per run when provider
  data is available.
- Enforce optional budget cap logic.
"""

from __future__ import annotations

from typing import Dict


def estimated_cost_usd(tokens_in: int, tokens_out: int, model: str) -> float:
  """Estimate USD cost given token usage and model."""
  # Placeholder flat pricing per 1M tokens; adjust as needed per provider
  pricing = {
    "openai/gpt-4o": (5.0 / 1_000_000, 15.0 / 1_000_000),  # $5 prompt / $15 completion per 1M tokens
  }
  rate_in, rate_out = pricing.get(model, (5.0 / 1_000_000, 15.0 / 1_000_000))
  return tokens_in * rate_in + tokens_out * rate_out


def should_abort_budget(current_spend: float, budget_usd: float | None) -> bool:
  if budget_usd is None:
    return False
  return current_spend >= budget_usd


