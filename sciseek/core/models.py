"""Typed models for SciSeek core."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional


class SearchMode(str, Enum):
    SIMPLE = "simple"
    REGEX = "regex"
    PROXIMITY = "proximity"
    BOOLEAN = "boolean"


@dataclass(slots=True)
class SearchConfig:
    root: Path
    file_formats: List[str]
    mode: SearchMode
    terms: List[str] = field(default_factory=list)
    boolean_query: str = ""
    groups: List[str] = field(default_factory=list)
    recursive: bool = True
    ignore_hidden: bool = True
    case_sensitive: bool = False
    use_cache: bool = True
    output_format: str = "markdown"
    output_dir: Optional[Path] = None
    output_name: Optional[str] = None
    max_pdf_pages: int = 30
    proximity_words: int = 10
    context_words: int = 20


@dataclass(slots=True)
class DocumentRef:
    path: Path
    format_type: str


@dataclass(slots=True)
class Occurrence:
    term: str
    count: int
    snippet: str
    page: Optional[int] = None
    line: Optional[int] = None


@dataclass(slots=True)
class DocumentResult:
    file_path: Path
    format_type: str
    matched_terms: List[str]
    occurrences: List[Occurrence]
    match_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunSummary:
    total_discovered: int
    total_processed: int
    total_matched: int
    total_errors: int
    duration_seconds: float
    output_file: Optional[Path] = None


@dataclass(slots=True)
class RunResult:
    documents: List[DocumentResult]
    errors: List[tuple[str, str]]
    summary: RunSummary


@dataclass(slots=True)
class UserSettings:
    language: str = "pt-BR"
    theme: str = "system"
    default_root: str = "."
    default_formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "md", "txt"])
    cache_enabled: bool = True
    max_pdf_pages: int = 30
    proximity_words: int = 10
    context_words: int = 20
    open_output_on_finish: bool = False
    workers: int = 1


@dataclass(slots=True)
class SearchHistoryEntry:
    run_at: str
    root: str
    mode: str
    terms_digest: str
    formats: List[str]
    total_processed: int
    total_matched: int
    output_file: str
    duration_seconds: float
    status: str


@dataclass(slots=True)
class SearchHistoryRecord:
    row_id: int
    entry: SearchHistoryEntry


def sanitize_terms(terms: List[str]) -> List[str]:
    cleaned: List[str] = []
    seen: set[str] = set()
    for raw in terms:
        t = raw.strip()
        if not t:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(t)
    return cleaned
