"""Command-line interface (stub).

Responsibilities:
- Provide a Typer-based CLI exposing `layoutscribe parse` and related
  flags described in `docs/CLI_SPEC.md`.
- Handle I/O paths, page selection, and artifact directories.
- Configure logging verbosity and optional MLflow tracing.

Note: This is a no-op CLI scaffold to expose `layoutscribe --help`.
"""

from pathlib import Path
from typing import List, Optional

import sys
import asyncio
import typer
from .api import parse as api_parse
from .utils.io import default_output_dir, ensure_dir, export_outputs
from .exceptions import (
  ProviderAuthError,
  ProviderRateLimitError,
  SchemaValidationError,
  RenderingError,
  BudgetExceededError,
)
from .tracing.mlflow_logger import start_run, log_params, log_artifact, end_run

app = typer.Typer(
  help="LLM-only document layout parsing (MVP scaffold)",
  no_args_is_help=True,
)


@app.callback()
def root(
  version: Optional[bool] = typer.Option(
    None,
    "--version",
    help="Show version and exit",
    is_flag=True,
  ),
  verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
  quiet: bool = typer.Option(False, "--quiet", help="Reduce output verbosity"),
) -> None:
  """LayoutScribe CLI root. Global options only; subcommands implement actions."""
  # Intentionally no logic here (skeleton only)
  return


@app.command()
def parse(
  input_path: Path = typer.Argument(..., help="Path to input PDF/PPTX/DOCX"),
  llm: str = typer.Option(..., "--llm", help="LiteLLM model id (e.g., openai/gpt-4o)"),
  outputs: List[str] = typer.Option(
    ["markdown", "text", "layout_json"],
    "--outputs",
    help="Outputs to produce",
  ),
  output_dir: Optional[Path] = typer.Option(
    None,
    "--output-dir",
    help="Directory to write artifacts",
  ),
  pages: Optional[str] = typer.Option(None, "--pages", help="Page selection, e.g., 1-3,7"),
  dpi: int = typer.Option(180, "--dpi", help="Render DPI"),
  parallel_pages: int = typer.Option(6, "--parallel-pages", help="Async concurrency cap"),
  provider_concurrency: Optional[int] = typer.Option(
    None,
    "--provider-concurrency",
    help="Override provider-specific semaphore",
  ),
  trace_mlflow: bool = typer.Option(False, "--trace-mlflow", help="Enable MLflow run"),
  budget_usd: Optional[float] = typer.Option(None, "--budget-usd", help="Cost cap (USD)"),
  save_overlays: bool = typer.Option(False, "--save-overlays", help="Save bbox overlays"),
  save_intermediate: bool = typer.Option(
    False,
    "--save-intermediate",
    help="Persist intermediate JSON",
  ),
  cost_per_page_usd: float = typer.Option(
    0.02,
    "--cost-per-page-usd",
    help="Estimated cost per page (USD) for budget guard",
  ),
  preview_chars: int = typer.Option(
    500,
    "--preview-chars",
    help="Characters to display per preview in console (0 to disable)",
  ),
  format: Optional[str] = typer.Option(
    None,
    "--format",
    help="Alias for outputs: all|markdown|text|layout_json",
  ),
) -> None:
  """Parse a document into Markdown, text, and layout JSON (skeleton only)."""
  out_dir = output_dir or default_output_dir(input_path)
  ensure_dir(out_dir)
  allowed_outputs = {"markdown", "text", "layout_json"}

  if format:
    fmt = format.lower()
    alias_map = {
      "markdown": ["markdown"],
      "md": ["markdown"],
      "text": ["text"],
      "plain": ["text"],
      "layout_json": ["layout_json"],
      "json": ["layout_json"],
      "all": ["markdown", "text", "layout_json"],
    }
    selected: List[str] = []
    for token in [t.strip() for t in fmt.split(",") if t.strip()]:
      mapped = alias_map.get(token)
      if not mapped:
        raise typer.BadParameter(
          f"Unknown format '{token}'. Choose from all|markdown|text|layout_json.",
          param_hint="--format",
        )
      selected.extend(mapped)
    outputs = selected

  normalized: List[str] = []
  for value in outputs:
    parts = [p.strip().lower() for p in value.split(",") if p.strip()]
    normalized.extend(parts or [value.lower()])

  deduped: List[str] = []
  for item in normalized:
    if item not in deduped:
      deduped.append(item)
  outputs = deduped

  invalid = [o for o in outputs if o not in allowed_outputs]
  if invalid:
    raise typer.BadParameter(f"Invalid outputs: {', '.join(invalid)}.", param_hint="--outputs")

  run_started = False
  try:
    if trace_mlflow:
      run_started = start_run(run_name="layoutscribe-parse")
      log_params(
        {
          "llm": llm,
          "dpi": dpi,
          "parallel_pages": parallel_pages,
          "provider_concurrency": provider_concurrency,
          "budget_usd": budget_usd,
          "pages": pages,
          "save_overlays": save_overlays,
          "save_intermediate": save_intermediate,
          "outputs": ",".join(outputs),
          "preview_chars": preview_chars,
          "cost_per_page_usd": cost_per_page_usd,
        }
      )

    doc = asyncio.run(
      api_parse(
        path=input_path.as_posix(),
        outputs=outputs,
        llm=llm,
        dpi=dpi,
        parallel_pages=parallel_pages,
        trace_mlflow=trace_mlflow,
        provider_concurrency=provider_concurrency,
        budget_usd=budget_usd,
        pages_spec=pages,
        save_overlays=save_overlays,
        save_intermediate=save_intermediate,
        cost_per_page_usd=cost_per_page_usd,
      )
    )
    manifest = export_outputs(
      doc,
      outputs=outputs,
      target_dir=out_dir,
      save_overlays=save_overlays,
      save_intermediate=save_intermediate,
    )
    doc.artifact_paths = manifest

    primary_paths = [Path(p) for p in manifest.get("primary", [])]
    overlay_paths = [Path(p) for p in manifest.get("overlays", [])]
    intermediate_paths = [Path(p) for p in manifest.get("intermediate", [])]

    if run_started:
      for path in primary_paths:
        log_artifact(path)
      for path in overlay_paths:
        log_artifact(path, artifact_path="overlays")
      for path in intermediate_paths:
        log_artifact(path, artifact_path="intermediate")

    typer.echo(f"Artifacts written to {out_dir}")

    if doc.metadata:
      meta = doc.metadata
      typer.echo(
        f"Summary → pages: {meta.page_count}, blocks: {meta.blocks_total}, tables: {meta.table_total}"
      )
      for page in meta.pages:
        preview = page.text_preview.strip()
        if preview_chars and len(preview) > preview_chars:
          preview = preview[:preview_chars] + "…"
        preview_suffix = f", preview=\"{preview}\"" if preview else ""
        typer.echo(
          f"  - Page {page.page_number}: blocks={page.block_count}, tables={page.table_count}{preview_suffix}"
        )

    if preview_chars:
      if "markdown" in outputs and doc.markdown:
        snippet = doc.markdown.strip()
        if len(snippet) > preview_chars:
          snippet = snippet[:preview_chars] + "…"
        typer.echo("\n[markdown preview]\n" + snippet)
      if "text" in outputs and doc.text:
        snippet = doc.text.strip()
        if len(snippet) > preview_chars:
          snippet = snippet[:preview_chars] + "…"
        typer.echo("\n[text preview]\n" + snippet)
  except SchemaValidationError as exc:
    typer.echo(f"Validation error: {exc}", err=True)
    if run_started:
      end_run(status="FAILED")
    sys.exit(2)
  except (ProviderAuthError, ProviderRateLimitError) as exc:
    typer.echo(f"Provider error: {exc}", err=True)
    if run_started:
      end_run(status="FAILED")
    sys.exit(3)
  except BudgetExceededError as exc:
    typer.echo(f"Budget exceeded: {exc}", err=True)
    if run_started:
      end_run(status="FAILED")
    sys.exit(4)
  except RenderingError as exc:
    typer.echo(f"Rendering error: {exc}", err=True)
    if run_started:
      end_run(status="FAILED")
    sys.exit(5)
  except Exception as exc:
    typer.echo(f"Unexpected error: {exc}", err=True)
    if run_started:
      end_run(status="FAILED")
    raise
  finally:
    if run_started:
      end_run(status="FINISHED")


def main() -> None:
  """Entrypoint for console script."""
  app()




