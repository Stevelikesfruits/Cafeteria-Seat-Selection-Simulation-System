# models/restaurant.py
import numpy as np
from typing import List, Dict
from models.student import PreferenceType


class Table:
    """桌子基类"""

    def __init__(self, table_id: int, capacity: int, space_cost: int):
        self.id = table_id
        self.capacity = capacity
        self.space_cost = space_cost
        self.seats = np.zeros(capacity, dtype=int)  # 0代表空闲，非0代表学生ID

    @property
    def occupied_count(self) -> int:
        return np.count_nonzero(self.seats)

    @property
    def is_full(self) -> bool:
        return self.occupied_count == self.capacity

    def get_free_seats(self) -> List[int]:
        return [i for i in range(self.capacity) if self.seats[i] == 0]


class Table2(Table):
    """双人桌"""

    def __init__(self, table_id: int):
        super().__init__(table_id, capacity=2, space_cost=4)


class Table4(Table):
    """四人桌"""

    def __init__(self, table_id: int):
        super().__init__(table_id, capacity=4, space_cost=6)


class Restaurant:
    """餐厅容器模型"""

    def __init__(self, num_tables_2: int = 20, num_tables_4: int = 20):
        # 按照文档：总空间200，双人占4，四人占6。这里默认 20*4 + 20*6 = 200
        self.total_space = 200
        self.tables: Dict[int, Table] = {}

        table_id = 1
        for _ in range(num_tables_2):
            self.tables[table_id] = Table2(table_id)
            table_id += 1
        for _ in range(num_tables_4):
            self.tables[table_id] = Table4(table_id)
            table_id += 1

    def get_table(self, table_id: int) -> Table:
        return self.tables.get(table_id)