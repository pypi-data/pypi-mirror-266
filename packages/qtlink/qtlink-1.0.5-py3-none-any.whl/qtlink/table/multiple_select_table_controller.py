# -*- coding:utf-8 -*-
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QTableView, QStyleOptionButton, QStyle, QHeaderView

from qtlink.table.table_controller import TableController
from qtlink.util import create_signal


class MultipleSelectTableController(TableController):
    def __init__(self, tableview: QTableView):
        super().__init__(tableview)
        self.model.itemChanged.connect(self.on_item_changed)
        self.signal_select_rows = create_signal(list)

        self.header = CustomHeader(toggle_check_state=self.toggle_check_state, parent=self.tableview)
        self.tableview.setHorizontalHeader(self.header)

        self.always_checked_data = []

    def update_model_data(self, model_data: list[dict],
                          hide_columns: list[str] = None,
                          always_checked_data: list = None):
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
        self.always_checked_data = always_checked_data if always_checked_data else []
        for data in model_data:
            items = [QStandardItem(str(data[column]) if data[column] else '')
                     for column in self.table_columns
                     if column not in hide_columns]
            items[0].setCheckable(True)
            if data in self.always_checked_data:
                items[0].setCheckState(Qt.Checked)
                # 禁用交互
                for item in items:
                    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)

            self.model.appendRow(items)
        self.update_table_columns(self.table_columns)
        # 重新连接信号
        self.model.itemChanged.connect(self.on_item_changed)
        self.on_item_changed()

    def toggle_check_state(self, is_checked):
        # 断开信号连接
        self.model.itemChanged.disconnect(self.on_item_changed)

        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            # 重设勾选状态
            if self.raw_data[row] not in self.always_checked_data:
                item.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)

        # 重新连接信号
        self.model.itemChanged.connect(self.on_item_changed)
        self.on_item_changed()

    def get_checked_rows(self):
        checked_rows = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)  # 勾选框在第一列
            if item.checkState() == Qt.Checked:
                checked_rows.append(self.raw_data[row])
        return checked_rows

    def on_item_changed(self, item: QStandardItem = None):
        if self.hover_delegate is not None and self.hover_delegate.is_hovering:
            return

        checked_rows = self.get_checked_rows()
        self.signal_select_rows.signal.emit(checked_rows)
        checked_rows_num = len(checked_rows)
        if checked_rows_num and checked_rows_num == len(self.raw_data):
            self.set_header_check_state(True)
        else:
            self.set_header_check_state(False)

    def set_header_check_state(self, is_checked: bool):
        self.header.update_check_state(is_checked)


class CustomHeader(QHeaderView):
    def __init__(self, toggle_check_state, orientation=Qt.Horizontal, parent=None):
        super(CustomHeader, self).__init__(orientation, parent)
        self.isChecked = False  # 初始化复选框状态为未选中
        self.toggle_check_state = toggle_check_state

    def update_check_state(self, is_checked):
        self.isChecked = is_checked
        self.updateSection(0)

    def mouseReleaseEvent(self, event):
        # 处理鼠标释放事件，用于切换表头复选框的状态
        index = self.logicalIndexAt(event.position().toPoint())
        if index == 0:
            self.update_check_state(not self.isChecked)  # 切换复选框状态
            self.toggle_check_state(self.isChecked)  # 更新模型中所有项的复选框状态
        else:
            super(CustomHeader, self).mouseReleaseEvent(event)

    def paintSection(self, painter, rect, logicalIndex):
        # 绘制表头的每一部分，用于绘制复选框
        painter.save()
        super(CustomHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        # 如果是第一列，绘制复选框
        if logicalIndex == 0:
            option = QStyleOptionButton()
            checkbox_width = 10  # 复选框宽度
            checkbox_height = 10  # 复选框高度
            checkbox_x = rect.x() + 3  # 复选框的水平位置
            checkbox_y = rect.y() + (rect.height() - checkbox_height) / 2  # 复选框的垂直位置
            option.rect = QRect(checkbox_x, checkbox_y, checkbox_width, checkbox_height)
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isChecked:
                option.state |= QStyle.State_On  # 设置复选框为选中状态
            else:
                option.state |= QStyle.State_Off  # 设置复选框为未选中状态
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)  # 绘制复选框
