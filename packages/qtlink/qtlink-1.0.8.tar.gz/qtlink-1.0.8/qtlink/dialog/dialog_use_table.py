from PySide6.QtWidgets import QDialog, QTableView, QLabel, QVBoxLayout

from qtlink.table.multiple_select_table_controller import MultipleSelectTableController
from qtlink.table.single_select_table_controller import SingleSelectTableController
from qtlink.table.table_controller import TableController


def show_dialog_use_table(text: str, table_data: list[dict], table_columns, show_or_exec: str = 'exec'):
    dialog = DialogUseTable(text, table_data=table_data, table_columns=table_columns)
    if show_or_exec == 'exec':
        dialog.exec()
    else:
        dialog.show()


class DialogUseTable(QDialog):
    def __init__(self, text: str, table_data: list[dict], table_columns, table_type: str = 'no_select', parent=None):
        super().__init__(parent)
        vLayout = QVBoxLayout()
        label = QLabel(text, self)
        label.setWordWrap(True)
        self.tableview = QTableView(self)
        vLayout.addWidget(label)
        vLayout.addWidget(self.tableview)
        self.setLayout(vLayout)
        if table_type == 'no_select':
            self.table_controller = TableController(tableview=self.tableview)
        elif table_type == 'single_select':
            self.table_controller = SingleSelectTableController(tableview=self.tableview)
        elif table_type == 'multiple_select':
            self.table_controller = MultipleSelectTableController(tableview=self.tableview)
        else:
            self.table_controller = TableController(tableview=self.tableview)
        self.update_table_columns(table_columns)
        self.update_table_data(table_data)

    def update_table_columns(self, table_columns):
        self.table_controller.update_table_columns(table_columns=table_columns)

    def update_table_data(self, table_data):
        self.table_controller.update_model_data(model_data=table_data)
