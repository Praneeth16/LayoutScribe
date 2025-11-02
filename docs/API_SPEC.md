# API Specification (No Code)

## Public Async Function
### `parse(...)`
**Purpose:** Parse a document into Markdown, plain text, and layout JSON using an LLM-only pipeline.

**Signature (conceptual):**
```
parse(
  path: str,
  outputs: list[str],                 # e.g., ["markdown", "text", "layout_json"]
  llm: str,                           # LiteLLM model id (e.g., "openai/gpt-4o")
  llm_params: dict = { "temperature": 0 },
  dpi: int = 180,
  parallel_pages: int = 6,
  trace_mlflow: bool = True,
  provider_concurrency: int | None = None,
  budget_usd: float | None = None,
  pages_spec: str | None = None,
  save_overlays: bool = False,
  save_intermediate: bool = False,
  cost_per_page_usd: float = 0.02,
  output_dir: str | Path | None = None,
) -> ParsedDocument
```

**Outputs Shape:**
- `ParsedDocument.markdown: str`
- `ParsedDocument.text: str`
- `ParsedDocument.layout_json: dict` (see **PROMPTS_AND_SCHEMA.md**)
- `ParsedDocument.metadata: DocumentMetadata`
- `ParsedDocument.artifact_paths: dict[str, list[str]] | None` (manifest when `output_dir` is provided or CLI export runs)

**Behavioral Notes**
- Validates JSON schema; if failure → one or two **LLM re-asks** (targeted).
- Returns best-effort artifacts even if some pages fail.

## Exceptions
- `ProviderRateLimitError`, `ProviderAuthError`, `SchemaValidationError`, `RenderingError`, `BudgetExceededError`.

### Error Mapping
- API exceptions map to CLI exit codes: `SchemaValidationError→2`, `Provider*→3`, `BudgetExceeded→4`, `RenderingError→5`.

## Data Models (conceptual)

```python
from pydantic import BaseModel
from typing import Literal, Optional, List

BlockType = Literal[
    "title", "heading", "paragraph", "list_item", "table",
    "figure", "equation", "caption", "footer", "header",
]

class TablePayload(BaseModel):
    rows: List[List[str]]

class Block(BaseModel):
    id: str
    type: BlockType
    bbox: list[float]  # [x0, y0, x1, y1], normalized 0..1
    text: Optional[str] = None
    level: Optional[int] = None  # for heading
    table: Optional[TablePayload] = None
    conf: Optional[float] = None  # 0..1, heuristic

class PageLayout(BaseModel):
    page_number: int
    width_px: int
    height_px: int
    blocks: List[Block]

class ParsedDocument(BaseModel):
    markdown: Optional[str]
    text: Optional[str]
    layout_json: Optional[dict]  # see docs/schema/layout_page.schema.json
    overlays_dir: Optional[str]
    intermediate_dir: Optional[str]
    metadata: Optional[DocumentMetadata]
    artifact_paths: Optional[dict[str, list[str]]]

class PageMetadata(BaseModel):
    page_number: int
    block_count: int
    table_count: int
    text_preview: str

class DocumentMetadata(BaseModel):
    page_count: int
    blocks_total: int
    table_total: int
    pages: List[PageMetadata]
```

## Usage Examples (conceptual)

```python
# Async usage
# doc = await parse(
#     path="samples/report.pdf",
#     outputs=["markdown", "text", "layout_json"],
#     llm="openai/gpt-4o",
#     dpi=180,
#     parallel_pages=6,
#     budget_usd=1.00,
#     output_dir="./artifacts/report",
# )
# assert doc.metadata.page_count > 0
# print(doc.artifact_paths)
```
