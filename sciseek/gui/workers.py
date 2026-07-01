"""Background workers for GUI."""

from __future__ import annotations

from sciseek.core.models import SearchConfig

try:
    from PySide6.QtCore import QObject, Signal, Slot
except Exception:  # pragma: no cover
    QObject = object  # type: ignore
    Signal = object  # type: ignore

    def Slot(*_args, **_kwargs):  # type: ignore
        def _decorator(fn):
            return fn

        return _decorator


class SearchWorker(QObject):
    progress = Signal(str, int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, service, cfg: SearchConfig):
        super().__init__()
        self.service = service
        self.cfg = cfg

    @Slot()
    def run(self) -> None:
        try:
            result = self.service.run(self.cfg, progress=self._on_progress)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_progress(self, evt) -> None:
        self.progress.emit(evt.stage, evt.current, evt.total, evt.message)
