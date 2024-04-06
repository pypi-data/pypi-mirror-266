# -*- coding:utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QTableView

from qtlink.table.table_controller import TableController
from qtlink.util import create_signal


class SingleSelectTableController(TableController):
    def __init__(self, tableview: QTableView):
        super().__init__(tableview)
        self.model.itemChanged.connect(self.on_item_changed)
        self.signal_select_row = create_signal(dict)

    def update_model_data(self, model_data: list[dict], hide_columns: list[str] = None):
        # 断开信号连接
        self.model.itemChanged.disconnect(self.on_item_changed)

        if hide_columns is None:
            hide_columns = []
        if not self.first_load:
            # 保存当前列宽
            self.save_current_column_widths()
        self.first_load = False

        self.model.clear()
        self.raw_data = model_data
        for data in model_data:
            items = [QStandardItem(str(data.get(column, None)) if data.get(column, None) is not None else '')
                     for column in self.table_columns
                     if column not in hide_columns]
            items[0].setCheckable(True)
            self.model.appendRow(items)
        self.update_table_columns(self.table_columns)
        # 重新连接信号
        self.model.itemChanged.connect(self.on_item_changed)
        self.on_item_changed()

    def on_item_changed(self, item: QStandardItem = None):
        if item is None or item.checkState() != Qt.Checked:
            return

        for row in range(self.model.rowCount()):
            if self.model.item(row, 0) != item:
                self.model.item(row, 0).setCheckState(Qt.Unchecked)

        self.signal_select_row.signal.emit(self.raw_data[item.row()])

    def get_checked_row(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)  # 勾选框在第一列
            if item.checkState() == Qt.Checked:
                return self.raw_data[row]
