"""MLflow logging helpers.

Responsibilities:
- Initialize MLflow runs when tracing is enabled.
- Log parameters, metrics, and artifacts (e.g., layout.json, document.md).
- Ensure no secrets are logged and paths are sanitized.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


def _get_mlflow():
  try:
    import mlflow  # type: ignore
    return mlflow
  except Exception:  # pragma: no cover
    return None


def start_run(run_name: Optional[str] = None) -> bool:
  mlflow = _get_mlflow()
  if mlflow is None:
    return False
  uri = os.getenv("LAYOUTSCRIBE_MLFLOW_TRACKING_URI")
  if uri:
    mlflow.set_tracking_uri(uri)
  mlflow.start_run(run_name=run_name)
  return True


def log_params(params: Dict[str, Any]) -> None:
  mlflow = _get_mlflow()
  if mlflow is None:
    return
  # Drop any keys that look like secrets
  safe = {k: v for k, v in params.items() if "key" not in k.lower() and "token" not in k.lower()}
  mlflow.log_params({k: str(v) for k, v in safe.items() if v is not None})


def log_artifact(path: Path, artifact_path: Optional[str] = None) -> None:
  mlflow = _get_mlflow()
  if mlflow is None:
    return
  if path.exists():
    mlflow.log_artifact(path.as_posix(), artifact_path=artifact_path)


def end_run(status: str = "FINISHED") -> None:
  mlflow = _get_mlflow()
  if mlflow is None:
    return
  try:
    mlflow.end_run(status=status)
  except Exception:
    pass

