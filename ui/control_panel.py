# ui/control_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QFrame, QMessageBox
from PySide6.QtCore import Signal
from models.student import PreferenceType
from ui.charts import PreferencePieChart


class ControlPanel(QWidget):
    # PySide6 使用 Signal 而不是 pyqtSignal
    preferences_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        # 定义与概念图匹配的颜色主题
        self.color_map = {
            PreferenceType.SINGLE: "#00BFFF",  # 单人单桌 - 蓝色
            PreferenceType.FACE_TO_FACE: "#FF6B6B",  # 双人面对面 - 粉红
            PreferenceType.DIAGONAL: "#8FBC8F",  # 双人斜对角 - 绿色
            PreferenceType.ADJACENT: "#FFA500"  # 双人邻座 - 橙色
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 1. 偏好输入区域
        self.pref_inputs = {}

        for pref in PreferenceType:
            # 创建带颜色背景的卡片
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color_map[pref]};
                    border-radius: 5px;
                    border: 1px solid #333;
                }}
                QLabel {{ color: #333; font-weight: bold; border: none; }}
                QSpinBox {{ background-color: white; border: 1px solid #ccc; }}
            """)
            f_layout = QVBoxLayout(frame)

            lbl = QLabel(f"输入{pref.value}百分比:")
            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setValue(25)  # 默认各25%
            spin.valueChanged.connect(self.on_pref_changed)

            f_layout.addWidget(lbl)
            f_layout.addWidget(spin)

            self.pref_inputs[pref] = spin
            layout.addWidget(frame)

        # 2. 饼图组件
        self.pie_chart = PreferencePieChart()
        layout.addWidget(self.pie_chart)

        layout.addStretch()

    def on_pref_changed(self):
        sizes = [self.pref_inputs[pref].value() for pref in PreferenceType]
        total = sum(sizes)

        # 实时更新饼图
        self.pie_chart.update_chart(sizes)

        # 只有总和为100时才发送合法的数据更新信号给后端
        if total == 100:
            new_ratios = {pref: self.pref_inputs[pref].value() / 100.0 for pref in PreferenceType}
            self.preferences_changed.emit(new_ratios)

    def set_inputs_enabled(self, enabled: bool):
        """仿真开始后，禁用输入框"""
        for spin in self.pref_inputs.values():
            spin.setEnabled(enabled)