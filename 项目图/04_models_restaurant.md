# models/restaurant.py -- 桌子体系与餐厅容器

## 类图总览

```mermaid
classDiagram
    class Table {
        <<基类>>
        +int id
        +int capacity
        +int space_cost
        +ndarray~int~ seats
        --
        +occupied_count() int
        +is_full() bool
        +get_free_seats() List~int~
    }

    class Table2 {
        <<子类 / 继承 Table>>
        capacity=2
        space_cost=4
    }

    class Table4 {
        <<子类 / 继承 Table>>
        capacity=4
        space_cost=6
    }

    class Restaurant {
        <<容器>>
        +int total_space = 200
        +int num_tables_2 = 20
        +int num_tables_4 = 20
        +Dict~int, Table~ tables
        --
        +get_table(table_id) Table
    }

    Table <|-- Table2 : 继承
    Table <|-- Table4 : 继承
    Restaurant *-- Table : tables 字典 (int -> Table)
```

---

## 核心数据结构：`Table.seats` (numpy 数组)

```
seats = np.zeros(capacity, dtype=int)

示例 (四人桌，第0和第2座有人):
        索引0    索引1    索引2    索引3
         |        |        |        |
seats = [ 101  ,   0   ,   102  ,   0   ]
          |              |
      student.id=101   student.id=102
      
0 = 空位，非0 = 该座位的 Student.id
```

这是**整个系统最核心的数据结构**：SeatAllocator 写入值、SimulationEngine 清空值、RestaurantView 读取渲染。

---

## 数据成员使用频率

| 成员 | 使用频率 | 主要使用场景 |
|------|----------|-------------|
| `Table.seats` | 极高 | 分配时写入/读取判断空位；离店时清空；视图渲染时遍历着色 |
| `Restaurant.tables` | 极高 | SeatAllocator 遍历查找空位；RestaurantView 遍历绘制 |
| `Table.get_free_seats()` | 极高 | 每次座位查找都调用，遍历 seats 返回所有值为0的索引 |
| `Table.capacity` | 高 | 判断桌子类型(2人/4人)；SINGLE 偏好匹配全空桌 |
| `Table.is_full` | 高 | 分配时快速跳过满桌 |
| `Table.space_cost` | 中 | 空间校验，构造 Restaurant 时检查 |
| `Table.occupied_count` | 中 | 统计信息，利用 `np.count_nonzero` 向量化计算 |

---

## 函数说明

- **`get_free_seats()`** -- 遍历 seats，收集值为 0 的索引返回。最频繁调用的方法。
- **`occupied_count` / `is_full`** -- 基于 `np.count_nonzero(seats)` 的 property，一行逻辑。
- **`Restaurant.__init__`** -- 先校验空间(n2*4 + n4*6 <= 200)，再循环创建 Table2/Table4 对象，ID 从 1 递增。

**继承关系**：`Table2(capacity=2, space=4)` 和 `Table4(capacity=4, space=6)` 仅通过 `super().__init__` 传入不同参数，无额外逻辑。
```

