import sys
import tempfile
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def main() -> int:
    from sciseek.core.models import SearchConfig, SearchMode
    from sciseek.core.service import SearchService
    from sciseek.core.settings import SettingsStore, UserPaths

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        corpus = base / "corpus"
        corpus.mkdir()
        (corpus / "paper 1.txt").write_text("microplastic tendon histology", encoding="utf-8")

        paths = UserPaths(base / "cfg", base / "cache", base / "data", base / "logs")
        for p in [paths.config_dir, paths.cache_dir, paths.data_dir, paths.log_dir, paths.default_exports]:
            p.mkdir(parents=True, exist_ok=True)

        service = SearchService(paths=paths, settings_store=SettingsStore(paths.config_file))
        cfg = SearchConfig(
            root=corpus,
            file_formats=["txt"],
            mode=SearchMode.SIMPLE,
            terms=["microplastic", "tendon"],
            output_format="json",
            output_dir=base / "out",
        )
        result = service.run(cfg)
        assert result.summary.total_matched >= 1

        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance() or QApplication([])
            app.quit()
        except Exception:
            pass

    print("smoke-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
