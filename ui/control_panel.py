# ui/control_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QFrame, QMessageBox
from PySide6.QtCore import Signal
# 导入学生比例
from models.student import PreferenceType
# 导入自定义的饼状图
from ui.charts import PreferencePieChart


class ControlPanel(QWidget):
    # 创建一个信号，同时信号附带一个字典信息
    # 此信号需要创建在__init__之前，属于类属性
    preferences_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        # 定义匹配的颜色主题
        # PreferenceType是枚举类，需要直接使用
        self.color_map = {
            PreferenceType.SINGLE: "#00BFFF",  # 单人单桌 - 蓝色
            PreferenceType.FACE_TO_FACE: "#FF6B6B",  # 双人面对面 - 粉红
            PreferenceType.DIAGONAL: "#8FBC8F",  # 双人斜对角 - 绿色
            PreferenceType.ADJACENT: "#FFA500"  # 双人邻座 - 橙色
        }
        self.init_ui()

    # 初始化布局
    def init_ui(self):
        # 将self作为参数传到布局里
        # 相当于将self设成垂直布局
        layout = QVBoxLayout(self)
        # 控件间距25像素
        layout.setSpacing(25)

        # 偏好输入区域
        self.pref_inputs = {}

        # PreferenceType中为座位偏好类型
        for pref in PreferenceType:
            # 创建带颜色背景的卡片，只相当于背景
            frame = QFrame()
            # 为Frame设置样式：背景色、圆角、边框；标签/输入框样式
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

            # 文本标签
            lbl = QLabel(f"输入{pref.value}百分比:")
            # 数字输入框：范围0-100，默认值25
            spin = QSpinBox()
            spin.setRange(0, 100)
            # 默认各25%
            spin.setValue(25)
            # 绑定信号：输入值变化时触发函数on_pref_changed
            spin.valueChanged.connect(self.on_pref_changed)

            # 将控件加入Frame布局
            f_layout.addWidget(lbl)
            f_layout.addWidget(spin)

            # 对应标签：桌子类型————数字输入框
            self.pref_inputs[pref] = spin
            # 将frame加入layout总布局
            layout.addWidget(frame)

        # 加入饼图组件
        self.pie_chart = PreferencePieChart()
        layout.addWidget(self.pie_chart)

        # 拉伸因子：让控件靠上显示，下方留空
        layout.addStretch()

    # 数值变化的更新函数
    def on_pref_changed(self):
        # 取出每个数字输入框的数字
        sizes = [self.pref_inputs[pref].value() for pref in PreferenceType]
        total = sum(sizes)

        # 实时更新饼图
        self.pie_chart.update_chart(sizes)

        # 只有总和为100时才发送合法的数据更新信号给后端
        if total == 100:
            # 将{类型：占比}这个字典绑定给信号发出去
            new_ratios = {pref: self.pref_inputs[pref].value() / 100.0 for pref in PreferenceType}
            self.preferences_changed.emit(new_ratios)

    # 启用/禁用函数
    def set_inputs_enabled(self, enabled: bool):
        """仿真开始后，禁用输入框"""
        for spin in self.pref_inputs.values():
            spin.setEnabled(enabled)