"""Provider routing via LiteLLM.

Responsibilities:
- Map user-specified model ids to LiteLLM providers and parameters.
- Expose a thin wrapper for vision calls consumed by PageVision.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict

from ..exceptions import ProviderAuthError, ProviderRateLimitError
from ..utils.backoff import DEFAULT_RETRY


@DEFAULT_RETRY
async def vision_json_call(
  model_id: str, image_bytes: bytes, instruction: str, temperature: float = 0.0
) -> Dict[str, Any]:
  """Call a vision model via LiteLLM and return parsed JSON."""
  try:
    import litellm  # type: ignore
  except ImportError as exc:
    raise RuntimeError("litellm is required for LLM calls") from exc

  image_b64 = base64.b64encode(image_bytes).decode("utf-8")
  image_url = f"data:image/png;base64,{image_b64}"

  messages = [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": instruction},
        {"type": "image_url", "image_url": {"url": image_url}},
      ],
    }
  ]

  try:
    response = await litellm.acompletion(
      model=model_id,
      messages=messages,
      temperature=temperature,
      response_format={"type": "json_object"},
    )
  except Exception as exc:
    err_str = str(exc).lower()
    if "rate" in err_str or "429" in err_str:
      raise ProviderRateLimitError(f"Rate limit: {exc}") from exc
    if "auth" in err_str or "401" in err_str or "403" in err_str:
      raise ProviderAuthError(f"Auth error: {exc}") from exc
    raise

  content = response.choices[0].message.content
  try:
    return json.loads(content)
  except json.JSONDecodeError as exc:
    # Fallback: return empty layout if JSON parse fails
    return {"page_number": 1, "width_px": 0, "height_px": 0, "blocks": []}


