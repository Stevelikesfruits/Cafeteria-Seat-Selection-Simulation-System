# ui/table_count_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt


class TableCountDialog(QDialog):
    """初始/重置时弹窗询问双人桌和四人桌数量"""

    def __init__(self, default_2: int = 20, default_4: int = 20, parent=None):
        #初始化父类
        super().__init__(parent)
        # 窗口标题
        self.setWindowTitle("餐桌数量设置")
        # 固定窗口尺寸（不可拉伸）
        self.setFixedSize(380, 260)

        # 初始化实例变量
        self._num_2 = default_2
        self._num_4 = default_4

        # 1. 整体布局：垂直布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 2. 提示文字标签
        hint = QLabel("请设置双人桌和四人桌的数量：\n"
                      "双人桌占4单位空间，四人桌占6单位空间，总计不超过200单位。")
        # 自动换行（避免文字超出窗口）
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 3. 桌数输入区域：表单布局
        form = QFormLayout()
        form.setSpacing(8)

        # 双人桌输入框
        self.spin_2 = QSpinBox()
        # 范围：0-50（50*4=200，单人桌最大上限）
        self.spin_2.setRange(0, 50)
        # 默认值
        self.spin_2.setValue(default_2)
        # 后缀文字（提升可读性）
        self.spin_2.setSuffix(" 张")
        # 数值变化时触发校验方法
        self.spin_2.valueChanged.connect(self._on_value_changed)

        # 四人桌输入框
        self.spin_4 = QSpinBox()
        # 范围：0-33（33*6=198≤200，四人桌最大上限）
        self.spin_4.setRange(0, 33)
        self.spin_4.setValue(default_4)
        self.spin_4.setSuffix(" 张")
        self.spin_4.valueChanged.connect(self._on_value_changed)

        # 将输入框添加到表单布局（标签+输入框）
        form.addRow("双人桌数量：", self.spin_2)
        form.addRow("四人桌数量：", self.spin_4)
        layout.addLayout(form)

        # 4. 空间占用提示标签（居中对齐）
        self.space_label = QLabel()
        self.space_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.space_label)

        # 5. 按钮区域：水平布局
        btn_layout = QHBoxLayout()
        # 左侧拉伸（让按钮靠右显示）
        btn_layout.addStretch()

        # 确定按钮
        self.btn_ok = QPushButton("确定")
        self.btn_ok.setFixedWidth(80)

        #self.accept是父类QDialog自带的内置方法
        #功能：立刻关闭当前对话框窗口；给对话框标记一个「用户确认了」的状态（在下面get_table_counts里用来判断）
        # 点击触发QDialog的accept()
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setFixedWidth(80)
        # 点击触发QDialog的reject()
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self._on_value_changed()

    def _on_value_changed(self):
        # 获取当前双人桌数量
        n2 = self.spin_2.value()
        # 获取当前双人桌数量
        n4 = self.spin_4.value()
        # 计算已用空间
        used = n2 * 4 + n4 * 6
        # 判断是否超出200单位限制
        ok = used <= 200

        # 仅当未超限时，“确定”按钮可用
        self.btn_ok.setEnabled(ok)

        # 根据是否超限，设置提示文字和样式
        if ok:
            self.space_label.setText(f"已用空间: {used} / 200 单位")
            self.space_label.setStyleSheet("color: green; font-weight: bold;") # 绿色加粗
        else:
            self.space_label.setText(f"已用空间: {used} / 200 单位 ⚠ 超出限制！")
            self.space_label.setStyleSheet("color: red; font-weight: bold;")  # 红色加粗+警告符号

    # 获取输入值
    def values(self):
        return self.spin_2.value(), self.spin_4.value()

    # 使用类方法
    @classmethod
    def get_table_counts(cls, default_2: int = 20, default_4: int = 20, parent=None):
        """静态方法：弹出对话框并返回 (num_2, num_4, accepted)"""
        # 创建对话框实例
        dlg = cls(default_2, default_4, parent)
        # 以模态方式显示对话框（阻塞程序，直到对话框关闭）
        result = dlg.exec()
        # 用户点击“确定”
        if result == QDialog.Accepted:
            return (*dlg.values(), True) # 返回(双人桌数, 四人桌数, True)
        # 用户点击“取消”或关闭窗口
        else:
            return default_2, default_4, False # 返回默认值+False
