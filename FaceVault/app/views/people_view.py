"""People grid: one card per person, context menu for rename/merge/delete,
double-click opens the person's photos."""

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..database.models import Face
from ..services.export_service import ExportService
from ..services.people_service import PeopleService
from ..services.thumbnail_service import ThumbnailService
from ..widgets.photo_grid import PhotoGrid
from ..widgets.photo_viewer import PhotoViewerDialog


class PersonPhotosDialog(QDialog):
    def __init__(self, title: str, images: list[tuple[int, str]],
                 thumbs: ThumbnailService, session_factory, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(820, 600)
        layout = QVBoxLayout(self)
        grid = PhotoGrid(thumbs)
        grid.set_images(images)
        grid.open_requested.connect(
            lambda index: PhotoViewerDialog(images, index, session_factory,
                                            config=config, parent=self).exec()
        )
        layout.addWidget(grid)


class PeopleView(QWidget):
    person_selected = Signal(dict, object)  # detail dict, cover Path|None
    data_changed = Signal()

    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory
        self.people_service = PeopleService(config, session_factory)
        self.thumbs = ThumbnailService(config)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("People")
        title.setObjectName("heading")
        layout.addWidget(title)

        self._hint = QLabel("No people yet — scan a folder to discover faces.")
        self._hint.setObjectName("subtle")
        layout.addWidget(self._hint)

        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(140, 140))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSpacing(12)
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self._context_menu)
        self.grid.itemSelectionChanged.connect(self._selection_changed)
        self.grid.itemDoubleClicked.connect(self._open_person)
        layout.addWidget(self.grid)

    # ---- data ---------------------------------------------------------
    def refresh(self) -> None:
        self.grid.clear()
        people = self.people_service.list_people()
        self._hint.setVisible(not people)
        for p in people:
            label = f"{p['name']}\n{p['face_count']} face(s)"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, p["id"])
            cover = self._cover_path(p["cover_face_id"])
            if cover:
                item.setIcon(QIcon(str(cover)))
            item.setSizeHint(QSize(160, 185))
            self.grid.addItem(item)

    def _cover_path(self, cover_face_id: int | None) -> Path | None:
        if cover_face_id is None:
            return None
        with self.session_factory() as session:
            face = session.get(Face, cover_face_id)
            if face is None:
                return None
            return self.thumbs.face_thumbnail(
                face.image.path, (face.x, face.y, face.w, face.h), face.id
            )

    def _selected_person_id(self) -> int | None:
        items = self.grid.selectedItems()
        return items[0].data(Qt.UserRole) if items else None

    # ---- interactions -------------------------------------------------
    def _selection_changed(self) -> None:
        pid = self._selected_person_id()
        if pid is None:
            return
        detail = self.people_service.person_detail(pid)
        with self.session_factory() as session:
            from ..database.repository import Repository

            best = Repository(session).best_face_of_person(pid)
        cover = self._cover_path(best.id if best else None)
        self.person_selected.emit(detail, cover)

    def _open_person(self, item: QListWidgetItem) -> None:
        pid = item.data(Qt.UserRole)
        detail = self.people_service.person_detail(pid)
        dlg = PersonPhotosDialog(
            f"{detail['name']} — {detail['photo_count']} photo(s)",
            detail["images"],
            self.thumbs,
            self.session_factory,
            config=self.config,
            parent=self,
        )
        dlg.exec()

    def _context_menu(self, pos) -> None:
        item = self.grid.itemAt(pos)
        if item is None:
            return
        pid = item.data(Qt.UserRole)
        menu = QMenu(self)
        act_rename = menu.addAction("Rename…")
        act_merge = menu.addAction("Merge into…")
        act_export = menu.addAction("Export photos to folder…")
        act_split = menu.addAction("Split person (wrongly merged look-alikes)…")
        act_delete = menu.addAction("Delete person (faces become unknown)")
        chosen = menu.exec(self.grid.mapToGlobal(pos))

        if chosen is act_rename:
            name, ok = QInputDialog.getText(self, "Rename person", "Name:")
            if ok and name.strip():
                self.people_service.rename(pid, name)
                self.data_changed.emit()
        elif chosen is act_merge:
            others = [p for p in self.people_service.list_people() if p["id"] != pid]
            if not others:
                QMessageBox.information(self, "Merge", "No other person to merge into.")
                return
            labels = [f"{p['name']} ({p['face_count']} faces)" for p in others]
            choice, ok = QInputDialog.getItem(
                self, "Merge person", "Merge into:", labels, 0, False
            )
            if ok:
                target = others[labels.index(choice)]
                self.people_service.merge(pid, target["id"])
                self.data_changed.emit()
        elif chosen is act_export:
            dest = QFileDialog.getExistingDirectory(self, "Export photos to…")
            if dest:
                n = ExportService(self.config, self.session_factory).export_person_photos(
                    pid, Path(dest)
                )
                QMessageBox.information(self, "Export", f"Copied {n} photo(s) to {dest}")
        elif chosen is act_split:
            confirm = QMessageBox.question(
                self, "Split person",
                "Re-cluster this person's faces at a stricter threshold?\n"
                "Distinct sub-groups become separate people; uncertain faces "
                "go to Unknown for review.",
            )
            if confirm == QMessageBox.Yes:
                result = self.people_service.split_person(pid)
                if result["split"]:
                    QMessageBox.information(
                        self, "Split person",
                        f"Created {result['new_people']} new person/people; "
                        f"{result['unassigned']} face(s) moved to Unknown.",
                    )
                else:
                    QMessageBox.information(
                        self, "Split person",
                        "These faces look consistent — nothing to split.",
                    )
                self.data_changed.emit()
        elif chosen is act_delete:
            confirm = QMessageBox.question(
                self, "Delete person",
                "Delete this person? Their faces return to the unknown pool.",
            )
            if confirm == QMessageBox.Yes:
                self.people_service.delete_person(pid)
                self.data_changed.emit()
