from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QListWidgetItem


class DoubleListWidget(QtWidgets.QWidget):
    item_moved = QtCore.pyqtSignal()

    def __init__(self, comparison=None):
        super().__init__()

        # Store the comparison function
        self._comparison = comparison

        # Create the list widgets
        self._left_list = QtWidgets.QListWidget()
        self._right_list = QtWidgets.QListWidget()

        # Enable multiple selection
        self._left_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        self._right_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )

        # Create the buttons
        self._right_arrow = QtWidgets.QPushButton(">>")
        self._left_arrow = QtWidgets.QPushButton("<<")

        # Connect the buttons to slots
        self._right_arrow.clicked.connect(
            lambda: self.move_items(self._left_list, self._right_list)
        )
        self._left_arrow.clicked.connect(
            lambda: self.move_items(self._right_list, self._left_list)
        )

        # Connect double click event to slots
        self._left_list.itemDoubleClicked.connect(
            lambda: self.move_items(self._left_list, self._right_list)
        )
        self._right_list.itemDoubleClicked.connect(
            lambda: self.move_items(self._right_list, self._left_list)
        )

        # Create a layout for the buttons
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.addWidget(self._right_arrow)
        button_layout.addWidget(self._left_arrow)

        # Create a layout for the lists and buttons
        double_list = QtWidgets.QHBoxLayout()
        double_list.addWidget(self._left_list)
        double_list.addLayout(button_layout)
        double_list.addWidget(self._right_list)

        self.setLayout(double_list)

    def add_items(self, items, item_ids, list_side="left"):
        for item, item_id in zip(items, item_ids):
            self.add_item(item, item_id, list_side)
        self.sort_list(list_side)

    def add_item(self, item, item_id, list_side="left"):
        new_item = QListWidgetItem(item)
        new_item.setData(QtCore.Qt.ItemDataRole.ToolTipRole, item_id)
        if list_side == "left":
            self._left_list.addItem(new_item)
        else:
            self._right_list.addItem(new_item)

    def clear_items(self, list_side="both"):
        if list_side in ["left", "both"]:
            self._left_list.clear()
        if list_side in ["right", "both"]:
            self._right_list.clear()

    def get_selected_items(self, list_side="right"):
        list_widget = self._right_list if list_side == "right" else self._left_list
        return [
            list_widget.item(i).data(QtCore.Qt.ItemDataRole.ToolTipRole)
            for i in range(list_widget.count())
        ]

    def move_items(self, source, destination):
        items = source.selectedItems()
        if items:
            for item in items:
                source.takeItem(source.row(item))
                destination.addItem(item)
            self.item_moved.emit()
            # Whenever move item is used it first appends to the bottom then sorts the given list
            self.sort_list("right" if source is self._left_list else "left")

    def sort_list(self, list_side):
        # Sorts list based on the given comparison function.
        list_widget = self._left_list if list_side == "left" else self._right_list
        items = [(list_widget.item(i).text(), list_widget.item(i).data(QtCore.Qt.ItemDataRole.ToolTipRole)) for i in range(list_widget.count())]
        items.sort(key=lambda item: item[0] if self._comparison is None else self._comparison(item[0]))
        list_widget.clear()
        for item in items:
            new_item = QListWidgetItem(item[0])
            new_item.setData(QtCore.Qt.ItemDataRole.ToolTipRole, item[1])
            list_widget.addItem(new_item)
