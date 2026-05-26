# ui/control_panel.py -- 右侧操控面板

## 类图总览

```mermaid
classDiagram
    class ControlPanel {
        <<QWidget 子类>>
        Signal preferences_changed(dict)
        -Dict[PreferenceType, QSpinBox] pref_inputs
        -Dict color_map
        -PreferencePieChart pie_chart
        --
        +init_ui()
        +on_pref_changed()
        +set_inputs_enabled(enabled: bool)
    }

    ControlPanel --> PreferenceType : 遍历枚举生成4个输入框
    ControlPanel *-- PreferencePieChart : 嵌入饼图
```

---

## `init_ui()` -- 构建 4 个偏好输入卡片

遍历 `PreferenceType` 枚举，为每种偏好创建一个带背景色的 Frame 卡片（含 QLabel 标签 + QSpinBox 0-100 输入框，默认 25），连接 `valueChanged` 信号到 `on_pref_changed`。最后嵌入 PreferencePieChart 饼图组件。

**颜色映射：**

| 偏好 | 颜色 | 色值 |
|------|------|------|
| SINGLE 单人 | 蓝色 | `#00BFFF` |
| FACE_TO_FACE 面对面 | 粉红 | `#FF6B6B` |
| DIAGONAL 斜对角 | 绿色 | `#8FBC8F` |
| ADJACENT 邻座 | 橙色 | `#FFA500` |

---

## `on_pref_changed()` -- 值变化处理

```mermaid
flowchart TD
    A["任一 SpinBox 值变化"] --> B["读取4个输入框的值 -> sizes 列表"]
    B --> C["实时更新饼图<br/>pie_chart.update_chart(sizes)"]
    C --> D{"总和 == 100?"}
    D -->|"是"| E["构建 new_ratios 字典<br/>值/100 转为小数"]
    E --> F["emit preferences_changed(new_ratios)<br/>通知 SimulationEngine"]
    D -->|"否"| G["什么都不发<br/>等待用户继续调整"]
```

**关键设计**：只有总和恰好为 100% 时才发射信号。

---

## `set_inputs_enabled()`

遍历 `pref_inputs` 字典，逐个 `setEnabled(enabled)`。仿真启动后禁用所有输入框，结束时重新启用，防止中途改参数导致数据不一致。
```

