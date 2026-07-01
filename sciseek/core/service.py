"""Central shared service used by CLI and GUI."""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Callable

from sciseek.core.events import ErrorEvent, ProgressEvent
from sciseek.core.exceptions import ExportError, ValidationError
from sciseek.core.models import (
    DocumentResult,
    RunResult,
    RunSummary,
    SearchConfig,
    SearchHistoryEntry,
    SearchHistoryRecord,
    UserSettings,
    sanitize_terms,
)
from sciseek.core.settings import SettingsStore, UserPaths
from sciseek.database import DataStore
from sciseek.exporters import (
    export_bibtex_partial,
    export_csv,
    export_html,
    export_json,
    export_markdown,
    unique_output_path,
)
from sciseek.extractors import EXTRACTOR_VERSION, ExtractorAdapter
from sciseek.searchers import SearchEngine

ProgressCb = Callable[[ProgressEvent], None]
ErrorCb = Callable[[ErrorEvent], None]


class SearchService:
    def __init__(self, paths: UserPaths, settings_store: SettingsStore, logger: logging.Logger | None = None):
        self.paths = paths
        self.settings_store = settings_store
        self.logger = logger or logging.getLogger("sciseek")
        self.store = DataStore(paths.cache_db, paths.history_db)
        self.cancel_event = Event()

    def cancel(self) -> None:
        self.cancel_event.set()

    def discover(self, cfg: SearchConfig, progress: ProgressCb | None = None) -> list[Path]:
        if not cfg.root.exists() or not cfg.root.is_dir():
            raise ValidationError(f"Diretorio invalido: {cfg.root}")
        suffixes = {f".{f.lower().strip('.')}" for f in cfg.file_formats}
        pattern = "**/*" if cfg.recursive else "*"
        found: list[Path] = []
        for p in cfg.root.glob(pattern):
            if self.cancel_event.is_set():
                break
            if not p.is_file():
                continue
            if cfg.ignore_hidden and p.name.startswith("."):
                continue
            if p.suffix.lower() not in suffixes:
                continue
            found.append(p)
        found.sort()
        if progress:
            progress(
                ProgressEvent(
                    stage="discover",
                    current=len(found),
                    total=len(found),
                    message="Descoberta concluida",
                )
            )
        return found

    def run(
        self,
        cfg: SearchConfig,
        progress: ProgressCb | None = None,
        on_error: ErrorCb | None = None,
    ) -> RunResult:
        self.cancel_event.clear()
        started = time.time()
        errors: list[tuple[str, str]] = []

        if cfg.mode.value != "boolean":
            cfg.terms = sanitize_terms(cfg.terms)
            if not cfg.terms:
                raise ValidationError("Informe ao menos um termo para a busca.")
        else:
            if not cfg.boolean_query.strip():
                raise ValidationError("Informe a expressao booleana.")

        files = self.discover(cfg, progress)
        total = len(files)

        extractor = ExtractorAdapter(max_pdf_pages=cfg.max_pdf_pages)
        engine = SearchEngine(
            case_sensitive=cfg.case_sensitive,
            proximity_words=cfg.proximity_words,
            context_words=cfg.context_words,
        )

        if cfg.mode.value == "regex":
            engine.validate_regex_terms(cfg.terms)

        docs: list[DocumentResult] = []
        processed = 0

        params = {"max_pdf_pages": cfg.max_pdf_pages}

        for idx, file_path in enumerate(files, start=1):
            if self.cancel_event.is_set():
                break
            try:
                if progress:
                    progress(
                        ProgressEvent(
                            stage="extract",
                            current=idx,
                            total=total,
                            message="Extraindo",
                            file_path=file_path,
                        )
                    )

                payload = None
                if cfg.use_cache:
                    payload = self.store.get_cached(file_path, EXTRACTOR_VERSION, params)

                if payload is None:
                    payload = extractor.extract(file_path)
                    if cfg.use_cache:
                        self.store.put_cached(
                            path=file_path,
                            extractor_version=EXTRACTOR_VERSION,
                            params=params,
                            format_type=payload["format_type"],
                            text_content=payload["text_content"],
                            metadata=payload["metadata"],
                        )

                if progress:
                    progress(
                        ProgressEvent(
                            stage="search",
                            current=idx,
                            total=total,
                            message="Buscando",
                            file_path=file_path,
                        )
                    )

                output = engine.search(
                    mode=cfg.mode,
                    text=payload["text_content"],
                    terms=cfg.terms,
                    boolean_query=cfg.boolean_query,
                )

                if output.match_count > 0:
                    docs.append(
                        DocumentResult(
                            file_path=file_path,
                            format_type=payload["format_type"],
                            matched_terms=output.matched_terms,
                            occurrences=output.occurrences,
                            match_count=output.match_count,
                            metadata=payload.get("metadata", {}),
                        )
                    )
                processed += 1
            except Exception as exc:
                msg = str(exc)
                errors.append((file_path.name, msg))
                if on_error:
                    on_error(ErrorEvent(file_name=file_path.name, message=msg))

        output_file = self.export(docs, cfg) if not self.cancel_event.is_set() else None

        elapsed = time.time() - started
        summary = RunSummary(
            total_discovered=total,
            total_processed=processed,
            total_matched=len(docs),
            total_errors=len(errors),
            duration_seconds=elapsed,
            output_file=output_file,
        )

        digest_input = cfg.boolean_query if cfg.mode.value == "boolean" else "|".join(cfg.terms)
        terms_digest = hashlib.sha1(digest_input.encode("utf-8")).hexdigest()[:12]
        self.store.add_history(
            SearchHistoryEntry(
                run_at=datetime.now().isoformat(timespec="seconds"),
                root=str(cfg.root),
                mode=cfg.mode.value,
                terms_digest=terms_digest,
                formats=cfg.file_formats,
                total_processed=summary.total_processed,
                total_matched=summary.total_matched,
                output_file=str(output_file) if output_file else "",
                duration_seconds=summary.duration_seconds,
                status="cancelled" if self.cancel_event.is_set() else "ok",
            )
        )

        return RunResult(documents=docs, errors=errors, summary=summary)

    def export(self, results: list[DocumentResult], cfg: SearchConfig) -> Path:
        out_dir = cfg.output_dir or self.paths.default_exports
        stem = cfg.output_name or f"sciseek_{int(time.time())}"
        fmt = cfg.output_format.lower()
        if fmt == "markdown":
            path = unique_output_path(out_dir, stem, ".md")
            return export_markdown(path, results, cfg)
        if fmt == "csv":
            path = unique_output_path(out_dir, stem, ".csv")
            return export_csv(path, results, cfg)
        if fmt == "json":
            path = unique_output_path(out_dir, stem, ".json")
            return export_json(path, results, cfg)
        if fmt == "html":
            path = unique_output_path(out_dir, stem, ".html")
            return export_html(path, results, cfg)
        if fmt == "bibtex":
            path = unique_output_path(out_dir, stem, ".bib")
            return export_bibtex_partial(path, results, cfg)
        raise ExportError(f"Formato de exportacao nao suportado: {cfg.output_format}")

    def get_settings(self) -> UserSettings:
        return self.settings_store.load()

    def update_settings(self, **kwargs: object) -> UserSettings:
        return self.settings_store.update(**kwargs)

    def history(self, limit: int = 25) -> list[SearchHistoryEntry]:
        return self.store.list_history(limit=limit)

    def history_records(self, limit: int = 50) -> list[SearchHistoryRecord]:
        return self.store.list_history_records(limit=limit)

    def delete_history_entry(self, row_id: int) -> int:
        return self.store.delete_history_entry(row_id)

    def cache_stats(self) -> dict[str, object]:
        return self.store.cache_stats()

    def clear_cache(self) -> int:
        return self.store.clear_cache()

    def clear_history(self) -> int:
        return self.store.clear_history()
