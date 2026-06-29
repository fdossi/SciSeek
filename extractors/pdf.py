"""
Extractor para arquivos PDF usando pypdf.
"""

import time
from pathlib import Path
from typing import Dict, Any, Tuple
import unicodedata
from pypdf import PdfReader
from .base import BaseExtractor, ExtractionResult


class PDFExtractor(BaseExtractor):
    """Extrai texto de arquivos PDF."""

    def _get_supported_extensions(self) -> Tuple[str, ...]:
        return (".pdf",)

    def can_process(self, file_path: Path) -> bool:
        """Verifica se pode processar o arquivo PDF."""
        is_valid, _ = self.validate_file(file_path)
        return is_valid

    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            ExtractionResult com o conteúdo extraído
        """
        start_time = time.time()
        
        # Validar arquivo
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="pdf",
                text_content="",
                metadata={},
                error=error_msg,
                success=False
            )

        try:
            max_pages = self.config.get("max_pages", 30)
            timeout_seconds = self.config.get("timeout_seconds", 10)

            text_parts = []
            page_count = 0

            pdf_reader = PdfReader(str(file_path))
            total_pages = len(pdf_reader.pages)
            pages_to_read = min(max_pages, total_pages)

            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                text = page.extract_text() or ""
                text_parts.append(text)
                page_count += 1

            combined_text = "\n".join(text_parts)
            normalized_text = self._normalize_text(combined_text)

            # Extrair metadados
            metadata = self._extract_metadata(pdf_reader)

            extraction_time_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="pdf",
                text_content=normalized_text,
                metadata=metadata,
                page_count=page_count,
                extraction_time_ms=extraction_time_ms,
                success=True
            )

        except Exception as e:
            extraction_time_ms = (time.time() - start_time) * 1000
            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="pdf",
                text_content="",
                metadata={},
                extraction_time_ms=extraction_time_ms,
                error=f"Erro ao extrair PDF: {str(e)}",
                success=False
            )

    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto extraído."""
        # NFKD normalization
        text = unicodedata.normalize("NFKD", text)
        # Remove multiple spaces
        text = " ".join(text.split())
        return text

    def _extract_metadata(self, pdf_reader: PdfReader) -> Dict[str, Any]:
        """Extrai metadados do PDF."""
        metadata = {}
        
        try:
            doc_info = pdf_reader.metadata
            if doc_info:
                metadata["title"] = doc_info.get("/Title", "").strip()
                metadata["author"] = doc_info.get("/Author", "").strip()
                metadata["subject"] = doc_info.get("/Subject", "").strip()
                metadata["creator"] = doc_info.get("/Creator", "").strip()
                metadata["producer"] = doc_info.get("/Producer", "").strip()
                metadata["creation_date"] = str(doc_info.get("/CreationDate", ""))
        except Exception:
            pass

        return metadata
