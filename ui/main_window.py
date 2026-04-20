# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer, Qt
from core.simulation import SimulationEngine
from ui.control_panel import ControlPanel
from ui.restaurant_view import RestaurantView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("餐厅排座仿真系统")
        self.resize(1100, 800)
        self.setStyleSheet("background-color: #EAEAEA;")  # 整体浅灰背景

        self.engine = SimulationEngine()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_simulation_step)

        self.init_ui()
        self.restaurant_view.init_restaurant_layout(self.engine.restaurant)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. 顶部按钮控制栏 (对应概念图顶部)
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignCenter)

        self.btn_start = QPushButton("开始")
        self.btn_pause = QPushButton("暂停")
        self.btn_end = QPushButton("结束")

        # 按钮样式
        btn_style = """
            QPushButton {{
                color: white; font-weight: bold; font-size: 18px;
                border-radius: 8px; padding: 10px 30px; border: 1px solid #333;
            }}
            QPushButton:disabled {{ background-color: #A0A0A0; }}
        """
        self.btn_start.setStyleSheet(btn_style + "QPushButton { background-color: #00BFFF; }")
        self.btn_pause.setStyleSheet(btn_style + "QPushButton { background-color: #FFD700; color: #333; }")
        self.btn_end.setStyleSheet(btn_style + "QPushButton { background-color: #FF69B4; }")

        self.btn_pause.setEnabled(False)
        self.btn_end.setEnabled(False)

        self.btn_start.clicked.connect(self.start_simulation)
        self.btn_pause.clicked.connect(self.pause_simulation)
        self.btn_end.clicked.connect(self.end_simulation)

        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_pause)
        top_bar.addWidget(self.btn_end)

        main_layout.addLayout(top_bar)

        # 2. 下方主内容区 (左侧视图，右侧面板)
        content_layout = QHBoxLayout()

        self.restaurant_view = RestaurantView()
        self.restaurant_view.setStyleSheet("background-color: white; border-radius: 10px;")

        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(280)
        self.control_panel.preferences_changed.connect(self.engine.update_preferences)

        content_layout.addWidget(self.restaurant_view, 3)
        content_layout.addWidget(self.control_panel, 1)

        main_layout.addLayout(content_layout)

    def start_simulation(self):
        # 检查参数总和是否为100
        total = sum(spin.value() for spin in self.control_panel.pref_inputs.values())
        if total != 100:
            QMessageBox.warning(self, "错误", "偏好百分比总和必须为100%！")
            return

        self.control_panel.set_inputs_enabled(False)
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_end.setEnabled(True)
        self.timer.start(500)  # 500ms 推进一分钟

    def pause_simulation(self):
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

    def end_simulation(self):
        self.timer.stop()
        stats = self.engine.get_statistics()
        QMessageBox.information(self, "仿真报告",
                                f"仿真结束！\n\n总经过时间: {stats['current_time']} 分钟\n"
                                f"累计接待人数: {stats['total_processed']} 人\n"
                                f"综合满意度得分: {stats['total_satisfaction_score']}"
                                )
        # 这里可以加入重置逻辑

    def on_simulation_step(self):
        self.engine.step()
        self.restaurant_view.update_view(self.engine.restaurant)