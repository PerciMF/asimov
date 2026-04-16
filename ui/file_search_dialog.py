from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
)

from tools.file_search_tool import (
    EXTENSOES_SUPORTADAS,
    FileSearchTool,
    SearchCancellationToken,
    SearchConfig,
    summarize_results,
)


class SearchWorker(QObject):
    progress = Signal(int, int, str, int, int)
    log = Signal(str)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, tool: FileSearchTool, config: SearchConfig, cancellation_token: SearchCancellationToken):
        super().__init__()
        self.tool = tool
        self.config = config
        self.cancellation_token = cancellation_token

    def run(self) -> None:
        try:
            resultados, origem_cache, cancelled = self.tool.search(
                config=self.config,
                progress_callback=lambda idx, total, arquivo, ocorrencias, erros: self.progress.emit(idx, total, str(arquivo), ocorrencias, erros),
                log_callback=self.log.emit,
                cancellation_token=self.cancellation_token,
            )
            exportado = self.tool.export_results(self.config, resultados, origem_cache, cancelled=cancelled)
            summary = summarize_results(self.config, resultados, origem_cache, cancelled=cancelled)
            self.finished.emit({"resultados": resultados, "origem_cache": origem_cache, "cancelled": cancelled, "summary": summary, "exportado": exportado})
        except Exception as exc:
            self.failed.emit(str(exc))


class FileSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscador de Arquivos")
        self.resize(980, 700)
        self.setMinimumSize(860, 600)

        self.tool = FileSearchTool()
        self.execution_summary = ""
        self.exported_path = ""
        self._thread: QThread | None = None
        self._cancel_token: SearchCancellationToken | None = None
        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🔎 Buscador Inteligente de Arquivos")
        title.setObjectName("title")
        subtitle = QLabel("Pesquisa em TXT, DOCX, XLSX/XLSM e PDF, com exportação dos resultados para Excel.")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setSpacing(10)
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText("Ex.: bomba, contrato, TAG-101...")
        form.addRow("Termo:", self.term_input)

        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)
        btn_folder = QPushButton("Selecionar pasta")
        btn_folder.clicked.connect(self.select_folder)
        folder_row.addWidget(btn_folder)
        form.addRow("Origem:", folder_row)

        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_input)
        btn_output = QPushButton("Selecionar saída")
        btn_output.clicked.connect(self.select_output)
        output_row.addWidget(btn_output)
        form.addRow("Saída:", output_row)
        layout.addWidget(form_widget)

        self.progress_overall = QProgressBar()
        self.status_label = QLabel("Aguardando execução...")
        self.summary_label = QLabel(f"Extensões suportadas: {', '.join(sorted(EXTENSOES_SUPORTADAS))}")
        layout.addWidget(QLabel("Progresso geral:"))
        layout.addWidget(self.progress_overall)
        layout.addWidget(self.status_label)
        layout.addWidget(self.summary_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Tipo", "Local", "Arquivo", "Status"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QLabel("Log da execução:"))
        layout.addWidget(self.log, 1)
        layout.addWidget(QLabel("Painel visual de resultados:"))
        layout.addWidget(self.results_table, 1)

        buttons = QHBoxLayout()
        self.search_button = QPushButton("🚀 Iniciar Busca")
        self.search_button.clicked.connect(self.start_search)
        self.cancel_button = QPushButton("⛔ Cancelar")
        self.cancel_button.clicked.connect(self.cancel_search)
        self.cancel_button.setEnabled(False)
        self.open_button = QPushButton("📂 Abrir exportado")
        self.open_button.clicked.connect(self.open_exported)
        self.open_button.setEnabled(False)
        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.reset)
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close)
        for btn in [self.search_button, self.cancel_button, self.open_button, clear_button, close_button]:
            buttons.addWidget(btn)
        layout.addLayout(buttons)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QDialog { background-color: #10161F; color: #E8F4FF; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #7FDBFF; }
            QLineEdit, QTextEdit, QTableWidget {
                background-color: #0D141C;
                color: #E8F4FF;
                border: 1px solid #35516B;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1D4E89;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2565AE; }
            QProgressBar {
                border: 1px solid #35516B;
                border-radius: 8px;
                background-color: #0D141C;
                text-align: center;
                min-height: 18px;
            }
            QProgressBar::chunk { background-color: #29B6F6; border-radius: 7px; }
            """
        )

    def append_log(self, message: str) -> None:
        self.log.append(message)
        QApplication.processEvents()

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de origem")
        if folder:
            self.folder_input.setText(folder)

    def select_output(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(self, "Salvar resultados como", str(Path.home() / "resultado_busca.xlsx"), "Excel (*.xlsx)")
        if filepath:
            self.output_input.setText(filepath)

    def validate_config(self) -> SearchConfig | None:
        termo = self.term_input.text().strip()
        pasta = self.folder_input.text().strip()
        saida = self.output_input.text().strip()
        if not termo:
            QMessageBox.warning(self, "Aviso", "Informe o termo da busca.")
            return None
        if not pasta:
            QMessageBox.warning(self, "Aviso", "Selecione a pasta de origem.")
            return None
        if not Path(pasta).exists():
            QMessageBox.warning(self, "Aviso", "A pasta informada não existe.")
            return None
        if not saida:
            QMessageBox.warning(self, "Aviso", "Selecione o arquivo de saída.")
            return None
        return SearchConfig(termo=termo, pasta=pasta, saida=saida)

    def on_progress(self, idx: int, total: int, arquivo: str, ocorrencias: int, erros: int) -> None:
        percent = int((idx / total) * 100) if total else 0
        self.progress_overall.setValue(percent)
        self.status_label.setText(f"{percent}% - Processando: {Path(arquivo).name}")
        self.summary_label.setText(f"Arquivos processados: {idx}/{total} | Ocorrências: {ocorrencias} | Erros: {erros}")
        QApplication.processEvents()

    def _populate_results(self, resultados: list) -> None:
        self.results_table.setRowCount(0)
        for item in resultados[:100]:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(item.tipo))
            self.results_table.setItem(row, 1, QTableWidgetItem(item.local))
            self.results_table.setItem(row, 2, QTableWidgetItem(Path(item.arquivo).name))
            self.results_table.setItem(row, 3, QTableWidgetItem(item.status))

    def start_search(self) -> None:
        config = self.validate_config()
        if config is None:
            return
        if self._thread is not None:
            QMessageBox.information(self, "Execução", "Já existe uma busca em andamento.")
            return
        self.search_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_overall.setValue(0)
        self.log.clear()
        self.results_table.setRowCount(0)
        self.status_label.setText("Preparando execução em thread...")
        self._cancel_token = SearchCancellationToken()
        worker = SearchWorker(self.tool, config, self._cancel_token)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.on_progress)
        worker.log.connect(self.append_log)
        worker.finished.connect(self.on_finished)
        worker.failed.connect(self.on_failed)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        thread.start()

    def cancel_search(self) -> None:
        if self._cancel_token is None:
            return
        self._cancel_token.cancel()
        self.append_log("Cancelamento solicitado pelo usuário.")
        self.status_label.setText("Cancelamento solicitado...")

    def on_finished(self, payload: dict) -> None:
        self.execution_summary = payload["summary"]
        self.exported_path = payload["exportado"]
        self._populate_results(payload["resultados"])
        self.progress_overall.setValue(100)
        self.status_label.setText("Concluído" if not payload["cancelled"] else "Cancelado com exportação parcial")
        self.summary_label.setText(f"Total de registros exportados: {len(payload['resultados'])}")
        self.append_log(f"Resultado salvo em: {self.exported_path}")
        self.open_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self._thread is not None:
            self._thread.quit()
  from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
)

from tools.file_search_tool import (
    EXTENSOES_SUPORTADAS,
    FileSearchTool,
    SearchCancellationToken,
    SearchConfig,
    summarize_results,
)


class SearchWorker(QObject):
    progress = Signal(int, int, str, int, int)
    log = Signal(str)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, tool: FileSearchTool, config: SearchConfig, cancellation_token: SearchCancellationToken):
        super().__init__()
        self.tool = tool
        self.config = config
        self.cancellation_token = cancellation_token

    def run(self) -> None:
        try:
            resultados, origem_cache, cancelled = self.tool.search(
                config=self.config,
                progress_callback=lambda idx, total, arquivo, ocorrencias, erros: self.progress.emit(idx, total, str(arquivo), ocorrencias, erros),
                log_callback=self.log.emit,
                cancellation_token=self.cancellation_token,
            )
            exportado = self.tool.export_results(self.config, resultados, origem_cache, cancelled=cancelled)
            summary = summarize_results(self.config, resultados, origem_cache, cancelled=cancelled)
            self.finished.emit({"resultados": resultados, "origem_cache": origem_cache, "cancelled": cancelled, "summary": summary, "exportado": exportado})
        except Exception as exc:
            self.failed.emit(str(exc))


class FileSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscador de Arquivos")
        self.resize(980, 700)
        self.setMinimumSize(860, 600)

        self.tool = FileSearchTool()
        self.execution_summary = ""
        self.exported_path = ""
        self._thread: QThread | None = None
        self._cancel_token: SearchCancellationToken | None = None
        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🔎 Buscador Inteligente de Arquivos")
        title.setObjectName("title")
        subtitle = QLabel("Pesquisa em TXT, DOCX, XLSX/XLSM e PDF, com exportação dos resultados para Excel.")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setSpacing(10)
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText("Ex.: bomba, contrato, TAG-101...")
        form.addRow("Termo:", self.term_input)

        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.folder_input)
        btn_folder = QPushButton("Selecionar pasta")
        btn_folder.clicked.connect(self.select_folder)
        folder_row.addWidget(btn_folder)
        form.addRow("Origem:", folder_row)

        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_input)
        btn_output = QPushButton("Selecionar saída")
        btn_output.clicked.connect(self.select_output)
        output_row.addWidget(btn_output)
        form.addRow("Saída:", output_row)
        layout.addWidget(form_widget)

        self.progress_overall = QProgressBar()
        self.status_label = QLabel("Aguardando execução...")
        self.summary_label = QLabel(f"Extensões suportadas: {', '.join(sorted(EXTENSOES_SUPORTADAS))}")
        layout.addWidget(QLabel("Progresso geral:"))
        layout.addWidget(self.progress_overall)
        layout.addWidget(self.status_label)
        layout.addWidget(self.summary_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["Tipo", "Local", "Arquivo", "Status"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QLabel("Log da execução:"))
        layout.addWidget(self.log, 1)
        layout.addWidget(QLabel("Painel visual de resultados:"))
        layout.addWidget(self.results_table, 1)

        buttons = QHBoxLayout()
        self.search_button = QPushButton("🚀 Iniciar Busca")
        self.search_button.clicked.connect(self.start_search)
        self.cancel_button = QPushButton("⛔ Cancelar")
        self.cancel_button.clicked.connect(self.cancel_search)
        self.cancel_button.setEnabled(False)
        self.open_button = QPushButton("📂 Abrir exportado")
        self.open_button.clicked.connect(self.open_exported)
        self.open_button.setEnabled(False)
        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.reset)
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.close)
        for btn in [self.search_button, self.cancel_button, self.open_button, clear_button, close_button]:
            buttons.addWidget(btn)
        layout.addLayout(buttons)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QDialog { background-color: #10161F; color: #E8F4FF; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #7FDBFF; }
            QLineEdit, QTextEdit, QTableWidget {
                background-color: #0D141C;
                color: #E8F4FF;
                border: 1px solid #35516B;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1D4E89;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2565AE; }
            QProgressBar {
                border: 1px solid #35516B;
                border-radius: 8px;
                background-color: #0D141C;
                text-align: center;
                min-height: 18px;
            }
            QProgressBar::chunk { background-color: #29B6F6; border-radius: 7px; }
            """
        )

    def append_log(self, message: str) -> None:
        self.log.append(message)
        QApplication.processEvents()

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de origem")
        if folder:
            self.folder_input.setText(folder)

    def select_output(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(self, "Salvar resultados como", str(Path.home() / "resultado_busca.xlsx"), "Excel (*.xlsx)")
        if filepath:
            self.output_input.setText(filepath)

    def validate_config(self) -> SearchConfig | None:
        termo = self.term_input.text().strip()
        pasta = self.folder_input.text().strip()
        saida = self.output_input.text().strip()
        if not termo:
            QMessageBox.warning(self, "Aviso", "Informe o termo da busca.")
            return None
        if not pasta:
            QMessageBox.warning(self, "Aviso", "Selecione a pasta de origem.")
            return None
        if not Path(pasta).exists():
            QMessageBox.warning(self, "Aviso", "A pasta informada não existe.")
            return None
        if not saida:
            QMessageBox.warning(self, "Aviso", "Selecione o arquivo de saída.")
            return None
        return SearchConfig(termo=termo, pasta=pasta, saida=saida)

    def on_progress(self, idx: int, total: int, arquivo: str, ocorrencias: int, erros: int) -> None:
        percent = int((idx / total) * 100) if total else 0
        self.progress_overall.setValue(percent)
        self.status_label.setText(f"{percent}% - Processando: {Path(arquivo).name}")
        self.summary_label.setText(f"Arquivos processados: {idx}/{total} | Ocorrências: {ocorrencias} | Erros: {erros}")
        QApplication.processEvents()

    def _populate_results(self, resultados: list) -> None:
        self.results_table.setRowCount(0)
        for item in resultados[:100]:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(item.tipo))
            self.results_table.setItem(row, 1, QTableWidgetItem(item.local))
            self.results_table.setItem(row, 2, QTableWidgetItem(Path(item.arquivo).name))
            self.results_table.setItem(row, 3, QTableWidgetItem(item.status))

    def start_search(self) -> None:
        config = self.validate_config()
        if config is None:
            return
        if self._thread is not None:
            QMessageBox.information(self, "Execução", "Já existe uma busca em andamento.")
            return
        self.search_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_overall.setValue(0)
        self.log.clear()
        self.results_table.setRowCount(0)
        self.status_label.setText("Preparando execução em thread...")
        self._cancel_token = SearchCancellationToken()
        worker = SearchWorker(self.tool, config, self._cancel_token)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.on_progress)
        worker.log.connect(self.append_log)
        worker.finished.connect(self.on_finished)
        worker.failed.connect(self.on_failed)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        thread.start()

    def cancel_search(self) -> None:
        if self._cancel_token is None:
            return
        self._cancel_token.cancel()
        self.append_log("Cancelamento solicitado pelo usuário.")
        self.status_label.setText("Cancelamento solicitado...")

    def on_finished(self, payload: dict) -> None:
        self.execution_summary = payload["summary"]
        self.exported_path = payload["exportado"]
        self._populate_results(payload["resultados"])
        self.progress_overall.setValue(100)
        self.status_label.setText("Concluído" if not payload["cancelled"] else "Cancelado com exportação parcial")
        self.summary_label.setText(f"Total de registros exportados: {len(payload['resultados'])}")
        self.append_log(f"Resultado salvo em: {self.exported_path}")
        self.open_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(1000)
            self._thread = None
        QMessageBox.information(self, "Concluído", f"Busca finalizada.\n\nArquivo salvo em:\n{self.exported_path}")

    def on_failed(self, error: str) -> None:
        QMessageBox.critical(self, "Erro", f"Falha ao executar a busca:\n\n{error}")
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(1000)
            self._thread = None

    def open_exported(self) -> None:
        if not self.exported_path:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.exported_path).resolve())))

    def reset(self) -> None:
        self.execution_summary = ""
        self.exported_path = ""
        self.term_input.clear()
        self.folder_input.clear()
        self.output_input.clear()
        self.progress_overall.setValue(0)
        self.status_label.setText("Aguardando execução...")
        self.summary_label.setText(f"Extensões suportadas: {', '.join(sorted(EXTENSOES_SUPORTADAS))}")
        self.log.clear()
        self.results_table.setRowCount(0)
        self.open_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)          self._thread.wait(1000)
            self._thread = None
        QMessageBox.information(self, "Concluído", f"Busca finalizada.\n\nArquivo salvo em:\n{self.exported_path}")

    def on_failed(self, error: str) -> None:
        QMessageBox.critical(self, "Erro", f"Falha ao executar a busca:\n\n{error}")
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(1000)
            self._thread = None

    def open_exported(self) -> None:
        if not self.exported_path:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.exported_path).resolve())))

    def reset(self) -> None:
        self.execution_summary = ""
        self.exported_path = ""
        self.term_input.clear()
        self.folder_input.clear()
        self.output_input.clear()
        self.progress_overall.setValue(0)
        self.status_label.setText("Aguardando execução...")
        self.summary_label.setText(f"Extensões suportadas: {', '.join(sorted(EXTENSOES_SUPORTADAS))}")
        self.log.clear()
        self.results_table.setRowCount(0)
        self.open_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
