# ui/charts.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.student import PreferenceType

# ===== 新增下面这两行代码来配置中文字体 =====
# 按顺序尝试加载：微软雅黑 -> 黑体 -> 苹果中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决有时候负号无法正常显示的问题
# ============================================

class PreferencePieChart(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure, self.ax = plt.subplots(figsize=(3, 3))
        # 设置图表背景透明，匹配UI
        self.figure.patch.set_facecolor('none')
        self.ax.set_facecolor('none')

        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 初始默认数据 (等比)
        self.labels = [pref.value for pref in PreferenceType]
        self.colors = ['#00BFFF', '#FF6B6B', '#8FBC8F', '#FFA500']  # 蓝, 红, 绿, 橙 (对应概念图)
        self.update_chart([25, 25, 25, 25])

    def update_chart(self, sizes):
        self.ax.clear()
        # 绘制饼图：带白色边框，类似概念图
        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=self.labels,
            colors=self.colors,
            autopct='%1.0f%%',
            startangle=140,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            textprops={'fontsize': 8, 'fontweight': 'bold'}
        )
        self.figure.tight_layout()
        self.canvas.draw()