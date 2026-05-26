# core/simulation.py -- 仿真引擎（核心调度器）

## 类图总览

```mermaid
classDiagram
    class SimulationEngine {
        -int num_tables_2
        -int num_tables_4
        -Restaurant restaurant
        -StudentGenerator generator
        -SeatAllocator allocator
        -int current_time = 0
        -List[Student] active_students
        -List[Student] history_students
        -Dict pref_ratios
        --
        +update_preferences(new_ratios: Dict)
        +step()
        -_process_departures()
        +get_statistics() dict
        +reset(num_tables_2?, num_tables_4?)
    }

    SimulationEngine *-- Restaurant : 持有
    SimulationEngine *-- StudentGenerator : 持有
    SimulationEngine *-- SeatAllocator : 持有
    SimulationEngine ..> SatisfactionCalculator : 调用静态方法
    SimulationEngine --> Student : 管理 active/history 列表
```

---

## 数据成员使用频率

| 成员 | 使用频率 | 说明 |
|------|----------|------|
| `restaurant` | 极高 | 每 tick 分配座位、释放座位、渲染视图都依赖它 |
| `active_students` | 极高 | 每 tick 遍历处理离店、追加新生 |
| `current_time` | 极高 | 每 tick +1，驱动人流曲线和离店判断 |
| `allocator` | 高 | 每 tick 为每个新生调用 allocate |
| `generator` | 高 | 每 tick 调用一次生成批次 |
| `history_students` | 高 | 离店学生归档，统计满意度时遍历 |
| `pref_ratios` | 中 | UI 更新时写入，生成学生时读取 |
| `num_tables_2/4` | 低 | 初始化/reset 时使用 |

---

## `step()` -- 每 Tick 主循环

```mermaid
flowchart TD
    START["current_time += 1"] --> PHASE1

    subgraph PHASE1["阶段1: 处理离店 _process_departures()"]
        D1["遍历 active_students"] --> D2{"leave_time <= current_time?"}
        D2 -->|"是"| D3{"已落座?"}
        D3 -->|"是"| D4["释放座位: table.seats[idx] = 0"]
        D3 -->|"否"| D5["无需释放"]
        D4 --> D6["移入 history_students"]
        D5 --> D6
        D2 -->|"否"| D7["保留在 active_students"]
    end

    PHASE1 --> PHASE2

    subgraph PHASE2["阶段2: 生成新生 generator.generate_batch()"]
        G1["传入 current_time + pref_ratios"] --> G2["返回 List[Student]"]
    end

    PHASE2 --> PHASE3

    subgraph PHASE3["阶段3: 分配座位 + 计算满意度"]
        L1["遍历每个新生"] --> L2["allocator.allocate(student)"]
        L2 -->|"成功"| L3["设定 leave_time = current_time + 20"]
        L3 --> L4["SatisfactionCalculator.calculate_and_assign"]
        L4 --> L5["加入 active_students"]
        L2 -->|"失败"| L6["SatisfactionCalculator.calculate_and_assign<br/>未落座, -1分"]
        L6 --> L7["直接进入 history_students"]
    end
```

---

## `_process_departures()` -- 离店处理

遍历 active_students，对 `leave_time <= current_time` 的学生：若已落座则遍历 seated_seat_indices 将对应 `seats[i]` 清零，然后移入 history_students。未到点的保留。

---

## `reset()` -- 完全重置

按可选新桌数重建 Restaurant / StudentGenerator / SeatAllocator，清零 current_time 和两个学生列表，pref_ratios 恢复默认各 25%。

---

## 关键时序参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 就餐时间 | 固定 20 分钟 | `leave_time = arrival_time + 20` |
| 定时器间隔 | 500ms(实际) = 1分钟(仿真) | 由 MainWindow 的 QTimer 控制 |
| 总仿真时长 | 由用户控制 | 点击"结束"停止 |

## 状态机

```mermaid
stateDiagram-v2
    [*] --> 初始 : 启动程序
    初始 --> 运行中 : 点击"开始"
    运行中 --> 暂停 : 点击"暂停"
    暂停 --> 运行中 : 点击"继续"
    运行中 --> 结束 : 点击"结束"
    暂停 --> 结束 : 点击"结束"
    结束 --> 初始 : reset() 重置
```
```

