"""Configuration models and environment resolution.

Responsibilities:
- Define Pydantic Settings for runtime configuration, reading from
  environment variables with the precedence described in
  `docs/CONFIGURATION.md`.
- Provide provider-specific concurrency and defaults (DPI, budgets).

Note: Fields only; no loading/validation logic is implemented here.
"""

from typing import Optional

from pydantic import BaseModel


class ProviderKeys(BaseModel):
  openai_api_key: Optional[str] = None
  azure_openai_api_key: Optional[str] = None
  azure_openai_endpoint: Optional[str] = None
  anthropic_api_key: Optional[str] = None
  google_api_key: Optional[str] = None


class RuntimeConfig(BaseModel):
  dpi: int = 180
  max_concurrency: int = 6
  provider_concurrency_openai: int = 6
  provider_concurrency_anthropic: int = 3
  provider_concurrency_google: int = 3
  mlflow_tracking_uri: Optional[str] = None
  budget_usd: Optional[float] = None


class AppSettings(BaseModel):
  provider_keys: ProviderKeys = ProviderKeys()
  runtime: RuntimeConfig = RuntimeConfig()


__all__ = ["ProviderKeys", "RuntimeConfig", "AppSettings"]


