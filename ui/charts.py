# ui/charts.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.student import PreferenceType
from core.student_generator import DistributionType

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


class DistributionLineChart(QWidget):
    """人流分布函数曲线图组件，显示所选分布类型的学生到达人数随时间变化曲线"""

    def __init__(self):
        super().__init__()
        # 默认显示二次函数倒U型曲线
        self.distribution_type = DistributionType.QUADRATIC
        self._init_ui()

    def _init_ui(self):
        """初始化matplotlib图表和布局"""
        layout = QVBoxLayout(self)
        # 移除边距让图表填满窗口
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建图表，figsize宽高比适合展示函数曲线
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        # 画布背景设为白色
        self.figure.patch.set_facecolor('white')
        # 绘图区域背景设为浅灰
        self.ax.set_facecolor('#FAFAFA')

        # 包装为Qt控件
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 绘制默认曲线
        self._draw()

    def set_distribution(self, dist_type: DistributionType):
        """切换分布类型并重绘曲线，由控制面板信号触发"""
        self.distribution_type = dist_type
        self._draw()

    def _draw(self):
        """根据当前分布类型计算并绘制函数曲线"""
        self.ax.clear()

        # 生成0到60分钟的x轴采样点，200个点保证曲线平滑
        x = np.linspace(0, 60, 200)

        if self.distribution_type == DistributionType.QUADRATIC:
            # 二次函数倒U型：y = -0.05*(x-30)^2 + 15
            y = -0.05 * ((x - 30) ** 2) + 15
            title = '二次函数(倒U型) — 峰值在30分钟'
        elif self.distribution_type == DistributionType.NORMAL:
            # 正态分布单峰：μ=30, σ=8, 峰值20人/分钟
            y = 20 * np.exp(-((x - 30) ** 2) / (2 * 8 ** 2))
            title = '正态分布(单峰) μ=30 σ=8 — 峰值在30分钟'
        elif self.distribution_type == DistributionType.TRI_MODAL:
            # 三峰正态分布：三个峰分别在第10、30、50分钟, σ=6
            y = (10 * np.exp(-((x - 10) ** 2) / (2 * 6 ** 2)) +
                 20 * np.exp(-((x - 30) ** 2) / (2 * 6 ** 2)) +
                 10 * np.exp(-((x - 50) ** 2) / (2 * 6 ** 2)))
            title = '三峰正态分布 — 峰位于第10/30/50分钟'

        # 将负数截断为0，学生人数不能为负
        y = np.clip(y, 0, None)

        # 绘制蓝色曲线并在曲线下方填充浅蓝色半透明区域
        self.ax.plot(x, y, color='#2979ff', linewidth=2)
        self.ax.fill_between(x, 0, y, color='#2979ff', alpha=0.1)

        # 设置坐标轴标签、范围、网格
        self.ax.set_xlabel('仿真时间 (分钟)', fontsize=10)
        self.ax.set_ylabel('到达人数', fontsize=10)
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 25)
        self.ax.grid(True, linestyle='--', alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()