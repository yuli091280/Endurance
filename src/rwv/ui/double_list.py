from enum import IntEnum, auto
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QListWidgetItem


class Side(IntEnum):
    """
    Enum to reference the side of a doubleList
    """

    LEFT = auto()
    RIGHT = auto()
    BOTH = auto()


class DoubleListWidget(QtWidgets.QWidget):
    """
    Double List UI Widget

    :param comparison: An optional function to use when comparing items
    :type comparison: function or None
    """
    item_moved = QtCore.pyqtSignal(Side, list)
    """signals for when items are moved in a doublelist"""

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

    def add_items(self, items, item_ids, list_side=Side.LEFT):
        """
        Add a list of items and item_ids to a list side.

        :param items: List of strings to add
        :type items: list[str]
        :param item_ids: Item ids that will use to reference the associated items
        :type item_ids: list[str]
        :param list_side: Where the added items will be added... 'left' or 'right'
        :type list_side: Side
        """
        for item, item_id in zip(items, item_ids):
            self.add_item(item, item_id, list_side)
        self.sort_list(list_side)

    def add_item(self, item, item_id, list_side=Side.LEFT):
        """
        Add a list of items and item_ids to a list side.

        :param item: Item string that will show on the list
        :type item: str
        :param item_id: Item ID that will use to reference the item
        :type item_id: list[str]
        :param list_side: Where the added item will be added... 'left' or 'right'
        :type list_side: Side
        """
        new_item = QListWidgetItem(item)
        new_item.setData(QtCore.Qt.ItemDataRole.ToolTipRole, item_id)
        if list_side == Side.LEFT:
            self._left_list.addItem(new_item)
        else:
            self._right_list.addItem(new_item)

    def clear_items(self, list_side=Side.BOTH):
        """
        Clear the items on a specific side or both.

        :param list_side: Which list will be clear... 'left', 'right' or 'both'
        :type list_side: Side
        """
        if list_side in [Side.LEFT, Side.BOTH]:
            self._left_list.clear()
        if list_side in [Side.RIGHT, Side.BOTH]:
            self._right_list.clear()

    def get_selected_items(self, list_side=Side.RIGHT):
        """
        Return the selected item ids on a specific side or both.

        :param list_side: Which list will the selected item ids be returned... 'left', 'right' or 'both'
        :type list_side: Side
        :return: The selected item ids
        :rtype: list[int]
        """
        list_widget = self._right_list if list_side == Side.RIGHT else self._left_list
        return [
            list_widget.item(i).data(QtCore.Qt.ItemDataRole.ToolTipRole)
            for i in range(list_widget.count())
        ]

    def move_items(self, source, destination):
        """
        Move the selected items from source to destination.

        :param source: The source list to get the selected items from
        :type source: PyQt6.QtWidgets.QListWidget
        :param destination: The destination list to move the selected items to
        :type source: PyQt6.QtWidgets.QListWidget
        """
        items = source.selectedItems()
        if len(items) == 0:
            return

        moved_ids = []
        for item in items:
            source.takeItem(source.row(item))
            destination.addItem(item)
            moved_ids.append(item.data(QtCore.Qt.ItemDataRole.ToolTipRole))

        destination_side = Side.RIGHT if source is self._left_list else Side.LEFT
        self.item_moved.emit(destination_side, moved_ids)
        # Whenever move item is used it first appends to the bottom then sorts the given list
        self.sort_list(destination_side)

    def sort_list(self, list_side):
        """
        Sort the list based on ID or the passed comparison function.

        :param list_side: Which list will be sorted... 'left', 'right' or 'both'
        :type list_side: Side
        """
        # Sorts list based on the given comparison function.
        list_widget = self._left_list if list_side == Side.LEFT else self._right_list
        items = [
            (
                list_widget.item(i).text(),
                list_widget.item(i).data(QtCore.Qt.ItemDataRole.ToolTipRole),
            )
            for i in range(list_widget.count())
        ]
        items.sort(
            key=lambda item: item[1]
            if self._comparison is None
            else self._comparison(item[1])
        )
        list_widget.clear()
        for item in items:
            new_item = QListWidgetItem(item[0])
            new_item.setData(QtCore.Qt.ItemDataRole.ToolTipRole, item[1])
            list_widget.addItem(new_item)
