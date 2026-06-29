"""
Validadores de entrada e configuração.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional


class ConfigValidator:
    """Valida configurações."""

    @staticmethod
    def validate_root_path(root: str) -> Tuple[bool, Optional[str]]:
        """
        Valida se o caminho raiz é válido.
        
        Returns:
            Tupla (is_valid, error_message)
        """
        if not root:
            return False, "Caminho raiz não pode estar vazio"

        path = Path(root)
        
        if not path.exists():
            return False, f"Caminho não existe: {root}"

        if not path.is_dir():
            return False, f"Caminho não é um diretório: {root}"

        return True, None

    @staticmethod
    def validate_search_terms(terms: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Valida se os termos de busca são válidos.
        
        Returns:
            Tupla (is_valid, error_message)
        """
        if not terms:
            return False, "Pelo menos um termo de busca é necessário"

        if any(not isinstance(t, str) or not t.strip() for t in terms):
            return False, "Todos os termos devem ser strings não-vazias"

        return True, None

    @staticmethod
    def validate_file_formats(formats: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Valida se os formatos são suportados.
        
        Args:
            formats: Lista de formatos (ex: ['pdf', 'docx'])
            
        Returns:
            Tupla (is_valid, error_message)
        """
        supported = ['pdf', 'docx', 'md', 'txt', 'xml', 'xlsx']
        
        if not formats:
            return False, "Pelo menos um formato deve ser especificado"

        invalid = [f for f in formats if f.lower() not in supported]
        
        if invalid:
            return False, f"Formatos não suportados: {', '.join(invalid)}"

        return True, None

    @staticmethod
    def validate_search_mode(mode: str) -> Tuple[bool, Optional[str]]:
        """
        Valida se o modo de busca é válido.
        
        Returns:
            Tupla (is_valid, error_message)
        """
        valid_modes = ['simple', 'regex', 'proximity', 'boolean']
        
        if mode.lower() not in valid_modes:
            return False, f"Modo inválido: {mode}. Válidos: {', '.join(valid_modes)}"

        return True, None

    @staticmethod
    def validate_output_format(format_type: str) -> Tuple[bool, Optional[str]]:
        """
        Valida se o formato de saída é válido.
        
        Returns:
            Tupla (is_valid, error_message)
        """
        valid_formats = ['markdown', 'csv', 'json', 'html', 'bibtex']
        
        if format_type.lower() not in valid_formats:
            return False, f"Formato inválido: {format_type}. Válidos: {', '.join(valid_formats)}"

        return True, None
