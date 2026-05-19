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
        # 移除布局内边距，让图表填满容器
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建matplotlib图表对象：figsize=(3,3) 设定图表尺寸（宽3英寸，高3英寸）
        # plt.subplots()返回：画布 (figure) + 绘图区域 (ax)
        self.figure, self.ax = plt.subplots(figsize=(3, 3))

        # 设置图表背景透明，匹配UI
        # 把最外层画布的背景设为透明，patch = 画布的背景层
        self.figure.patch.set_facecolor('none')
        # 把内部绘图区域的背景也设为透明
        self.ax.set_facecolor('none')

        # matplotlib是电脑绘图工具，Qt无法识别
        # FigureCanvas把matplotlib的图表，包装成一个 Qt 能显示的控件，self.canvas表示这个控件
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 从学生模中导入偏好种类
        self.labels = [pref.value for pref in PreferenceType]
        # 蓝, 红, 绿, 橙
        self.colors = ['#00BFFF', '#FF6B6B', '#8FBC8F', '#FFA500']
        # 初始默认数据，渲染初始画面
        # 删掉的话需要等数据更改才会出现饼图
        self.update_chart([25, 25, 25, 25])

    # 饼图更新函数
    def update_chart(self, sizes):
        self.ax.clear()
        # 绘制饼图：带白色边框
        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=self.labels,
            colors=self.colors,
            autopct='%1.0f%%', # 在饼图内部显示的百分比格式
            startangle=140, # # 饼图起始角度（140度，让第一个扇区从非水平位置开始）
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}, # 设置饼块的样式：白色边框，边框宽度 2 像素
            textprops={'fontsize': 8, 'fontweight': 'bold'} # 文字样式：字号8，加粗
        )
        # 自动调整布局（避免标签/百分比文字溢出）
        self.figure.tight_layout()
        # 刷新画布，渲染新图表
        self.canvas.draw()