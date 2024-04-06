# -*- coding:utf-8 -*-
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QLabel, QListWidgetItem, \
    QAbstractItemView, QHBoxLayout, QSpacerItem, QSizePolicy

scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: #F1F1F1;
    width: 12px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #CCCCCC;
    min-height: 20px;
}

QScrollBar:horizontal {
    border: none;
    background: #F1F1F1;
    height: 12px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:horizontal {
    background: #CCCCCC;
    min-width: 20px;
}
"""

list_widget_style = """
QListWidget::item:hover {
    background-color: rgb(240, 240, 240);
    border: none;
    outline: none;
}

QListWidget::item:selected {
    background-color: rgb(220, 220, 220);
    border: none;
    outline: none;
}

QListWidget:focus {
    outline: none;
}

"""


class CustomWidget(QWidget):
    def __init__(self, dict_item):
        super().__init__()
        path = dict_item['path']
        time = dict_item['time']
        self.subtitle = path
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # 创建水平布局
        hLayout = QHBoxLayout()

        # 创建垂直布局并添加标签
        vLayout = QVBoxLayout()
        titleLabel = QLabel(os.path.basename(path), self)
        subtitleLabel = QLabel(path, self)
        subtitleLabel.setStyleSheet("color: rgb(150, 150, 150);")

        vLayout.addWidget(titleLabel)
        vLayout.addWidget(subtitleLabel)

        # 将垂直布局添加到水平布局的左侧
        hLayout.addLayout(vLayout)

        # 添加水平弹簧到水平布局
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hLayout.addSpacerItem(spacer)

        # 添加一个新的标签到水平布局的右侧
        label_time = QLabel(format_timestamp_in_record(time), self)
        label_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label_time.setStyleSheet("color: rgb(150, 150, 150);")

        hLayout.addWidget(label_time)

        # 设置CustomWidget的主布局为hLayout
        self.setLayout(hLayout)


class ListWidget(QWidget):
    """只是容器"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # 创建QListWidget
        self.listWidget = QListWidget(self)
        layout.addWidget(self.listWidget)
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距为0
        layout.setSpacing(0)  # 设置布局内部组件间的间距为0
        self.setLayout(layout)
        self.setStyleSheet("QWidget { border: none; }")
        # 应用滚动条样式
        self.listWidget.verticalScrollBar().setStyleSheet(scrollbar_style)
        self.listWidget.horizontalScrollBar().setStyleSheet(scrollbar_style)
        self.listWidget.setStyleSheet(list_widget_style)
        # 设置像素级的垂直滚动
        self.listWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)  # noqa

    def add_widgets(self, widgets: list):
        self.listWidget.clear()
        for widget in widgets:
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)
