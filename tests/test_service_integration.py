from pathlib import Path

from sciseek.core.models import SearchConfig, SearchMode
from sciseek.core.service import SearchService
from sciseek.core.settings import SettingsStore, UserPaths


def _service(tmp_path: Path) -> SearchService:
    paths = UserPaths(
        config_dir=tmp_path / "cfg",
        cache_dir=tmp_path / "cache",
        data_dir=tmp_path / "data",
        log_dir=tmp_path / "logs",
    )
    for p in [paths.config_dir, paths.cache_dir, paths.data_dir, paths.log_dir, paths.default_exports]:
        p.mkdir(parents=True, exist_ok=True)
    return SearchService(paths=paths, settings_store=SettingsStore(paths.config_file))


def test_end_to_end_txt_md(tmp_path: Path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "a.txt").write_text("alpha beta gamma", encoding="utf-8")
    (root / "b.md").write_text("# title\n\nalpha only", encoding="utf-8")

    service = _service(tmp_path)
    cfg = SearchConfig(
        root=root,
        file_formats=["txt", "md"],
        mode=SearchMode.SIMPLE,
        terms=["alpha"],
        use_cache=False,
        output_format="json",
        output_dir=tmp_path / "out",
    )
    result = service.run(cfg)
    assert result.summary.total_discovered == 2
    assert result.summary.total_matched >= 1
    assert result.summary.output_file is not None
    assert result.summary.output_file.exists()


def test_cache_toggle_and_invalidation(tmp_path: Path):
    root = tmp_path / "corpus"
    root.mkdir()
    file_path = root / "a.txt"
    file_path.write_text("alpha", encoding="utf-8")

    service = _service(tmp_path)
    cfg = SearchConfig(
        root=root,
        file_formats=["txt"],
        mode=SearchMode.SIMPLE,
        terms=["alpha"],
        use_cache=True,
        output_dir=tmp_path / "out",
    )
    service.run(cfg)
    stats1 = service.cache_stats()
    assert stats1["entries"] >= 1

    file_path.write_text("alpha delta", encoding="utf-8")
    second = service.run(cfg)
    assert second.summary.total_matched >= 1

    cfg_no_cache = SearchConfig(
        root=root,
        file_formats=["txt"],
        mode=SearchMode.SIMPLE,
        terms=["alpha"],
        use_cache=False,
        output_dir=tmp_path / "out",
    )
    service.run(cfg_no_cache)
