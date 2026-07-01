"""Main window for SciSeek GUI."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from sciseek.app import build_service
from sciseek.core.models import DocumentResult, SearchConfig, SearchMode

from .models import ResultsTableModel
from .workers import SearchWorker

try:
    from PySide6.QtCore import QSortFilterProxyModel, Qt, QThread
    from PySide6.QtGui import QAction, QDesktopServices
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMenu,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QSplitter,
        QTableView,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover
    QMainWindow = object  # type: ignore


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.service = build_service()
        self.worker_thread = None
        self.worker = None
        self.last_config: SearchConfig | None = None
        self._docs: list[DocumentResult] = []

        self.model = ResultsTableModel()
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        self._build_ui()
        self._refresh_history()

    def _build_ui(self) -> None:
        self.setWindowTitle("SciSeek")
        self.resize(1220, 780)

        root = QWidget(self)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        header_box = QHBoxLayout()
        header = QLabel("SciSeek - Busca local em documentos cientificos")
        header.setStyleSheet("font-size: 18px; font-weight: 600;")
        header_box.addWidget(header)

        self.new_btn = QPushButton("Nova busca")
        self.new_btn.clicked.connect(self._reset_form)
        self.open_result_btn = QPushButton("Abrir resultado")
        self.open_result_btn.clicked.connect(self._open_last_output)
        self.settings_btn = QPushButton("Configuracoes")
        self.settings_btn.clicked.connect(self._show_settings)
        self.help_btn = QPushButton("Ajuda")
        self.help_btn.clicked.connect(self._show_help)

        for b in [self.new_btn, self.open_result_btn, self.settings_btn, self.help_btn]:
            header_box.addWidget(b)
        layout.addLayout(header_box)

        split = QSplitter(Qt.Horizontal)
        layout.addWidget(split)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        form = QGridLayout()
        self.root_edit = QLineEdit(str(Path.cwd()))
        browse = QPushButton("Selecionar pasta")
        browse.clicked.connect(self._pick_root)

        self.formats_edit = QLineEdit("pdf,docx,md,txt")
        self.terms_edit = QTextEdit()
        self.terms_edit.setPlaceholderText("Um termo por linha")

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["simple", "regex", "proximity", "boolean"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)

        self.boolean_edit = QLineEdit()
        self.boolean_edit.setPlaceholderText("Expressao booleana (modo boolean)")

        self.proximity_edit = QLineEdit("10")
        self.context_edit = QLineEdit("20")

        self.cache_check = QCheckBox("Usar cache")
        self.cache_check.setChecked(True)
        self.recursive_check = QCheckBox("Busca recursiva")
        self.recursive_check.setChecked(True)
        self.hidden_check = QCheckBox("Incluir ocultos")
        self.case_check = QCheckBox("Case sensitive")

        self.output_format = QComboBox()
        self.output_format.addItems(["markdown", "csv", "json", "html", "bibtex"])
        self.output_dir = QLineEdit(str(self.service.paths.default_exports))
        out_dir_btn = QPushButton("Pasta de saida")
        out_dir_btn.clicked.connect(self._pick_output_dir)

        form.addWidget(QLabel("Pasta"), 0, 0)
        form.addWidget(self.root_edit, 0, 1)
        form.addWidget(browse, 0, 2)
        form.addWidget(QLabel("Formatos"), 1, 0)
        form.addWidget(self.formats_edit, 1, 1, 1, 2)
        form.addWidget(QLabel("Modo"), 2, 0)
        form.addWidget(self.mode_combo, 2, 1)
        form.addWidget(QLabel("Booleano"), 3, 0)
        form.addWidget(self.boolean_edit, 3, 1, 1, 2)
        form.addWidget(QLabel("Proximidade (palavras)"), 4, 0)
        form.addWidget(self.proximity_edit, 4, 1)
        form.addWidget(QLabel("Contexto"), 4, 2)
        form.addWidget(self.context_edit, 4, 3)
        form.addWidget(QLabel("Termos"), 5, 0)
        form.addWidget(self.terms_edit, 5, 1, 1, 3)
        form.addWidget(self.cache_check, 6, 0)
        form.addWidget(self.recursive_check, 6, 1)
        form.addWidget(self.hidden_check, 6, 2)
        form.addWidget(self.case_check, 6, 3)
        form.addWidget(QLabel("Saida"), 7, 0)
        form.addWidget(self.output_format, 7, 1)
        form.addWidget(self.output_dir, 7, 2)
        form.addWidget(out_dir_btn, 7, 3)

        left_layout.addLayout(form)

        controls = QHBoxLayout()
        self.run_btn = QPushButton("Iniciar busca")
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._start)
        self.cancel_btn.clicked.connect(self._cancel)

        self.repeat_btn = QPushButton("Repetir ultima")
        self.repeat_btn.clicked.connect(self._repeat_last)

        controls.addWidget(self.run_btn)
        controls.addWidget(self.cancel_btn)
        controls.addWidget(self.repeat_btn)
        left_layout.addLayout(controls)

        hist_box = QGroupBox("Historico")
        hist_layout = QVBoxLayout(hist_box)
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._history_run_selected)

        hist_btns = QHBoxLayout()
        self.history_reload = QPushButton("Atualizar")
        self.history_reload.clicked.connect(self._refresh_history)
        self.history_delete = QPushButton("Remover")
        self.history_delete.clicked.connect(self._delete_selected_history)
        self.history_clear = QPushButton("Limpar")
        self.history_clear.clicked.connect(self._clear_history)
        hist_btns.addWidget(self.history_reload)
        hist_btns.addWidget(self.history_delete)
        hist_btns.addWidget(self.history_clear)

        hist_layout.addWidget(self.history_list)
        hist_layout.addLayout(hist_btns)
        left_layout.addWidget(hist_box)

        split.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        filter_bar = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filtrar resultados...")
        self.filter_edit.textChanged.connect(self.proxy.setFilterFixedString)

        self.group_combo = QComboBox()
        self.group_combo.addItems(["Sem agrupamento", "Por formato", "Por termo"])
        self.group_combo.currentTextChanged.connect(self._apply_grouping)

        filter_bar.addWidget(QLabel("Filtro"))
        filter_bar.addWidget(self.filter_edit)
        filter_bar.addWidget(QLabel("Agrupar"))
        filter_bar.addWidget(self.group_combo)
        right_layout.addLayout(filter_bar)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_table_menu)
        self.table.selectionModel().selectionChanged.connect(self._show_details)
        right_layout.addWidget(self.table)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Detalhes e trechos aparecerao aqui")
        right_layout.addWidget(self.details)

        split.addWidget(right)
        split.setSizes([500, 700])

        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.status = QLabel("Pronto")
        layout.addWidget(self.status)

        self._on_mode_changed(self.mode_combo.currentText())

    def _reset_form(self) -> None:
        self.terms_edit.clear()
        self.boolean_edit.clear()
        self.filter_edit.clear()
        self.details.clear()
        self._docs = []
        self.model.set_rows([])
        self.status.setText("Pronto")
        self.progress.setValue(0)

    def _pick_root(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Selecionar pasta", self.root_edit.text())
        if p:
            self.root_edit.setText(p)

    def _pick_output_dir(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Saida", self.output_dir.text())
        if p:
            self.output_dir.setText(p)

    def _on_mode_changed(self, mode: str) -> None:
        is_boolean = mode == "boolean"
        self.boolean_edit.setEnabled(is_boolean)
        self.terms_edit.setEnabled(not is_boolean)

    def _build_config(self) -> SearchConfig:
        terms = [t.strip() for t in self.terms_edit.toPlainText().splitlines() if t.strip()]
        return SearchConfig(
            root=Path(self.root_edit.text()).resolve(),
            file_formats=[f.strip() for f in self.formats_edit.text().split(",") if f.strip()],
            mode=SearchMode(self.mode_combo.currentText()),
            terms=terms,
            boolean_query=self.boolean_edit.text().strip(),
            recursive=self.recursive_check.isChecked(),
            ignore_hidden=not self.hidden_check.isChecked(),
            case_sensitive=self.case_check.isChecked(),
            use_cache=self.cache_check.isChecked(),
            output_format=self.output_format.currentText(),
            output_dir=Path(self.output_dir.text()).resolve() if self.output_dir.text().strip() else None,
            proximity_words=max(1, int(self.proximity_edit.text() or "10")),
            context_words=max(5, int(self.context_edit.text() or "20")),
        )

    def _start(self) -> None:
        try:
            cfg = self._build_config()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", str(exc))
            return
        self._run_with_config(cfg)

    def _run_with_config(self, cfg: SearchConfig) -> None:
        self.last_config = cfg
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status.setText("Executando...")
        self.progress.setValue(0)

        self.worker_thread = QThread(self)
        self.worker = SearchWorker(self.service, cfg)
        self.worker.moveToThread(self.worker_thread)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def _repeat_last(self) -> None:
        if self.last_config is None:
            QMessageBox.information(self, "Info", "Nenhuma busca anterior nesta sessao.")
            return
        self._run_with_config(self.last_config)

    def _cancel(self) -> None:
        self.service.cancel()
        self.status.setText("Cancelando...")

    def _on_progress(self, stage: str, current: int, total: int, message: str) -> None:
        if total > 0:
            self.progress.setValue(int((current / total) * 100))
        self.status.setText(f"{stage}: {message} ({current}/{total})")

    def _on_finished(self, run_result) -> None:
        self._docs = run_result.documents
        self._apply_grouping(self.group_combo.currentText())
        self.status.setText(
            f"Concluido. {run_result.summary.total_matched} documentos encontrados. Saida: {run_result.summary.output_file}"
        )
        self.progress.setValue(100)
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._refresh_history()
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def _on_failed(self, message: str) -> None:
        self.status.setText(f"Erro: {message}")
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.critical(self, "Falha", message)
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()

    def _show_details(self, *_args) -> None:
        idx = self.table.currentIndex()
        if not idx.isValid():
            return
        src = self.proxy.mapToSource(idx)
        row = self.model.get_row(src.row())
        if row is None:
            return
        lines = [
            f"Arquivo: {row.file_path.name}",
            f"Caminho: {row.file_path}",
            f"Formato: {row.format_type}",
            f"Termos: {', '.join(row.matched_terms)}",
            f"Ocorrencias: {row.match_count}",
        ]

        if row.metadata:
            lines.extend(["", "Metadados:"])
            for k, v in row.metadata.items():
                lines.append(f"- {k}: {v}")

        lines.extend(["", "Trechos:"])
        for occ in row.occurrences[:20]:
            lines.append(f"- [{occ.term}] x{occ.count}: {occ.snippet}")
        self.details.setPlainText("\n".join(lines))

    def _open_table_menu(self, pos) -> None:
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return
        src = self.proxy.mapToSource(idx)
        row = self.model.get_row(src.row())
        if row is None:
            return

        menu = QMenu(self)
        copy_path = QAction("Copiar caminho", self)
        open_file = QAction("Abrir arquivo", self)
        open_folder = QAction("Abrir pasta", self)

        copy_path.triggered.connect(lambda: self._copy_text(str(row.file_path)))
        open_file.triggered.connect(lambda: self._open_file(row.file_path))
        open_folder.triggered.connect(lambda: self._open_folder(row.file_path.parent))

        menu.addAction(copy_path)
        menu.addAction(open_file)
        menu.addAction(open_folder)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _copy_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)

    def _open_file(self, path: Path) -> None:
        QDesktopServices.openUrl(path.as_uri())

    def _open_folder(self, path: Path) -> None:
        if os.name == "nt":
            subprocess.run(["explorer", str(path)], check=False)
        else:
            QDesktopServices.openUrl(path.as_uri())

    def _open_last_output(self) -> None:
        records = self.service.history_records(limit=1)
        if not records:
            QMessageBox.information(self, "Info", "Sem resultados no historico.")
            return
        out = records[0].entry.output_file
        if not out:
            QMessageBox.information(self, "Info", "Ultima execucao sem arquivo de saida.")
            return
        path = Path(out)
        if not path.exists():
            QMessageBox.warning(self, "Aviso", "Arquivo nao encontrado no caminho salvo.")
            return
        self._open_file(path)

    def _apply_grouping(self, mode: str) -> None:
        docs = list(self._docs)
        if mode == "Por formato":
            docs.sort(key=lambda d: (d.format_type.lower(), -d.match_count, d.file_path.name.lower()))
        elif mode == "Por termo":
            docs.sort(
                key=lambda d: (
                    (d.matched_terms[0].lower() if d.matched_terms else ""),
                    -d.match_count,
                    d.file_path.name.lower(),
                )
            )
        self.model.set_rows(docs)

    def _refresh_history(self) -> None:
        self.history_list.clear()
        for rec in self.service.history_records(limit=100):
            e = rec.entry
            text = f"#{rec.row_id} | {e.run_at} | {e.mode} | {e.total_matched}/{e.total_processed} | {e.output_file}"
            self.history_list.addItem(text)

    def _selected_history_id(self) -> int | None:
        item = self.history_list.currentItem()
        if item is None:
            return None
        text = item.text()
        try:
            return int(text.split("|")[0].strip().lstrip("#"))
        except Exception:
            return None

    def _history_run_selected(self, item=None) -> None:
        if item is None:
            item = self.history_list.currentItem()
        if item is None:
            return
        parts = item.text().split("|")
        if len(parts) < 5:
            return
        out = parts[-1].strip()
        if out and Path(out).exists():
            self._open_file(Path(out))

    def _delete_selected_history(self) -> None:
        row_id = self._selected_history_id()
        if row_id is None:
            QMessageBox.information(self, "Info", "Selecione um item do historico.")
            return
        self.service.delete_history_entry(row_id)
        self._refresh_history()

    def _clear_history(self) -> None:
        if QMessageBox.question(self, "Confirmar", "Limpar todo o historico?") != QMessageBox.Yes:
            return
        self.service.clear_history()
        self._refresh_history()

    def _show_settings(self) -> None:
        settings = self.service.get_settings()
        QMessageBox.information(
            self,
            "Configuracoes",
            (
                f"Idioma: {settings.language}\n"
                f"Tema: {settings.theme}\n"
                f"Cache padrao: {settings.cache_enabled}\n"
                f"Proximidade: {settings.proximity_words}\n"
                f"Contexto: {settings.context_words}"
            ),
        )

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Ajuda",
            (
                "1) Selecione pasta e formatos.\n"
                "2) Informe termos (um por linha) ou expressao booleana.\n"
                "3) Clique em Iniciar busca.\n"
                "4) Use filtro, detalhes e menu de contexto para explorar resultados."
            ),
        )
