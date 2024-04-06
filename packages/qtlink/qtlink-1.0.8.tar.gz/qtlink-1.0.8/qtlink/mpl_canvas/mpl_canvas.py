from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class MplCanvas(QWidget):
    def __init__(self, enable_toolbar: bool = True, parent=None):
        super(MplCanvas, self).__init__(parent)

        self.canvas = FigureCanvas(Figure(figsize=(5, 4), constrained_layout=True))
        self.ax = self.canvas.figure.subplots()

        self.vertical_layout = QVBoxLayout()
        if enable_toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.vertical_layout.addWidget(self.toolbar)
        self.vertical_layout.addWidget(self.canvas)
        self.setLayout(self.vertical_layout)

    def clear_canvas(self):
        self.canvas.figure.clear()
        self.ax = self.canvas.figure.subplots()
        self.canvas.draw_idle()

    def plot_lines(self, data: list[dict],
                   x_label: str = '',
                   y_label: str = '',
                   title: str = ''):

        enable_legend = False
        for item in data:
            if item.get('label'):
                enable_legend = True
                self.ax.plot(item['x'], item['y'], marker='o', markersize=3, label=item['label'])
            else:
                self.ax.plot(item['x'], item['y'], marker='o', markersize=3)

        # 设置轴标签和标题
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(title)
        if enable_legend:
            self.ax.legend(loc="upper left")
        self.canvas.draw_idle()
