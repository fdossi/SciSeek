"""
Utilitários para resolução e tratamento de caminhos.
"""

from pathlib import Path
from typing import List, Optional


class PathResolver:
    """Resolve caminhos de forma portável."""

    @staticmethod
    def resolve_root(root: str = None) -> Path:
        """
        Resolve o diretório raiz.
        
        Args:
            root: Caminho (relativo ou absoluto) ou None para diretório atual
            
        Returns:
            Path objeto resolvido
        """
        if root is None:
            return Path.cwd()
        
        root_path = Path(root)
        
        # Se relativo, resolver contra cwd
        if not root_path.is_absolute():
            root_path = Path.cwd() / root_path
        
        return root_path.resolve()

    @staticmethod
    def find_files(root: Path, extensions: List[str] = None,
                  recursive: bool = True,
                  ignore_hidden: bool = True) -> List[Path]:
        """
        Encontra arquivos no diretório.
        
        Args:
            root: Diretório raiz
            extensions: Lista de extensões (ex: ['.pdf', '.md'])
            recursive: Buscar recursivamente
            ignore_hidden: Ignorar arquivos ocultos
            
        Returns:
            Lista de caminhos encontrados
        """
        if not root.exists():
            return []

        pattern = "**/*" if recursive else "*"
        files = []

        for path in root.glob(pattern):
            if not path.is_file():
                continue

            # Ignorar ocultos
            if ignore_hidden and path.name.startswith('.'):
                continue

            # Filtrar por extensão
            if extensions and path.suffix.lower() not in extensions:
                continue

            files.append(path)

        return sorted(files)

    @staticmethod
    def make_relative(file_path: Path, root: Path) -> str:
        """
        Converte caminho absoluto em relativo.
        
        Args:
            file_path: Caminho absoluto
            root: Diretório raiz para referenciar
            
        Returns:
            Caminho relativo como string
        """
        try:
            return str(file_path.relative_to(root))
        except ValueError:
            return str(file_path)
