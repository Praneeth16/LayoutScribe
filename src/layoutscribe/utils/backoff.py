"""Retry and backoff policies.

Responsibilities:
- Provide decorators/utilities for exponential backoff with jitter on
  retryable provider errors (429/5xx/timeouts).
"""

from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential_jitter

DEFAULT_RETRY = retry(
  reraise=True,
  stop=stop_after_attempt(5),
  wait=wait_exponential_jitter(exp_base=2, max=10),
)



