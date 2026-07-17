"""Duplicates: exact (sha256) and near (dHash) duplicate groups."""

from pathlib import Path

from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from ..ai.duplicate_detector import near_duplicate_groups
from ..config import AppConfig
from ..database.models import Image
from ..database.repository import Repository


class DuplicatesView(QWidget):
    def __init__(self, config: AppConfig, session_factory, parent=None):
        super().__init__(parent)
        self.config = config
        self.session_factory = session_factory

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Duplicates")
        title.setObjectName("heading")
        layout.addWidget(title)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Size", "Resolution"])
        self.tree.setColumnWidth(0, 480)
        layout.addWidget(self.tree)

    def refresh(self) -> None:
        self.tree.clear()
        with self.session_factory() as session:
            repo = Repository(session)

            exact_root = QTreeWidgetItem(["Exact duplicates (identical bytes)"])
            self.tree.addTopLevelItem(exact_root)
            exact_groups = repo.exact_duplicate_groups()
            exact_paths: set[frozenset[str]] = set()
            for group in exact_groups:
                exact_paths.add(frozenset(i.path for i in group))
                node = QTreeWidgetItem([f"{len(group)} copies"])
                exact_root.addChild(node)
                for img in group:
                    node.addChild(self._image_item(img))
            if not exact_groups:
                exact_root.addChild(QTreeWidgetItem(["none found"]))

            near_root = QTreeWidgetItem(["Near duplicates (resized / re-encoded)"])
            self.tree.addTopLevelItem(near_root)
            near = near_duplicate_groups(
                repo.images_with_phash(), max_distance=self.config.near_duplicate_distance
            )
            shown = 0
            for ids in near:
                images = [session.get(Image, i) for i in ids]
                images = [i for i in images if i is not None]
                # Skip groups that are exactly the same as an exact-dup group.
                if frozenset(i.path for i in images) in exact_paths:
                    continue
                node = QTreeWidgetItem([f"{len(images)} similar images"])
                near_root.addChild(node)
                for img in images:
                    node.addChild(self._image_item(img))
                shown += 1
            if shown == 0:
                near_root.addChild(QTreeWidgetItem(["none found"]))

        self.tree.expandToDepth(0)

    @staticmethod
    def _image_item(img: Image) -> QTreeWidgetItem:
        size = f"{(img.size_bytes or 0) / 1024:.0f} KB"
        res = f"{img.width}×{img.height}" if img.width else ""
        item = QTreeWidgetItem([Path(img.path).name, size, res])
        item.setToolTip(0, img.path)
        return item
