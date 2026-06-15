# core/seat_allocator.py -- 座位分配器

## 类图总览

```mermaid
classDiagram
    class SeatAllocator {
        -Restaurant restaurant
        --
        +allocate(student: Student) bool
        -_find_perfect_match(pref: PreferenceType) Tuple
        -_find_any_free_seat() Tuple
    }

    SeatAllocator --> Restaurant : 持有引用，读写 tables
    SeatAllocator --> Student : 读取 preference / 写入 seated_table_id
    SeatAllocator --> PreferenceType : 分支判断偏好类型
    SeatAllocator --> Table2 : isinstance 类型判断
    SeatAllocator --> Table4 : isinstance 类型判断
```

---

## `allocate()` -- 主入口（两阶段策略）

```mermaid
flowchart TD
    A["输入: Student 对象"] --> B{"1. 完美匹配<br/>_find_perfect_match(pref)"}
    B -->|"找到"| E["table_id, seat_idx"]
    B -->|"未找到"| C{"2. 降级策略<br/>_find_any_free_seat()"}
    C -->|"找到"| E
    C -->|"未找到"| D["返回 False<br/>餐厅满员"]
    
    E --> F["table.seats[seat_idx] = student.id"]
    F --> G["student.seated_table_id = table_id"]
    G --> H["student.seated_seat_indices = [seat_idx]"]
    H --> I["返回 True"]
```

---

## `_find_perfect_match()` -- 详细匹配逻辑

```mermaid
flowchart TD
    START["遍历 restaurant.tables.values()"] --> CHECK_FULL{"桌子满座?"}
    CHECK_FULL -->|"是"| NEXT["跳过，下一张桌子"]
    CHECK_FULL -->|"否"| GET_FREE["获取 free_seats 列表"]
    
    GET_FREE --> WHICH_PREF{"学生偏好类型?"}
    
    WHICH_PREF -->|"SINGLE<br/>单人单座"| S1{"整张桌子全空<br/>len(free)==capacity?"}
    S1 -->|"是"| FOUND["返回 table.id, free_seats[0]"]
    S1 -->|"否"| NEXT
    
    WHICH_PREF -->|"FACE_TO_FACE<br/>双人面对面"| F1{"桌子类型?"}
    F1 -->|"Table2"| F2{"至少1个空位?"}
    F2 -->|"是"| FOUND
    F2 -->|"否"| NEXT
    F1 -->|"Table4"| F3{"位0和2同时空?"}
    F3 -->|"是"| F4["返回 table.id, 0"]
    F3 -->|"否"| F5{"位1和3同时空?"}
    F5 -->|"是"| F6["返回 table.id, 1"]
    F5 -->|"否"| NEXT
    
    WHICH_PREF -->|"DIAGONAL<br/>双人斜对角"| D1{"是 Table4<br/>且有至少1空位?"}
    D1 -->|"是"| FOUND
    D1 -->|"否"| NEXT
    
    WHICH_PREF -->|"ADJACENT<br/>双人邻座"| D1
    
    NEXT --> START
```

### 匹配规则速查表

| 偏好 | Table2 | Table4 |
|------|--------|--------|
| SINGLE | 找完全空桌 | 找完全空桌 |
| FACE_TO_FACE | 任意空位即可 | 找对面空位 (0--2, 1--3) |
| DIAGONAL | -- | 任意空位 (未精确检查斜对角) |
| ADJACENT | -- | 任意空位 (未精确检查邻座) |

---

## `_find_any_free_seat()` -- 降级策略

```mermaid
flowchart TD
    A["遍历所有桌子"] --> B{"free_seats 非空?"}
    B -->|"是"| C["返回 table.id, free_seats[0]"]
    B -->|"否"| D["继续下一张"]
    D --> A
    A -->|"遍历完仍未找到"| E["返回 None, None"]
```

找第一个有空位的桌子，返回第一个空位。不检测偏好。

---

## 算法复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 完美匹配 | O(T*C) | T=桌子数(默认40), C=容量(2/4), 约160次检查 |
| 降级查找 | O(T*C) | 最坏情况两次全遍历，约320次数组访问/tick |

## 已知限制

- **DIAGONAL / ADJACENT 未精确匹配**：代码注释标注"不具体检查"，只检查 Table4 有任意空位即返回，未验证斜对角/邻座条件
- **SINGLE 偏好只在全空桌匹配**：不分配给已有部分占用的桌子
```

