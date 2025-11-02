"""Custom exceptions mapped to API and CLI error handling.

These mirror the conceptual exceptions in `docs/API_SPEC.md` and map to
CLI exit codes in `docs/CLI_SPEC.md`.
"""


class LayoutScribeError(Exception):
  """Base exception for all LayoutScribe errors."""


class ProviderRateLimitError(LayoutScribeError):
  """Provider returned a rate limit response (e.g., HTTP 429)."""


class ProviderAuthError(LayoutScribeError):
  """Provider authentication failure or missing credentials."""


class SchemaValidationError(LayoutScribeError):
  """Produced JSON failed schema or geometry validation."""


class RenderingError(LayoutScribeError):
  """Input could not be rendered (unsupported or corrupt)."""


class BudgetExceededError(LayoutScribeError):
  """Run aborted due to exceeding configured budget."""


__all__ = [
  "LayoutScribeError",
  "ProviderRateLimitError",
  "ProviderAuthError",
  "SchemaValidationError",
  "RenderingError",
  "BudgetExceededError",
]


