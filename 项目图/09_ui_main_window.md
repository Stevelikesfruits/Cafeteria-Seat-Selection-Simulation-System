# ui/main_window.py -- 主窗口（UI 总控制器）

## 类图总览

```mermaid
classDiagram
    class MainWindow {
        -int _num_tables_2
        -int _num_tables_4
        -SimulationEngine engine
        -QTimer timer
        -QPushButton btn_start
        -QPushButton btn_pause
        -QPushButton btn_end
        -RestaurantView restaurant_view
        -ControlPanel control_panel
        --
        +init_ui()
        +start_simulation()
        +pause_simulation()
        +end_simulation()
        +on_simulation_step()
    }

    MainWindow --> SimulationEngine : 持有，驱动 step()
    MainWindow *-- RestaurantView : 子组件
    MainWindow *-- ControlPanel : 子组件
    MainWindow ..> TableCountDialog : 弹窗调用
    MainWindow --> QTimer : 定时器 500ms
```

---

## 启动流程

```mermaid
flowchart TD
    A["1. 弹窗 TableCountDialog<br/>用户输入双人桌/四人桌数量"] --> B{"用户确认?"}
    B -->|"确定"| C["2. 创建 SimulationEngine<br/>传入桌数"]
    B -->|"取消"| C2["使用默认值 20+20<br/>创建 SimulationEngine"]
    C --> D["3. 创建 QTimer<br/>连接 timeout -> on_simulation_step"]
    C2 --> D
    D --> E["4. init_ui() 构建界面<br/>顶部按钮栏 + 左右分区"]
    E --> F["5. control_panel.init_ui()<br/>初始化偏好输入区+饼图"]
    F --> G["6. restaurant_view.init_restaurant_layout()<br/>根据 Restaurant 绘制桌椅"]
    G --> H["就绪，等待用户操作"]
```

---

## `start_simulation()` -- 开始仿真

校验偏好总和是否=100%，通过后禁用输入框、切换按钮状态、启动 QTimer（500ms 间隔）。

## `pause_simulation()` -- 暂停/继续

判断 `timer.isActive()`：运行中则 stop 并改按钮文字为"继续"；已暂停则 start 并恢复文字为"暂停"。

## `end_simulation()` -- 结束仿真

停止定时器 -> 调用 `engine.get_statistics()` 弹出报告 -> 弹窗询问新桌数 -> `engine.reset()` -> 刷新餐厅视图 -> 恢复按钮和输入框初始状态。

## `on_simulation_step()` -- 定时器回调

每 500ms 触发：`engine.step()` 推进 1 分钟仿真 -> `restaurant_view.update_view()` 刷新座位颜色。

---

## 按钮状态机

```mermaid
stateDiagram-v2
    state "初始" as init
    state "运行中" as running
    state "已暂停" as paused
    
    init: 开始(启用) 暂停(禁用) 结束(禁用)
    running: 开始(禁用) 暂停(启用) 结束(启用)
    paused: 开始(禁用) 继续(启用) 结束(启用)

    init --> running : 点击"开始"(校验100%)
    running --> paused : 点击"暂停"
    paused --> running : 点击"继续"
    running --> init : 点击"结束"(弹报告+重置)
    paused --> init : 点击"结束"(弹报告+重置)
```

---

## 信号/槽连接一览

| 信号源 | 信号 | 槽函数 | 触发时机 |
|--------|------|--------|----------|
| `btn_start` | `clicked` | `start_simulation` | 用户点击"开始" |
| `btn_pause` | `clicked` | `pause_simulation` | 用户点击"暂停/继续" |
| `btn_end` | `clicked` | `end_simulation` | 用户点击"结束" |
| `QTimer` | `timeout` | `on_simulation_step` | 每 500ms 自动 |
| `ControlPanel` | `preferences_changed(dict)` | `engine.update_preferences` | 偏好总和=100%时 |

**注意**: `preferences_changed -> engine.update_preferences` 是 UI 与 Core 之间唯一的运行时数据通道（Qt Signal/Slot 机制）。
```

