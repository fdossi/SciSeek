"""SQLite data store for cache and history."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sciseek.core.models import SearchHistoryEntry, SearchHistoryRecord


class DataStore:
    def __init__(self, cache_db: Path, history_db: Path):
        self.cache_db = cache_db
        self.history_db = history_db
        self.cache_db.parent.mkdir(parents=True, exist_ok=True)
        self.history_db.parent.mkdir(parents=True, exist_ok=True)
        self._init_cache()
        self._init_history()

    def _init_cache(self) -> None:
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache_docs (
                    file_key TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    extractor_version TEXT NOT NULL,
                    params_hash TEXT NOT NULL,
                    format_type TEXT NOT NULL,
                    text_content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _init_history(self) -> None:
        with sqlite3.connect(self.history_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _make_key(path: Path) -> str:
        return hashlib.sha256(str(path).encode("utf-8")).hexdigest()

    @staticmethod
    def _make_params_hash(params: dict[str, Any]) -> str:
        raw = json.dumps(params, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_cached(
        self,
        path: Path,
        extractor_version: str,
        params: dict[str, Any],
    ) -> dict[str, Any] | None:
        key = self._make_key(path)
        st = path.stat()
        params_hash = self._make_params_hash(params)
        with sqlite3.connect(self.cache_db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM cache_docs WHERE file_key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        if row["file_size"] != st.st_size or float(row["mtime"]) != float(st.st_mtime):
            return None
        if row["extractor_version"] != extractor_version or row["params_hash"] != params_hash:
            return None
        return {
            "format_type": row["format_type"],
            "text_content": row["text_content"],
            "metadata": json.loads(row["metadata_json"]),
        }

    def put_cached(
        self,
        path: Path,
        extractor_version: str,
        params: dict[str, Any],
        format_type: str,
        text_content: str,
        metadata: dict[str, Any],
    ) -> None:
        key = self._make_key(path)
        st = path.stat()
        params_hash = self._make_params_hash(params)
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_docs (
                    file_key, file_path, file_size, mtime, extractor_version,
                    params_hash, format_type, text_content, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    str(path),
                    st.st_size,
                    st.st_mtime,
                    extractor_version,
                    params_hash,
                    format_type,
                    text_content,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            conn.commit()

    def cache_stats(self) -> dict[str, Any]:
        with sqlite3.connect(self.cache_db) as conn:
            cnt = conn.execute("SELECT COUNT(*) FROM cache_docs").fetchone()[0]
        size_mb = self.cache_db.stat().st_size / (1024 * 1024) if self.cache_db.exists() else 0.0
        return {"entries": cnt, "size_mb": round(size_mb, 3)}

    def clear_cache(self) -> int:
        with sqlite3.connect(self.cache_db) as conn:
            cur = conn.execute("DELETE FROM cache_docs")
            conn.commit()
            return cur.rowcount

    def add_history(self, entry: SearchHistoryEntry) -> None:
        payload = json.dumps(asdict(entry), ensure_ascii=False)
        with sqlite3.connect(self.history_db) as conn:
            conn.execute("INSERT INTO search_history(payload_json) VALUES (?)", (payload,))
            conn.commit()

    def list_history(self, limit: int = 25) -> list[SearchHistoryEntry]:
        with sqlite3.connect(self.history_db) as conn:
            rows = conn.execute(
                "SELECT payload_json FROM search_history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        out: list[SearchHistoryEntry] = []
        for (payload,) in rows:
            data = json.loads(payload)
            out.append(SearchHistoryEntry(**data))
        return out

    def list_history_records(self, limit: int = 50) -> list[SearchHistoryRecord]:
        with sqlite3.connect(self.history_db) as conn:
            rows = conn.execute(
                "SELECT id, payload_json FROM search_history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        out: list[SearchHistoryRecord] = []
        for row_id, payload in rows:
            out.append(SearchHistoryRecord(row_id=row_id, entry=SearchHistoryEntry(**json.loads(payload))))
        return out

    def delete_history_entry(self, row_id: int) -> int:
        with sqlite3.connect(self.history_db) as conn:
            cur = conn.execute("DELETE FROM search_history WHERE id = ?", (row_id,))
            conn.commit()
            return cur.rowcount

    def clear_history(self) -> int:
        with sqlite3.connect(self.history_db) as conn:
            cur = conn.execute("DELETE FROM search_history")
            conn.commit()
            return cur.rowcount
