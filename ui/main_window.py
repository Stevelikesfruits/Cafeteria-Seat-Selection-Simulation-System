# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer, Qt
# 从已添加的sys.path路径中导入自定义的类
from core.simulation import SimulationEngine
from ui.control_panel import ControlPanel
from ui.restaurant_view import RestaurantView

# 定义MainWindow类
class MainWindow(QMainWindow):
    # 初始化
    def __init__(self):
        # 先初始化父类QMainWindow()
        super().__init__()
        self.setWindowTitle("餐厅排座仿真系统")
        self.resize(1100, 800)
        # 设置背景颜色为浅灰色
        self.setStyleSheet("background-color: #EAEAEA;")

        # 初始化仿真引擎
        self.engine = SimulationEngine()
        # 初始化一个定时器，是程序每隔一段时间自动执行一段代码
        self.timer = QTimer()
        # 时间一到就执行on_simulation_step函数
        self.timer.timeout.connect(self.on_simulation_step)

        # 用init_ui()函数搭建界面
        self.init_ui()
        # 用self.engine.restaurant中的参数搭建餐厅界面
        self.restaurant_view.init_restaurant_layout(self.engine.restaurant)

    # 定义ui界面设置函数
    def init_ui(self):
        # 设置底板
        central_widget = QWidget()
        # 将这块底板设置给self，后续操作也会同步给self
        self.setCentralWidget(central_widget)
        # 设置主要底层布局为垂直布局
        main_layout = QVBoxLayout(central_widget)

        # 设置 顶部按钮控制栏 为水平布局
        top_bar = QHBoxLayout()
        # 设置按钮居中对齐
        top_bar.setAlignment(Qt.AlignCenter)

        self.btn_start = QPushButton("开始")
        self.btn_pause = QPushButton("暂停")
        self.btn_end = QPushButton("结束")

        # 按钮样式
        btn_style = """
        QPushButton {
            color: #ffffff;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px 30px;
            border: 1px solid #222222;
            background-color: #2979ff;
        }

        /* 禁用状态：大幅度褪色、文字变暗、边框变浅，反差超大 */
        QPushButton:disabled {
            color: #999999;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
            border: 1px solid #bbbbbb;
            background-color: #e0e0e0;
        }
        """
        self.btn_start.setStyleSheet(btn_style + "QPushButton { background-color: #00BFFF; }")
        self.btn_pause.setStyleSheet(btn_style + "QPushButton { background-color: #FFD700; color: #333; }")
        self.btn_end.setStyleSheet(btn_style + "QPushButton { background-color: #FF69B4; }")

        # 初始状态：暂停/结束按钮禁用
        self.btn_pause.setEnabled(False)
        self.btn_end.setEnabled(False)

        # 关联按钮点击函数
        self.btn_start.clicked.connect(self.start_simulation)
        self.btn_pause.clicked.connect(self.pause_simulation)
        self.btn_end.clicked.connect(self.end_simulation)

        # 将三个按钮交给top_bar水平布局管理
        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_pause)
        top_bar.addWidget(self.btn_end)

        # 布局嵌套
        # 将顶部按钮布局，装入main_layout底层垂直布局里
        main_layout.addLayout(top_bar)


        # 2. 下方主内容区 (左侧视图，右侧面板)
        content_layout = QHBoxLayout()

        # 设置左侧餐厅视图
        self.restaurant_view = RestaurantView()
        self.restaurant_view.setStyleSheet("background-color: white; border-radius: 10px;")

        # 设置右边操作栏
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(280)
        # 当产生修改信号时，自动通知引擎，更新参数
        self.control_panel.preferences_changed.connect(self.engine.update_preferences)

        # 将self.restaurant_view加入到content_layout布局中，大小占比为3
        content_layout.addWidget(self.restaurant_view, 3)
        # 将self.control_panel加入到content_layout布局中，大小占比为1
        content_layout.addWidget(self.control_panel, 1)

        # 将下方主内容区布局加入到底层布局中
        main_layout.addLayout(content_layout)

    # 开始按钮关联函数：启动仿真
    def start_simulation(self):
        # 检查参数总和是否为100
        # 提取右侧所有控件里的值进行相加
        total = sum(spin.value() for spin in self.control_panel.pref_inputs.values())
        if total != 100:
            QMessageBox.warning(self, "错误", "偏好百分比总和必须为100%！")
            return

        # 开始后禁用右侧输入框
        self.control_panel.set_inputs_enabled(False)
        # 重新设置按钮状态
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_end.setEnabled(True)
        # 启动计数器，重复间隔设为500ms
        self.timer.start(500)

    # 暂停按钮关联函数：暂停和继续
    def pause_simulation(self):
        # 判断定时器是否在运行
        if self.timer.isActive():
            self.timer.stop()
            self.btn_pause.setText("继续")
            self.btn_pause.setStyleSheet(
                "QPushButton { background-color: #32CD32; color: white; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 10px 30px; }")
        else:
            self.timer.start(500)
            self.btn_pause.setText("暂停")
            self.btn_pause.setStyleSheet(
                "QPushButton { background-color: #FFD700; color: #333; font-weight: bold; font-size: 18px; border-radius: 8px; padding: 10px 30px; }")

    # 结束按钮关联函数：
    def end_simulation(self):
        self.timer.stop()
        # 获取仿真统计数据
        stats = self.engine.get_statistics()
        # 弹出仿真报告提示框
        QMessageBox.information(self, "仿真报告",
                                f"仿真结束！\n\n总经过时间: {stats['current_time']} 分钟\n"
                                f"累计接待人数: {stats['total_processed']} 人\n"
                                f"综合满意度得分: {stats['total_satisfaction_score']}"
                                )

        # 进行重置
        self.engine.reset()
        # 刷新餐厅界面
        self.restaurant_view.update_view(self.engine.restaurant)
        # 重置按钮和右侧操作栏
        self.control_panel.set_inputs_enabled(True)
        self.btn_start.setEnabled(True)
        self.btn_end.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("暂停")
        btn_style = """
                QPushButton {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 8px;
                    padding: 10px 30px;
                    border: 1px solid #222222;
                    background-color: #2979ff;
                }

                /* 禁用状态：大幅度褪色、文字变暗、边框变浅，反差超大 */
                QPushButton:disabled {
                    color: #999999;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 8px;
                    border: 1px solid #bbbbbb;
                    background-color: #e0e0e0;
                }
                """
        self.btn_pause.setStyleSheet(btn_style + "QPushButton { background-color: #FFD700; color: #333; }")




    # 仿真步进逻辑
    def on_simulation_step(self):
        # 引擎执行一次步进，推进1分钟，处理排座/顾客离店等逻辑
        self.engine.step()
        self.restaurant_view.update_view(self.engine.restaurant)