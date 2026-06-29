"""
Extractors para arquivos de texto simples (Markdown e TXT).
"""

import time
from pathlib import Path
from typing import Dict, Any, Tuple
import re
import unicodedata
from .base import BaseExtractor, ExtractionResult


class MarkdownExtractor(BaseExtractor):
    """Extrai texto de arquivos Markdown."""

    def _get_supported_extensions(self) -> Tuple[str, ...]:
        return (".md", ".markdown")

    def can_process(self, file_path: Path) -> bool:
        """Verifica se pode processar o arquivo Markdown."""
        is_valid, _ = self.validate_file(file_path)
        return is_valid

    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extrai texto de um arquivo Markdown.
        
        Args:
            file_path: Caminho para o arquivo Markdown
            
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
                format_type="markdown",
                text_content="",
                metadata={},
                error=error_msg,
                success=False
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extrair metadados YAML frontmatter (opcional)
            metadata = {}
            parse_frontmatter = self.config.get("parse_frontmatter", True)
            
            if parse_frontmatter:
                metadata, content = self._extract_frontmatter(content)

            # Remover blocos de código (opcional)
            include_code = self.config.get("include_code_blocks", False)
            if not include_code:
                content = self._remove_code_blocks(content)

            normalized_text = self._normalize_text(content)

            extraction_time_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="markdown",
                text_content=normalized_text,
                metadata=metadata,
                extraction_time_ms=extraction_time_ms,
                success=True
            )

        except Exception as e:
            extraction_time_ms = (time.time() - start_time) * 1000
            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="markdown",
                text_content="",
                metadata={},
                extraction_time_ms=extraction_time_ms,
                error=f"Erro ao extrair Markdown: {str(e)}",
                success=False
            )

    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extrai frontmatter YAML do início do arquivo."""
        metadata = {}
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                # Simples parse YAML (não usa yaml library)
                frontmatter = parts[1]
                content = parts[2]
                
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()

        return metadata, content

    def _remove_code_blocks(self, content: str) -> str:
        """Remove blocos de código markdown."""
        # Remove fenced code blocks (``` ou ~~~)
        content = re.sub(r'```[\s\S]*?```', '', content)
        content = re.sub(r'~~~[\s\S]*?~~~', '', content)
        return content

    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto extraído."""
        text = unicodedata.normalize("NFKD", text)
        text = " ".join(text.split())
        return text


class TextExtractor(BaseExtractor):
    """Extrai texto de arquivos TXT simples."""

    def _get_supported_extensions(self) -> Tuple[str, ...]:
        return (".txt",)

    def can_process(self, file_path: Path) -> bool:
        """Verifica se pode processar o arquivo TXT."""
        is_valid, _ = self.validate_file(file_path)
        return is_valid

    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extrai texto de um arquivo TXT.
        
        Args:
            file_path: Caminho para o arquivo TXT
            
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
                format_type="txt",
                text_content="",
                metadata={},
                error=error_msg,
                success=False
            )

        try:
            # Tentar diferentes encodings
            content = None
            encodings = ["utf-8", "latin-1", "cp1252", "ascii"]
            
            for encoding in encodings:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise ValueError("Não foi possível decodificar o arquivo com nenhuma encoding")

            normalized_text = self._normalize_text(content)

            extraction_time_ms = (time.time() - start_time) * 1000

            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="txt",
                text_content=normalized_text,
                metadata={},
                extraction_time_ms=extraction_time_ms,
                encoding=encoding,
                success=True
            )

        except Exception as e:
            extraction_time_ms = (time.time() - start_time) * 1000
            return ExtractionResult(
                file_path=file_path,
                file_name=file_path.name,
                format_type="txt",
                text_content="",
                metadata={},
                extraction_time_ms=extraction_time_ms,
                error=f"Erro ao extrair TXT: {str(e)}",
                success=False
            )

    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto extraído."""
        text = unicodedata.normalize("NFKD", text)
        text = " ".join(text.split())
        return text
