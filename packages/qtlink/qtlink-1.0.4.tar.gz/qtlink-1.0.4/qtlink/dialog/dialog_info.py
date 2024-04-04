from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


def show_dialog_info(text: str, enable_btn_confirm: bool = False, show_or_exec: str = 'exec'):
    dialog = DialogInfo(text, enable_btn_confirm)
    if show_or_exec == 'exec':
        dialog.exec()
    else:
        dialog.show()


class DialogInfo(QDialog):
    def __init__(self, text: str, enable_btn_confirm: bool = False):
        super().__init__()
        vLayout = QVBoxLayout()

        label = QLabel(text, self)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        if enable_btn_confirm:
            btn_confirm = QPushButton('确定', self)
            btn_confirm.clicked.connect(self.close)
            vLayout.addWidget(btn_confirm)

        self.setLayout(vLayout)
