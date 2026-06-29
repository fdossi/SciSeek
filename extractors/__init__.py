"""
Extractors module - Extração multi-formato de documentos
"""

from .base import BaseExtractor, ExtractionResult
from .pdf import PDFExtractor
from .docx import DocxExtractor
from .markdown_text import MarkdownExtractor, TextExtractor
from .factory import ExtractorFactory

__all__ = [
    "BaseExtractor",
    "ExtractionResult",
    "PDFExtractor",
    "DocxExtractor",
    "MarkdownExtractor",
    "TextExtractor",
    "ExtractorFactory",
]
