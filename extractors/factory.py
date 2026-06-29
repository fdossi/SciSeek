"""
Factory para criar e gerenciar extractores.
Implementa o padrão Factory Method e Strategy.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from .base import BaseExtractor
from .pdf import PDFExtractor
from .docx import DocxExtractor
from . import MarkdownExtractor, TextExtractor


class ExtractorFactory:
    """Factory para criar extractores apropriados para diferentes formatos."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o factory.
        
        Args:
            config: Configurações globais para os extractores
        """
        self.config = config or {}
        self._extractors: Dict[str, type] = {
            "pdf": PDFExtractor,
            "docx": DocxExtractor,
            "md": MarkdownExtractor,
            "txt": TextExtractor,
        }

    def get_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """
        Retorna um extractor apropriado para o arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Instância do extractor apropriado ou None
        """
        file_ext = file_path.suffix.lower().lstrip(".")
        
        # Procurar pela extensão
        if file_ext in self._extractors:
            extractor_class = self._extractors[file_ext]
            # Passar config específica se existir
            format_config = self.config.get(file_ext, {})
            return extractor_class(config=format_config)

        return None

    def can_process(self, file_path: Path) -> bool:
        """Verifica se o arquivo pode ser processado."""
        extractor = self.get_extractor(file_path)
        if extractor:
            return extractor.can_process(file_path)
        return False

    def get_supported_formats(self) -> List[str]:
        """Retorna lista de formatos suportados."""
        return list(self._extractors.keys())

    def get_supported_extensions(self) -> List[str]:
        """Retorna lista de extensões suportadas."""
        extensions = []
        for extractor_class in self._extractors.values():
            extractor = extractor_class()
            extensions.extend(extractor.supported_extensions)
        return extensions

    def register_extractor(self, format_name: str, extractor_class: type) -> None:
        """
        Registra um novo extractor.
        
        Args:
            format_name: Nome do formato (ex: 'xml')
            extractor_class: Classe que herda de BaseExtractor
        """
        if not issubclass(extractor_class, BaseExtractor):
            raise TypeError(f"{extractor_class} deve herdar de BaseExtractor")
        
        self._extractors[format_name] = extractor_class

    def remove_extractor(self, format_name: str) -> None:
        """Remove um extractor registrado."""
        if format_name in self._extractors:
            del self._extractors[format_name]
