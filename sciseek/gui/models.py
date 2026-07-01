"""Qt table models for SciSeek GUI."""

from __future__ import annotations

from typing import List

from sciseek.core.models import DocumentResult

try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
except Exception:  # pragma: no cover
    QAbstractTableModel = object  # type: ignore
    QModelIndex = object  # type: ignore
    Qt = object  # type: ignore


class ResultsTableModel(QAbstractTableModel):
    headers = ["Arquivo", "Caminho", "Formato", "Termos", "Ocorrencias", "Score"]

    def __init__(self):
        super().__init__()
        self._rows: List[DocumentResult] = []

    def set_rows(self, rows: List[DocumentResult]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent=None):  # noqa: N802
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=None):  # noqa: N802
        parent = parent or QModelIndex()
        return 0 if parent.isValid() else len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # noqa: N802
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[section]
        return section + 1

    def data(self, index, role=Qt.DisplayRole):  # noqa: N802
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        if col == 0:
            return row.file_path.name
        if col == 1:
            return str(row.file_path)
        if col == 2:
            return row.format_type
        if col == 3:
            return ", ".join(row.matched_terms)
        if col == 4:
            return row.match_count
        if col == 5:
            return row.match_count + len(row.matched_terms)
        return None

    def get_row(self, row_idx: int) -> DocumentResult | None:
        if 0 <= row_idx < len(self._rows):
            return self._rows[row_idx]
        return None
