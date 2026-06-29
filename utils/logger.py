"""
Sistema de logging para o research searcher.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Gerenciador centralizado de logging."""

    _instance = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._logger = self._setup_logger()

    @staticmethod
    def _setup_logger(log_file: Path = None, level: str = "INFO") -> logging.Logger:
        """Configura o logger."""
        if log_file is None:
            log_file = Path.cwd() / "research_searcher.log"

        logger = logging.getLogger("research_searcher")
        logger.setLevel(level)

        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)

        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Formato
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Retorna a instância do logger."""
        return self._logger

    def info(self, message: str) -> None:
        """Log de informação."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log de aviso."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log de erro."""
        self._logger.error(message)

    def debug(self, message: str) -> None:
        """Log de debug."""
        self._logger.debug(message)


# Instância global do logger
_logger_instance = Logger()
log = _logger_instance.get_logger()
