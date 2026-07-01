"""Execution events emitted by SearchService."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class ProgressEvent:
    stage: str
    current: int
    total: int
    message: str
    file_path: Optional[Path] = None


@dataclass(slots=True)
class ErrorEvent:
    file_name: str
    message: str
