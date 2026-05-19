# models/restaurant.py
import numpy as np
from typing import List, Dict  # 为了兼容py3.8及以下版本而引入内部库
from models.student import PreferenceType


class Table:
    """桌子基类"""

    def __init__(self, table_id: int, capacity: int, space_cost: int):
        self.id = table_id
        self.capacity = capacity
        self.space_cost = space_cost
        # 使用numpy一维数组作为作为类型
        self.seats = np.zeros(capacity, dtype=int)  # 0代表空闲，非0代表学生ID

    @property
    def occupied_count(self) -> int:
        """返回这个桌子的空座位个数"""
        return np.count_nonzero(self.seats)

    @property
    def is_full(self) -> bool:
        """判断这个桌子是否被占满"""
        return self.occupied_count == self.capacity

    def get_free_seats(self) -> List[int]:
        """返回这个桌子的空座位列表"""
        return [i for i in range(self.capacity) if self.seats[i] == 0]


class Table2(Table):
    """双人桌"""

    # super()是代理父类对象,python自动向上寻找其父类,
    # 这里是单继承,因此会向上找到Table这个基类
    # 这样不用写Table.__init__(self, table_id, capacity=2, space_cost=4)
    # 而且比较规范
    def __init__(self, table_id: int):
        super().__init__(table_id, capacity=2, space_cost=4)


class Table4(Table):
    """四人桌"""

    def __init__(self, table_id: int):
        super().__init__(table_id, capacity=4, space_cost=6)


class Restaurant:
    """餐厅容器模型"""

    def __init__(self, num_tables_2: int = 20, num_tables_4: int = 20):
        """餐厅桌子初始化"""
        # 按照文档：总空间200，双人占4，四人占6。这里默认 20*4 + 20*6 = 200
        self.total_space = 200
        self.tables: Dict[int, Table] = {}
        #   ^^^^^^^^  ^^^^^^^^^^^^^^^   ^^
        #   属性名     类型注解（声明）    赋初值

        # 开始循环初始化每一张桌子对象
        table_id = 1
        for _ in range(num_tables_2):
            self.tables[table_id] = Table2(table_id)
            table_id += 1
        for _ in range(num_tables_4):
            self.tables[table_id] = Table4(table_id)
            table_id += 1

    def get_table(self, table_id: int) -> Table:
        """从 Restaurant 对象里, 根据 table_id 获取对应的桌子对象"""
        return self.tables.get(table_id)
        # .get()方法:
        # 如果 table_id 存在, 就返回对应的桌子对象;
        # 如果 table_id 不存在, 它会返回 None(而不会像 self.tables[table_id] 那样抛出 KeyError 异常)