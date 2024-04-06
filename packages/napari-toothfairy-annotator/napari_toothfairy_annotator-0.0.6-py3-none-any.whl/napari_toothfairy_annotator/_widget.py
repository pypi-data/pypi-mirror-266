import os
import json
import numpy as np
from pathlib import Path
# from napari_plugin_engine import napari_hook_implementation

from qtpy.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QFileSystemModel
)
from qtpy.QtCore import  (
    QDir,
    QModelIndex,
    QPoint,
    QRegExp,
    QSortFilterProxyModel,
    Qt,
)
from qtpy.QtGui import (
    QColor,
    QPainter,
    QIcon,
)

from napari.viewer import Viewer
from magicgui.widgets import FileEdit
from magicgui.types import FileDialogMode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from qtpy.QtCore import QModelIndex

from napari_toothfairy_annotator.FDI_Annotator import FDI_Annotator

class ColorWidgetItem(QListWidgetItem):
    def __init__(self, text, color):
        super().__init__(text)
        self.color = color

    def paint(self, painter):
        painter.fillRect(self.rect().adjusted(0, 0, -50, 0), self.color)
        super().paint(painter)


class WidgetAnnotator(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.fdi_annotator = FDI_Annotator()
        self.associations = {0: "00"}
        self._available_ids = None

        self.load_associated_volume()

        self.viewer.layers.move_multiple([0,2,1])

        layout = QVBoxLayout()

        self.list1 = QListWidget()
        # self.list1.setSortingEnabled(True)
        layout.addWidget(self.list1)

        self.list2 = QListWidget()
        self.list2.setSortingEnabled(True)
        layout.addWidget(self.list2)
        self.list2.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )

        self.associate_button = QPushButton("Associate IDs")
        self.associate_button.clicked.connect(self.associate_ids)
        layout.addWidget(self.associate_button)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload)
        layout.addWidget(self.reload_button)

        self.setLayout(layout)
        self.load_associations()
        self.update_lists()


    def reload(self,):
        source = self.get_source()
        annotation_npy_path = os.path.join(source, 'annotation.npy')

        if not os.path.isfile(annotation_npy_path):
            print('path not found on reload')
            return

        self.load_associations()
        self.viewer.layers.remove('annotation')
        annotation = np.load(annotation_npy_path)

        keys = self.associations.keys()
        print(keys)
        for key in keys:
            mask = annotation == int(key)
            annotation[mask] = 0

        self.viewer.add_labels(annotation, name='annotation', visible=True)


    def load_associated_volume(self,):
        source = self.get_source()
        associated_volume_path = os.path.join(source, 'associated.npy')
        if os.path.isfile(associated_volume_path):
            self.associated_volume = np.load(associated_volume_path)
        else:
            self.associated_volume = np.zeros_like(self.viewer.layers['annotation'].data)
        self.viewer.add_labels(self.associated_volume, name='associated', visible=False)

    def associate_ids(self):
        selected_items_list1 = self.list1.selectedItems()
        selected_items_list2 = self.list2.selectedItems()

        for item1 in selected_items_list1:
            for item2 in selected_items_list2:
                fdi_id = self.fdi_annotator.inverse[item1.text()]['ID']
                self.associations[int(item2.text())] = fdi_id
                mask = self.viewer.layers['annotation'].data == int(item2.text())
                self.viewer.layers['annotation'].data[mask] = 0
                self.viewer.layers['associated'].data[mask] = int(fdi_id)
        self.viewer.layers['annotation'].refresh()
        self.viewer.layers['associated'].refresh()
        self.update_lists()
        self.save()

    def get_source(self,):
        source = self.viewer.layers['annotation'].source.path
        if source is None:
            source = self.viewer.layers['volume'].source.path
        if source is None:
            source = self.viewer.layers['annotation'].metadata['parent_folder']
        if source is None:
            source = self.viewer.layers['volume'].metadata['parent_folder']

        assert source is not None, "I tried so hard and got so far but in the end it doesn't even matter"

        return source


    def save(self,):
        data = self.viewer.layers['associated'].data
        source = self.get_source()

        save_path = os.path.join(source, 'associated.npy')
        np.save(save_path, data)
        association_file = os.path.join(source, 'associations.json')
        with open(association_file, 'w') as f:
            json.dump(self.associations, f)


    def load_associations(self,):
        source = self.get_source()
        association_file = os.path.join(source, 'associations.json')

        if not os.path.isfile(association_file):
            return

        with open(association_file) as f:
            print('Load associations.json')
            str_id_associations = json.load(f)
            self.associations = {}
            for k, v in str_id_associations.items():
                self.associations[int(k)] = v

        for left_id, right_id in self.associations.items():
            mask = self.viewer.layers['annotation'].data == int(left_id)
            self.viewer.layers['annotation'].data[mask] = 0
        self.viewer.layers['annotation'].refresh()


    def update_lists(self):
        self.list1.clear()
        self.list2.clear()

        for id_data in self.get_fdi_ids():
            item = ColorWidgetItem(id_data['name'], QColor("white"))
            self.list1.addItem(item)

        already_annotated = set(self.associations.keys())
        print(f'already_annotated: {already_annotated}')

        for id_data in self.get_available_ids():
            s = f'{id_data}'
            if int(id_data) in already_annotated:
                assoc_id = self.associations[int(id_data)]
                s += f' > {self.fdi_annotator.fdi_notation[assoc_id]["name"]}'
            item = ColorWidgetItem(s, QColor("red"))
            self.list2.addItem(item)

    def get_available_ids(self,):
        if self._available_ids is None:
            data = self.viewer.layers['annotation'].data
            self._available_ids = np.unique(data).tolist()
            self._available_ids += self.associations.keys()
            self._available_ids = list(set(self._available_ids))
        return self._available_ids

    def get_fdi_ids(self,):
        return self.fdi_annotator.fdi_notation.values()

    def get_available_layers(self,):
        return [layer.name for layer in self.viewer.layers]


class DirectoryFriendlyFilterProxyModel(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Accepts directories and files that pass the base class's filter
        
        Note: This custom proxy ensures that we can search for filenames and keep the directories
        in the tree view
        """
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)

        if model.isDir(index):
            return True

        return super().filterAcceptsRow(source_row, source_parent)


class FolderBrowser(QWidget):
    """Main Widget for the Folder Browser Dock Widget
    
    The napari viewer is passed in as an argument to the constructor
    """
    viewer: Viewer
    folder_chooser: FileEdit
    file_system_model: QFileSystemModel
    proxy_model: DirectoryFriendlyFilterProxyModel
    search_field: QLineEdit
    tree_view: QTreeView
    annotator_widget: WidgetAnnotator

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.setLayout(QVBoxLayout())

        current_directory: Path = Path(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.layout().addWidget(QLabel("Directory"))
        self.folder_chooser = FileEdit(
            mode=FileDialogMode.EXISTING_DIRECTORY,
            value=current_directory,
        )
        self.layout().addWidget(self.folder_chooser.native)

        def directory_changed(*_) -> None:
            current_directory = Path(self.folder_chooser.value)
            self.tree_view.setRootIndex(
                self.proxy_model.mapFromSource(
                    self.file_system_model.index(current_directory.as_posix())
                )
            )

        self.folder_chooser.line_edit.changed.connect(directory_changed)

        # --------------------------------------------
        # File system abstraction with proxy for search filtering
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.proxy_model = DirectoryFriendlyFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_system_model)

        # Create search box and connect to proxy model
        self.layout().addWidget(QLabel("File filter"))
        self.search_field = QLineEdit()
        # Note: We should agree on the best regex interaction to provide here
        def update_filter(text: str) -> None:
            self.proxy_model.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
        self.search_field.textChanged.connect(update_filter)
        search_widget = QWidget()
        search_widget.setLayout(QHBoxLayout())
        search_widget.layout().addWidget(QLabel("Search:"))
        search_widget.layout().addWidget(self.search_field)
        self.layout().addWidget(search_widget)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setRootIndex(
            self.proxy_model.mapFromSource(
                self.file_system_model.index(current_directory.as_posix())
            )
        )
    
        self.tree_view.doubleClicked.connect(self.__tree_double_click)

        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        self.layout().addWidget(self.tree_view)

        self.annotator_widget = None


    def __tree_double_click(self, index: QModelIndex) -> None:
        """Action on double click in the tree model
        
        Opens the selected file or in the folder
        
        Args:
            index: Index of the selected item in the tree view
        """

        source_index: QModelIndex = self.proxy_model.mapToSource(index)
        file_path: str = self.file_system_model.filePath(source_index)

        if self.file_system_model.isDir(source_index):
            if self.annotator_widget is not None:
                self.layout().removeWidget(self.annotator_widget)
                self.annotator_widget = None

            layers_to_remove = self.viewer.layers.copy()
            for layer in layers_to_remove:
                self.viewer.layers.remove(layer)

            print(f'Layers: {len(self.viewer.layers)}')

            self.viewer.open(file_path, plugin='napari-toothfairy-annotator')
            self.annotator_widget = WidgetAnnotator(self.viewer)
            self.layout().addWidget(self.annotator_widget)

    def __show_context_menu(self, position: QPoint) -> None:
        """Show a context menu when right-clicking in the tree view"""
        menu = QMenu()
        open_multiple_action = menu.addAction("Open multiple files")
        open_multiple_action.triggered.connect(
            lambda: self.__open_multi_selection(is_stack=False)
        )
        open_as_stack_action = menu.addAction("Open as stack")
        open_as_stack_action.triggered.connect(
            lambda: self.__open_multi_selection(is_stack=True)
        )

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def __open_multi_selection(self, is_stack: bool) -> None:
        """Open multiple files in the viewer
        
        The files are selected in the tree view
        
        Args:
            is_stack: If True, the files are opened as a stack
        """
        indices: list[QModelIndex] = self.tree_view.selectionModel().selectedIndexes()
        fs_paths: list[str] = [
            self.file_system_model.filePath(self.proxy_model.mapToSource(index)) for index in indices
            if not self.file_system_model.isDir(self.proxy_model.mapToSource(index)) and index.column() == 0
        ]

        # Nothing to do when there is no file selected
        if len(fs_paths) == 0:
            return

        self.viewer.open(fs_paths, stack=is_stack)


# @napari_hook_implementation
# def napari_experimental_provide_dock_widget():
#     return [FolderBrowser]
