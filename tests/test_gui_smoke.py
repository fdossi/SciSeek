import importlib.util

import pytest

HAS_PYSIDE = importlib.util.find_spec("PySide6") is not None
HAS_PYTEST_QT = importlib.util.find_spec("pytestqt") is not None


@pytest.mark.skipif(not (HAS_PYSIDE and HAS_PYTEST_QT), reason="PySide6/pytest-qt nao instalado")
def test_gui_window_opens(qtbot):
    from sciseek.gui.main_window import MainWindow

    win = MainWindow()
    qtbot.addWidget(win)
    win.show()
    assert win.isVisible()
