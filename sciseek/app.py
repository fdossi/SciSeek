"""Application factories for CLI/GUI."""

from .core.service import SearchService
from .core.settings import SettingsStore, UserPaths


def build_service() -> SearchService:
    paths = UserPaths.detect("SciSeek", "SciSeek")
    settings = SettingsStore(paths.config_file)
    return SearchService(paths=paths, settings_store=settings)
