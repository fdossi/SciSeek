"""Adapters for legacy extractor implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from extractors.factory import ExtractorFactory  # legacy module reuse

EXTRACTOR_VERSION = "1"


class ExtractorAdapter:
    def __init__(self, max_pdf_pages: int = 30):
        self._factory = ExtractorFactory(
            {
                "pdf": {"max_pages": max_pdf_pages},
                "docx": {"include_tables": True},
                "md": {"parse_frontmatter": True, "include_code_blocks": False},
            }
        )

    def extract(self, file_path: Path) -> Dict[str, Any]:
        extractor = self._factory.get_extractor(file_path)
        if extractor is None:
            raise ValueError(f"Formato nao suportado para extracao: {file_path.suffix}")
        result = extractor.extract(file_path)
        if not result.success:
            raise ValueError(result.error or "Falha na extracao")
        return {
            "format_type": result.format_type,
            "text_content": result.text_content,
            "metadata": result.metadata,
            "page_count": result.page_count,
        }
