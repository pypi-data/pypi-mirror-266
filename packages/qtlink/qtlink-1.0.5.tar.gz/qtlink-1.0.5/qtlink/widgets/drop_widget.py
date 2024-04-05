# -*- coding:utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from qtlink.util import create_signal


class DropWidget(QWidget):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.signal_accept_path = create_signal(str)

        self.setAcceptDrops(True)
        self.label = QLabel(label, self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            # 处理每个URL，这里只取第一个
            url = mimeData.urls()[0]
            # 转换为本地文件路径（去掉 file:/// 前缀）
            path = url.toLocalFile()
            self.signal_accept_path.signal.emit(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
