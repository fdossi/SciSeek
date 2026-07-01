import subprocess
import sys
from pathlib import Path


def test_legacy_wrapper_quick(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [sys.executable, str(repo / "research_searcher.py"), "--quick"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    # pode retornar 0/1/2 dependendo do historico e de erros de processamento, mas nao deve quebrar por import
    assert proc.returncode in {0, 1, 2}
    assert "Traceback" not in proc.stderr
