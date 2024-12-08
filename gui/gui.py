import asyncio
from re import search
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QMainWindow,
    QListWidget,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from pathlib import Path

from config import MOD_SCAN_DIRS
from mod_manager.mods_handler import get_mods_info
from mod_manager.mod_handler import Mod

class ModWidget(QListWidgetItem):
    def __init__(self,mod: Mod) -> None:
        self.mod = mod

        super().__init__()

        self.setText(self.mod.name)
        self.setToolTip(self.mod.path.as_posix())

class ModListWidget(QListWidget):
    def __init__(self,mods: dict[Path,Mod]) -> None:
        super().__init__()
        self.currentItemChanged.connect(self.index_changed)
        self.setSelectionMode( QtWidgets.QAbstractItemView.ExtendedSelection) # type: ignore
        self.setAlternatingRowColors(True)
        self.setDragEnabled(True)

        for mod in mods.values():
            self.addItem(ModWidget(mod))
    
    def get_mods(self):
        items = []

        for x in range(self.count()-1):
            items.append(self.item(x))
        
        return items
    
    def index_changed(self, index):  # Not an index, index is a QListWidgetItem
        mod_info_widget.update(index.mod)

    def search(self,search_string: str):
        for x in range(self.count()-1):
            item = self.item(x)
            item.setHidden(not item.mod.search_visible(search_string)) # type: ignore

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        print(event)
        return super().dragEnterEvent(event)

class ModListToggler(QVBoxLayout):
    def __init__(self,mods: dict[Path,Mod]) -> None:
        super().__init__()

        # Searchbar
        self.searchbar = QLineEdit()
        self.addWidget(self.searchbar)

        self.searchbar.textChanged.connect(self.search_lists)

        # Modlists
        modlists = QHBoxLayout()

        self.source_mods = ModListWidget(mods)
        modlists.addWidget(self.source_mods)
        
        self.active_mods = ModListWidget({})
        modlists.addWidget(self.active_mods)

        self.addLayout(modlists)

    def search_lists(self):
        search_string = self.searchbar.text()

        self.source_mods.search(search_string)
        self.active_mods.search(search_string)

    def get_active_mods(self) -> dict[Path, Mod]:
        return {item.mod.path: item.mod for item in self.active_mods.get_mods()}

    def move_mods(self,data):
        print(data)
    

class ModInfoWidget(QLabel):
    def __init__(self):
        super().__init__()

    def update(self,mod: Mod):
        self.setText(mod.name)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RimTag")

        self.mods = asyncio.run(get_mods_info(MOD_SCAN_DIRS))

        self.tags_widget = QTabWidget()
        self.tags_widget.setMovable(True)

        for tag_name in ["Biotech","Royalty"]:
            self.make_tag_toggler(tag_name)

        global mod_info_widget
        mod_info_widget = ModInfoWidget() 

        layout = QVBoxLayout()
        layout.addWidget(mod_info_widget)
        layout.addWidget(self.tags_widget)

        widget = QWidget()
        widget.setLayout(layout)

        # In QListWidget there are two separate signals for the item, and the str
        self.setCentralWidget(widget)

    def make_tag_toggler(self,tag_name: str) -> None:
        toggler_widget = QWidget()
        toggler_widget.setLayout(ModListToggler(self.mods))
        self.tags_widget.addTab(toggler_widget,tag_name)

app = QApplication([])