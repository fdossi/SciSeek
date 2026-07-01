"""Settings and user path management."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .models import UserSettings

try:
    from platformdirs import PlatformDirs
except ImportError:  # pragma: no cover
    PlatformDirs = None  # type: ignore


class UserPaths:
    def __init__(self, config_dir: Path, cache_dir: Path, data_dir: Path, log_dir: Path):
        self.config_dir = config_dir
        self.cache_dir = cache_dir
        self.data_dir = data_dir
        self.log_dir = log_dir
        self.config_file = self.config_dir / "settings.json"
        self.history_db = self.data_dir / "history.sqlite"
        self.cache_db = self.cache_dir / "cache.sqlite"
        self.default_exports = self.data_dir / "exports"

    @classmethod
    def detect(cls, app_name: str, app_author: str) -> "UserPaths":
        if PlatformDirs is None:
            base = Path.cwd() / ".sciseek-user"
            config = base / "config"
            cache = base / "cache"
            data = base / "data"
            logs = base / "logs"
        else:
            dirs = PlatformDirs(app_name, app_author)
            config = Path(dirs.user_config_dir)
            cache = Path(dirs.user_cache_dir)
            data = Path(dirs.user_data_dir)
            logs = Path(dirs.user_log_dir)
        for p in (config, cache, data, logs):
            p.mkdir(parents=True, exist_ok=True)
        exports = data / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        return cls(config, cache, data, logs)


class SettingsStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load(self) -> UserSettings:
        if not self.file_path.exists():
            return UserSettings()
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
            return UserSettings(**raw)
        except Exception:
            return UserSettings()

    def save(self, settings: UserSettings) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")

    def update(self, **kwargs: Any) -> UserSettings:
        current = self.load()
        data: Dict[str, Any] = asdict(current)
        data.update(kwargs)
        updated = UserSettings(**data)
        self.save(updated)
        return updated
