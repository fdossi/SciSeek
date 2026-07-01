"""GUI entrypoint."""

from __future__ import annotations


def run_gui() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("PySide6 nao instalado.") from exc

    from .main_window import MainWindow

    app = QApplication([])
    win = MainWindow()
    win.show()
    return app.exec()
