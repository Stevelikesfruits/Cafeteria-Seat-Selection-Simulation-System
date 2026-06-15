# ui/control_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QFrame, QPushButton, QComboBox
from PySide6.QtCore import Signal, Qt
# 导入学生比例
from models.student import PreferenceType
# 导入人数分布类型枚举
from core.student_generator import DistributionType
# 导入自定义的饼状图
from ui.charts import PreferencePieChart, DistributionLineChart


class PreferenceSettingsWindow(QWidget):
    """人群比例设置弹窗，点击侧边栏按钮弹出，设置四种座位偏好的权重比例"""
    # 偏好变更信号，附带{PreferenceType: ratio}字典
    preferences_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("人群比例设置")
        self.resize(420, 600)
        # 非模态，可与主窗口同时操作
        self.setWindowFlags(Qt.Window)

        self.color_map = {
            PreferenceType.SINGLE: "#00BFFF",
            PreferenceType.FACE_TO_FACE: "#FF6B6B",
            PreferenceType.DIAGONAL: "#8FBC8F",
            PreferenceType.ADJACENT: "#FFA500"
        }
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 偏好权重输入区域，四个偏好各一个SpinBox
        self.pref_inputs = {}
        for pref in PreferenceType:
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color_map[pref]};
                    border-radius: 5px;
                    border: 1px solid #333;
                }}
                QLabel {{ color: #333; font-weight: bold; border: none; }}
                QSpinBox {{
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 4px 8px;
                    color: #333333;
                }}
                QSpinBox::up-button, QSpinBox::down-button {{
                    background-color: #e0e0e0;
                    border-left: 1px solid #cccccc;
                    width: 20px;
                    height: 12px;
                }}
                QSpinBox::up-arrow, QSpinBox::down-arrow {{
                    width: 10px;
                    height: 10px;
                    background-color: #333333;
                }}
            """)
            f_layout = QVBoxLayout(frame)
            lbl = QLabel(f"输入{pref.value}权重:")
            spin = QSpinBox()
            spin.setRange(0, 100)
            # 初始默认值25，四个偏好各25%
            spin.setValue(25)
            spin.valueChanged.connect(self._on_spin_changed)

            f_layout.addWidget(lbl)
            f_layout.addWidget(spin)
            self.pref_inputs[pref] = spin
            layout.addWidget(frame)

        # 实时百分比显示标签
        self.lbl_percentages = QLabel()
        self.lbl_percentages.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
        self.lbl_percentages.setWordWrap(True)
        layout.addWidget(self.lbl_percentages)

        # 全零警告标签
        self.lbl_warning = QLabel()
        self.lbl_warning.setStyleSheet("color: #FF4444; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.lbl_warning)

        # 饼图组件
        self.pie_chart = PreferencePieChart()
        layout.addWidget(self.pie_chart)

        layout.addStretch()

        # 初始化时触发一次计算
        self._on_spin_changed()

    def _on_spin_changed(self):
        """任一SpinBox值变化时自动计算百分比并更新饼图和文字"""
        values = [self.pref_inputs[pref].value() for pref in PreferenceType]
        total = sum(values)

        if total > 0:
            # 按权重自动计算百分比
            percentages = [v / total * 100 for v in values]
            self.pie_chart.update_chart(percentages)
            # 显示文字：各偏好名称及百分比
            text = " | ".join(f"{pref.value}: {p:.1f}%" for pref, p in zip(PreferenceType, percentages))
            self.lbl_percentages.setText(text)
            self.lbl_warning.setText("")
            # 发送偏好比例信号给仿真引擎
            ratios = {pref: v / total for pref, v in zip(PreferenceType, values)}
            self.preferences_changed.emit(ratios)
        else:
            self.lbl_warning.setText("权重不能全部为0，请至少给一个偏好设置非零值")
            self.lbl_percentages.setText("")

    def set_inputs_enabled(self, enabled: bool):
        """仿真开始后禁用所有SpinBox"""
        for spin in self.pref_inputs.values():
            spin.setEnabled(enabled)

    def get_total_weight(self) -> int:
        """返回当前四个权重的总和，供外部校验"""
        return sum(spin.value() for spin in self.pref_inputs.values())

    def closeEvent(self, event):
        """关闭窗口时隐藏而非销毁，再次打开数据不丢失"""
        self.hide()
        event.ignore()


class DistributionChartWindow(QWidget):
    """人流分布函数曲线弹窗，点击侧边栏按钮弹出，显示当前分布类型的函数曲线"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("人流函数曲线")
        self.resize(700, 400)
        self.setWindowFlags(Qt.Window)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.chart = DistributionLineChart()
        layout.addWidget(self.chart)

    def set_distribution(self, dist_type: DistributionType):
        """切换分布类型时更新曲线，由侧边栏下拉框信号触发"""
        self.chart.set_distribution(dist_type)

    def closeEvent(self, event):
        """关闭窗口时隐藏而非销毁，再次打开数据不丢失"""
        self.hide()
        event.ignore()


class ControlPanel(QWidget):
    # 人数分布类型变更信号，附带DistributionType枚举值
    distribution_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 按钮统一样式
        btn_style = """
            QPushButton {
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 12px 20px;
                border: 1px solid #222222;
                background-color: #2979ff;
            }
            QPushButton:disabled {
                color: #999999;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                border: 1px solid #bbbbbb;
                background-color: #e0e0e0;
            }
        """

        # 人数分布类型下拉框
        dist_frame = QFrame()
        dist_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #333;
            }
            QLabel { color: #333; font-weight: bold; border: none; }
            QComboBox {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #333;
                selection-background-color: #2979ff;
                selection-color: white;
            }
        """)
        dist_layout = QVBoxLayout(dist_frame)
        dist_label = QLabel("人数分布类型:")
        self.dist_combo = QComboBox()
        for dist_type in DistributionType:
            self.dist_combo.addItem(dist_type.value, dist_type)
        self.dist_combo.setCurrentIndex(0)
        self.dist_combo.currentIndexChanged.connect(self._on_distribution_changed)

        dist_layout.addWidget(dist_label)
        dist_layout.addWidget(self.dist_combo)
        layout.addWidget(dist_frame)

        # 按钮A：人群比例设置
        self.btn_pref_settings = QPushButton("人群比例设置")
        self.btn_pref_settings.setStyleSheet(btn_style + "QPushButton { background-color: #00BFFF; }")
        layout.addWidget(self.btn_pref_settings)

        # 按钮B：人流函数曲线
        self.btn_chart = QPushButton("人流函数曲线")
        self.btn_chart.setStyleSheet(btn_style + "QPushButton { background-color: #FFA500; }")
        layout.addWidget(self.btn_chart)

        # 拉伸因子，控件靠上
        layout.addStretch()

    def _on_distribution_changed(self):
        """下拉框切换分布类型时发送信号"""
        selected = self.dist_combo.currentData()
        self.distribution_changed.emit(selected)

    def set_inputs_enabled(self, enabled: bool):
        """仿真开始/结束后启用或禁用侧边栏控件"""
        self.dist_combo.setEnabled(enabled)
        self.btn_pref_settings.setEnabled(enabled)
        self.btn_chart.setEnabled(enabled)
