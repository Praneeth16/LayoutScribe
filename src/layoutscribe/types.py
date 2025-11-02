"""Typed data models for LayoutScribe.

Responsibilities:
- Define Pydantic models for Block, PageLayout, DocumentLayout, and
  ParsedDocument as specified in `docs/API_SPEC.md` and validated by
  `docs/schema/layout_page.schema.json`.
- Centralize typed contracts used by API and CLI layers.

Note: Fields only; no behavior or validation logic is implemented here.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


BlockType = Literal[
  "title",
  "heading",
  "paragraph",
  "list_item",
  "table",
  "figure",
  "equation",
  "caption",
  "footer",
  "header",
]


class TablePayload(BaseModel):
  rows: List[List[str]]


class Block(BaseModel):
  id: str
  type: BlockType
  bbox: List[float]  # [x0, y0, x1, y1], normalized 0..1
  text: Optional[str] = None
  level: Optional[int] = None  # for heading
  table: Optional[TablePayload] = None
  conf: Optional[float] = None  # 0..1, heuristic


class PageLayout(BaseModel):
  page_number: int
  width_px: int
  height_px: int
  blocks: List[Block]


class DocumentLayout(BaseModel):
  pages: List[PageLayout]


class ParsedDocument(BaseModel):
  markdown: Optional[str] = None
  text: Optional[str] = None
  layout_json: Optional[DocumentLayout] = None
  overlays_dir: Optional[str] = None
  intermediate_dir: Optional[str] = None
  metadata: Optional["DocumentMetadata"] = None
  artifact_paths: Optional[Dict[str, List[str]]] = None


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


__all__ = [
  "BlockType",
  "TablePayload",
  "Block",
  "PageLayout",
  "DocumentLayout",
  "ParsedDocument",
  "DocumentMetadata",
  "PageMetadata",
]


