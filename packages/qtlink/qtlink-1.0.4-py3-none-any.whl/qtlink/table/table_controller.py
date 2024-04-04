# -*- coding:utf-8 -*-
from PySide6 import QtGui, QtCore
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QTableView

from qtlink.util import create_signal


class TableController:
    def __init__(self, tableview: QTableView,
                 highlight_hover_row: bool = False):
        self.tableview = tableview
        self.table_columns = None
        self.raw_data = None
        self.column_widths = None
        self.first_load = True
        self.model = QtGui.QStandardItemModel()
        self.signal_click_row = create_signal(dict)
        # 连接信号
        self.tableview.clicked.connect(self.on_table_clicked)
        # 禁止上下文菜单
        scrollBar = self.tableview.verticalScrollBar()
        scrollBar.setContextMenuPolicy(Qt.NoContextMenu)
        scrollBar = self.tableview.horizontalScrollBar()
        scrollBar.setContextMenuPolicy(Qt.NoContextMenu)
        # 启用高亮一整行效果
        if highlight_hover_row:
            self.tableview.setMouseTracking(True)
            self.hover_delegate = HoverDelegate(tableview=tableview)
            self.tableview.entered.connect(self.hover_delegate.on_entered)
        else:
            self.hover_delegate = None

    def update_model_data(self, model_data: list[dict], hide_columns: list[str] = None):
        if hide_columns is None:
            hide_columns = []
        if not self.first_load:
            # 保存当前列宽
            self.save_current_column_widths()
        self.first_load = False

        self.model.clear()
        self.raw_data = model_data
        for data in model_data:
            items = [QStandardItem(str(data[column]) if data[column] is not None else '')
                     for column in self.table_columns
                     if column not in hide_columns]
            self.model.appendRow(items)
        self.update_table_columns(self.table_columns)

    def update_table_columns(self, table_columns: list[str]):
        self.table_columns = table_columns
        self.model.setHorizontalHeaderLabels(table_columns)
        self.tableview.setModel(self.model)

        if self.column_widths is not None:
            for item in self.column_widths:
                index, width = item
                self.tableview.setColumnWidth(index, width)

    def clear_model_data(self):
        self.update_model_data(model_data=[])

    def save_current_column_widths(self):
        if self.column_widths is None:
            return
        for index in range(self.model.columnCount()):
            width = self.tableview.columnWidth(index)
            # 确保保存的列宽信息与列的数量相匹配
            if index < len(self.column_widths):
                self.column_widths[index] = (index, width)
            else:
                self.column_widths.append((index, width))

    def on_table_clicked(self, index):
        # index是QModelIndex类型，可以用来检索数据
        row = index.row()  # 获取行号
        # 获取该行的所有列的数据
        rowData = self.raw_data[row]
        self.signal_click_row.signal.emit(rowData)

    def set_column_width(self, column_widths: list[tuple] = None):
        self.column_widths = column_widths

    def set_select_row(self, index: int):
        if len(self.raw_data) - 1 >= index:
            first_index = self.model.index(index, 0)
            self.tableview.selectionModel().select(first_index,
                                                   QItemSelectionModel.Select | QItemSelectionModel.Rows)

    def set_not_select_row(self, index: int):
        if len(self.raw_data) - 1 >= index:
            first_index = self.model.index(index, 0)
            self.tableview.selectionModel().select(first_index,
                                                   QItemSelectionModel.Deselect | QItemSelectionModel.Rows)

    def __del__(self):
        if self.hover_delegate and self.tableview.viewport():
            self.tableview.viewport().removeEventFilter(self.hover_delegate)


class HoverDelegate(QtCore.QObject):
    def __init__(self, tableview):
        super().__init__(tableview)
        self.tableview = tableview
        self.row_under_mouse = -1
        self.hover_color = QtGui.QColor(240, 240, 240)
        # 安装事件过滤器到表格视图的视口上
        self.tableview.viewport().installEventFilter(self)
        self.is_hovering = False

    def on_entered(self, index):
        self.is_hovering = True
        hover_row = index.row()
        # 检查当前行是否被选中
        is_row_selected = self.tableview.selectionModel().isRowSelected(hover_row, QtCore.QModelIndex())
        if hover_row != self.row_under_mouse:
            # 还原上一行的背景色
            if self.row_under_mouse >= 0:
                self.set_row_background(self.row_under_mouse, self.tableview.palette().base())
            # 重设当前行背景色
            if not is_row_selected:
                self.set_row_background(hover_row, self.hover_color)
                self.row_under_mouse = hover_row
        self.is_hovering = False

    def set_row_background(self, hover_row, color):
        for column in range(self.tableview.model().columnCount()):
            index = self.tableview.model().index(hover_row, column)
            rect = self.tableview.visualRect(index)
            self.tableview.viewport().update(rect)
            self.tableview.model().setData(index, color, Qt.BackgroundRole)

    def clear_hover_style(self):
        if self.row_under_mouse >= 0:
            self.set_row_background(self.row_under_mouse, self.tableview.palette().base())
            self.row_under_mouse = -1
            self.tableview.viewport().update()  # 更新视图以反映背景色的变化

    def eventFilter(self, watched, event):
        if watched and watched == self.tableview.viewport() and event.type() == QtCore.QEvent.Leave:  # noqa
            self.clear_hover_style()
        return super().eventFilter(watched, event)
