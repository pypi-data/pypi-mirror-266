from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


def show_dialog_choice(text: str, click_btn_confirm, show_or_exec: str = 'exec'):
    dialog = DialogChoice(text, click_btn_confirm)
    if show_or_exec == 'exec':
        dialog.exec()
    else:
        dialog.show()


class DialogChoice(QDialog):
    def __init__(self, text: str, click_btn_confirm):
        super().__init__()
        vLayout = QVBoxLayout()
        self.click_btn_confirm = click_btn_confirm
        label = QLabel(text, self)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        hLayout = QHBoxLayout()
        btn_confirm = QPushButton('确定', self)
        btn_confirm.clicked.connect(self.on_clicked_btn_confirm)
        hLayout.addWidget(btn_confirm)

        btn_cancel = QPushButton('取消', self)
        btn_cancel.clicked.connect(self.close)
        hLayout.addWidget(btn_cancel)
        vLayout.addLayout(hLayout)

        self.setLayout(vLayout)

    def on_clicked_btn_confirm(self):
        self.click_btn_confirm()
        self.close()
