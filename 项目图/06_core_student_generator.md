# core/student_generator.py -- 学生生成器

## 类图总览

```mermaid
classDiagram
    class StudentGenerator {
        -int current_student_id = 1
        --
        +generate_batch(current_time: int, pref_ratios: Dict) List[Student]
    }

    StudentGenerator --> Student : 创建实例
    StudentGenerator --> PreferenceType : 遍历 keys，按权重随机选
```

---

## `generate_batch()` -- 完整流程

```mermaid
flowchart TD
    subgraph 阶段1["阶段1: 计算人数 (倒U型人流模型)"]
        A["输入: current_time 当前分钟"] --> B["代入公式<br/>base = -0.05 * (t-30)^2 + 15"]
        B --> C["取整 + 下限0<br/>不能为负数"]
        C --> D["叠加随机扰动<br/>noise in [-2, +3]"]
        D --> E["actual_count = max(0, base + noise)<br/>本批次学生数"]
    end

    subgraph 阶段2["阶段2: 按比例生成学生"]
        E --> F{"actual_count > 0?"}
        F -->|"否"| G["返回空列表"]
        F -->|"是"| H["循环 actual_count 次"]
        H --> I["random.choices<br/>按 pref_ratios 权重随机选偏好"]
        I --> J["创建 Student 对象<br/>id / preference / arrival_time"]
        J --> K["current_student_id += 1"]
        K --> L{"循环结束?"}
        L -->|"否"| I
        L -->|"是"| M["返回 List[Student]"]
    end
```

---

## 倒U型人流曲线

```
人数
 ^
16|        *  *
14|      *      *
12|    *          *
10|   *            *
 8|  *              *
 6| *                *
 4|*                  *
 2|*                    *
 0+------------------------------> 时间(分钟)
   0   10   20   30   40   50   60

峰值在 t=30 分钟:
base = -0.05 * 0 + 15 = 15 人/分钟
随机扰动后: 13~18 人/分钟

t=0 时: base = -45 + 15 = -30 --> 截断为 0
t=60时: base = -45 + 15 = -30 --> 截断为 0
```

---

## 偏好分配机制

使用 Python `random.choices` 的加权随机选择。UI 层通过 `pref_ratios` 字典（如 `{SINGLE: 0.25, FACE_TO_FACE: 0.25, ...}`）动态控制各偏好比例，每次生成时按权重随机分配。

| 参数 | 值 |
|------|-----|
| 人流模型 | 二次函数: `y = -0.05*(t-30)^2 + 15` |
| 高峰期 | t=30 分钟 (约 15 人/分钟) |
| 随机扰动 | `random.randint(-2, 3)` |
| 最小值 | `max(0, ...)` 确保人数不为负 |
| 学生ID | 全局自增，从 1 开始，跨批次连续 |
```

