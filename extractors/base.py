"""
Classe abstrata base para extractores de documentos.
Define a interface comum para todos os tipos de arquivo suportados.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Resultado da extração de um documento."""
    file_path: Path
    file_name: str
    format_type: str
    text_content: str
    metadata: Dict[str, Any]
    page_count: Optional[int] = None
    encoding: str = "utf-8"
    extraction_time_ms: float = 0.0
    error: Optional[str] = None
    success: bool = True


class BaseExtractor(ABC):
    """
    Classe abstrata base para todos os extractores de documentos.
    
    Cada extractor concreto (PDF, DOCX, MD, etc.) deve herdar desta classe
    e implementar os métodos abstratos.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o extractor.
        
        Args:
            config: Dicionário com configurações específicas do formato
        """
        self.config = config or {}
        self.supported_extensions = self._get_supported_extensions()

    @abstractmethod
    def _get_supported_extensions(self) -> Tuple[str, ...]:
        """Retorna tupla com extensões suportadas (ex: ('.pdf',))"""
        pass

    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Verifica se o arquivo pode ser processado por este extractor."""
        pass

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extrai o texto do documento.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            ExtractionResult com o conteúdo extraído
        """
        pass

    def validate_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Valida se o arquivo existe e tem extensão correta.
        
        Returns:
            Tupla (is_valid, error_message)
        """
        if not file_path.exists():
            return False, f"Arquivo não encontrado: {file_path}"

        if not file_path.is_file():
            return False, f"Caminho não é um arquivo: {file_path}"

        if file_path.suffix.lower() not in self.supported_extensions:
            return False, f"Extensão não suportada: {file_path.suffix}"

        return True, None

    def get_file_size_mb(self, file_path: Path) -> float:
        """Retorna o tamanho do arquivo em MB."""
        return file_path.stat().st_size / (1024 * 1024)

    def get_format_type(self) -> str:
        """Retorna o tipo de formato que este extractor processa."""
        return self.__class__.__name__.replace("Extractor", "").lower()
