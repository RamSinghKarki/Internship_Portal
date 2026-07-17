"""Main window: sidebar | stacked views | info panel, with background scans.

Scans run on a QThread so the UI stays responsive; the thread emits
progress and a summary, and views refresh when it finishes.
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from ..config import AppConfig
from ..database.session import create_session_factory
from ..services.scan_service import ScanService
from ..themes import load_theme
from ..widgets.info_panel import InfoPanel
from ..widgets.sidebar import Sidebar
from .dashboard_view import DashboardView
from .duplicates_view import DuplicatesView
from .people_view import PeopleView
from .settings_view import SettingsView


class ScanThread(QThread):
    progress = Signal(int, int, str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, config: AppConfig, session_factory, folder: Path):
        super().__init__()
        self.config = config
        self.session_factory = session_factory
        self.folder = folder

    def run(self) -> None:
        try:
            summary = ScanService(self.config, self.session_factory).scan(
                self.folder,
                progress=lambda d, t, p: self.progress.emit(d, t, p),
            )
            self.finished_ok.emit(summary)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        config.ensure_dirs()
        self.session_factory = create_session_factory(config.db_path)
        self._scan_thread: ScanThread | None = None

        self.setWindowTitle("FaceVault")
        self.resize(1280, 800)

        # Toolbar ------------------------------------------------------
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.scan_button = QPushButton("Scan Folder…")
        self.scan_button.setObjectName("primary")
        self.scan_button.clicked.connect(self._pick_folder)
        toolbar.addWidget(self.scan_button)

        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy(),
                             spacer.sizePolicy().verticalPolicy())
        progress_wrap = QWidget()
        wrap_layout = QHBoxLayout(progress_wrap)
        wrap_layout.setContentsMargins(12, 0, 0, 0)
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("subtle")
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(260)
        self.progress_bar.hide()
        wrap_layout.addWidget(self.progress_bar)
        wrap_layout.addWidget(self.progress_label)
        wrap_layout.addStretch()
        toolbar.addWidget(progress_wrap)

        # Views --------------------------------------------------------
        self.sidebar = Sidebar()
        self.stack = QStackedWidget()
        self.info_panel = InfoPanel()

        self.dashboard = DashboardView(config, self.session_factory)
        self.people = PeopleView(config, self.session_factory)
        self.duplicates = DuplicatesView(config, self.session_factory)
        self.settings = SettingsView(config)

        self._sections = {
            "dashboard": self.dashboard,
            "people": self.people,
            "duplicates": self.duplicates,
            "settings": self.settings,
        }
        for view in self._sections.values():
            self.stack.addWidget(view)

        self.sidebar.section_selected.connect(self._switch_section)
        self.people.person_selected.connect(self.info_panel.show_person)
        self.people.data_changed.connect(self.refresh_all)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stack)
        splitter.addWidget(self.info_panel)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(2, True)
        self.setCentralWidget(splitter)

        self.statusBar().showMessage(f"Library: {config.data_dir}")

        if not config.models_available():
            self.statusBar().showMessage(
                f"AI models missing from {config.models_dir} — "
                "run models/download_models.py once, then restart."
            )
            self.scan_button.setEnabled(False)

        self.refresh_all()

    # ---- navigation --------------------------------------------------
    def _switch_section(self, key: str) -> None:
        view = self._sections[key]
        self.stack.setCurrentWidget(view)
        if hasattr(view, "refresh"):
            view.refresh()
        self.info_panel.setVisible(key == "people")

    def refresh_all(self) -> None:
        current = self.stack.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()

    # ---- scanning ----------------------------------------------------
    def _pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose a photo folder")
        if not folder:
            return
        self.scan_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # indeterminate until first tick
        self.progress_label.setText("Discovering images…")

        self._scan_thread = ScanThread(self.config, self.session_factory, Path(folder))
        self._scan_thread.progress.connect(self._on_progress)
        self._scan_thread.finished_ok.connect(self._on_scan_done)
        self._scan_thread.failed.connect(self._on_scan_failed)
        self._scan_thread.start()

    def _on_progress(self, done: int, total: int, path: str) -> None:
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
        self.progress_label.setText(Path(path).name)

    def _on_scan_done(self, summary: dict) -> None:
        self._scan_finished()
        self.refresh_all()
        QMessageBox.information(
            self,
            "Scan complete",
            f"{summary['new_images']} new/updated images "
            f"({summary['skipped']} unchanged skipped)\n"
            f"{summary['faces_found']} faces detected\n"
            f"{summary['faces_matched']} matched to existing people\n"
            f"{summary['new_people']} new people discovered\n"
            f"{summary['unknown_faces']} faces still unknown",
        )

    def _on_scan_failed(self, message: str) -> None:
        self._scan_finished()
        QMessageBox.critical(self, "Scan failed", message)

    def _scan_finished(self) -> None:
        self.scan_button.setEnabled(True)
        self.progress_bar.hide()
        self.progress_label.setText("")
        self._scan_thread = None


def run_gui(config: AppConfig) -> int:
    app = QApplication(sys.argv[:1])
    app.setApplicationName("FaceVault")
    qss = load_theme("dark")
    if qss:
        app.setStyleSheet(qss)
    window = MainWindow(config)
    window.show()
    return app.exec()
