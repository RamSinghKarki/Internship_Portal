"""Unknown faces: manually assign auto-ungrouped faces to people.

This closes the loop the automatic clustering can't: singleton faces,
low-quality faces, and genuinely new people get human confirmation here.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..database.repository import Repository
from ..services.people_service import PeopleService
from ..services.thumbnail_service import ThumbnailService


class UnknownFacesView(QWidget):
    data_changed = Signal()

    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory
        self.people = PeopleService(config, session_factory)
        self.thumbs = ThumbnailService(config)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Unknown faces")
        title.setObjectName("heading")
        layout.addWidget(title)

        hint = QLabel(
            "Faces the automatic grouping couldn't confidently place. "
            "Select one or more and assign them."
        )
        hint.setObjectName("subtle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        actions = QHBoxLayout()
        assign_btn = QPushButton("Assign to person…")
        create_btn = QPushButton("New person from selection…")
        create_btn.setObjectName("primary")
        assign_btn.clicked.connect(self._assign_existing)
        create_btn.clicked.connect(self._create_person)
        self._count = QLabel("")
        self._count.setObjectName("subtle")
        actions.addWidget(create_btn)
        actions.addWidget(assign_btn)
        actions.addStretch()
        actions.addWidget(self._count)
        layout.addLayout(actions)

        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(120, 120))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSpacing(10)
        self.grid.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.grid)

    def refresh(self) -> None:
        self.grid.clear()
        with self.session_factory() as session:
            faces = Repository(session).unknown_faces()
            for face in faces:
                thumb = self.thumbs.face_thumbnail(
                    face.image.path, (face.x, face.y, face.w, face.h), face.id
                )
                item = QListWidgetItem(f"q{face.quality:.0f}")
                item.setData(Qt.UserRole, face.id)
                item.setToolTip(face.image.path)
                if thumb:
                    item.setIcon(QIcon(str(thumb)))
                item.setSizeHint(QSize(135, 160))
                self.grid.addItem(item)
        self._count.setText(f"{self.grid.count()} unknown face(s)")

    def _selected_face_ids(self) -> list[int]:
        return [item.data(Qt.UserRole) for item in self.grid.selectedItems()]

    def _assign_existing(self) -> None:
        face_ids = self._selected_face_ids()
        if not face_ids:
            QMessageBox.information(self, "Assign", "Select one or more faces first.")
            return
        people = self.people.list_people()
        if not people:
            QMessageBox.information(
                self, "Assign", "No people exist yet — create one from a selection."
            )
            return
        labels = [f"{p['name']} ({p['face_count']} faces)" for p in people]
        choice, ok = QInputDialog.getItem(
            self, "Assign faces", "Person:", labels, 0, False
        )
        if ok:
            person = people[labels.index(choice)]
            moved = self.people.assign_faces(face_ids, person["id"])
            self.refresh()
            self.data_changed.emit()
            QMessageBox.information(
                self, "Assign", f"Assigned {moved} face(s) to {person['name']}."
            )

    def _create_person(self) -> None:
        face_ids = self._selected_face_ids()
        if not face_ids:
            QMessageBox.information(self, "New person", "Select one or more faces first.")
            return
        name, ok = QInputDialog.getText(
            self, "New person", "Name (optional — leave blank for auto-number):"
        )
        if ok:
            self.people.create_person_from_faces(face_ids, name)
            self.refresh()
            self.data_changed.emit()
