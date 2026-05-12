# tests/test_models.py
"""models 模块单元测试 —— 覆盖 student.py 与 restaurant.py"""
import sys
sys.path.insert(0, ".")

import numpy as np
import pytest
from models.student import Student, PreferenceType
from models.restaurant import Table, Table2, Table4, Restaurant


# ============================================================
# 一、PreferenceType 枚举测试
# ============================================================
class TestPreferenceType:
    """测试座位偏好枚举的定义正确性"""

    def test_members_exist(self):
        """四个偏好成员应当全部存在"""
        assert hasattr(PreferenceType, "SINGLE")
        assert hasattr(PreferenceType, "FACE_TO_FACE")
        assert hasattr(PreferenceType, "DIAGONAL")
        assert hasattr(PreferenceType, "ADJACENT")

    # @pytest.mark.parametrize 和下面的 def test_member_values 是强绑定的装饰关系：
    # 前者负责把后者的单一测试“克隆”成多组参数化的测试。
    # member 和 expected_value 并不是全局变量，
    # 而是在每个测试用例运行时，由 pytest 从提供的元组里取出并作为参数传入函数的局部变量.
    @pytest.mark.parametrize("member, expected_value", [
        (PreferenceType.SINGLE,       "单人单座"),
        (PreferenceType.FACE_TO_FACE, "双人面对面"),
        (PreferenceType.DIAGONAL,     "双人斜对角"),
        (PreferenceType.ADJACENT,     "双人邻座"),
    ])
    def test_member_values(self, member, expected_value):
        """每个枚举成员的 .value 应为对应的中文描述"""
        assert member.value == expected_value


# ============================================================
# 二、Student 数据类测试
# ============================================================
class TestStudent:
    """测试学生实体类的字段默认值与属性逻辑"""

    def test_default_values(self):
        """创建 Student 时，可选字段应有正确的默认值"""
        s = Student(id=1, preference=PreferenceType.SINGLE, arrival_time=10)
        assert s.group_id == -1
        assert s.seated_table_id == -1
        assert s.seated_seat_indices == []
        assert s.leave_time == 0
        assert s.satisfaction_score == 0

    def test_is_seated_false_by_default(self):
        """未入座时 is_seated 返回 False"""
        s = Student(id=2, preference=PreferenceType.FACE_TO_FACE, arrival_time=3)
        assert s.is_seated is False

    def test_is_seated_true_after_seating(self):
        """设置 seated_table_id 后 is_seated 返回 True"""
        s = Student(id=3, preference=PreferenceType.SINGLE, arrival_time=5)
        s.seated_table_id = 10
        s.seated_seat_indices = [0]
        assert s.is_seated is True

    def test_field_assignment(self):
        """所有字段应能正确读写"""
        s = Student(id=42, preference=PreferenceType.DIAGONAL, arrival_time=8,
                    group_id=7, seated_table_id=3,
                    seated_seat_indices=[1, 2], leave_time=25,
                    satisfaction_score=2)
        assert s.id == 42
        assert s.preference == PreferenceType.DIAGONAL
        assert s.arrival_time == 8
        assert s.group_id == 7
        assert s.seated_table_id == 3
        assert s.seated_seat_indices == [1, 2]
        assert s.leave_time == 25
        assert s.satisfaction_score == 2


# ============================================================
# 三、Table 基类测试
# ============================================================
class TestTable:
    """测试桌子基类的初始化、属性和方法"""

    def test_init_state(self):
        """桌子初始化后，id/capacity/space_cost 正确，seats 全为 0"""
        t = Table(table_id=1, capacity=4, space_cost=6)
        assert t.id == 1
        assert t.capacity == 4
        assert t.space_cost == 6
        assert len(t.seats) == 4
        assert np.all(t.seats == 0)

    def test_occupied_count_empty(self):
        """空桌 occupied_count 应为 0"""
        t = Table(1, capacity=3, space_cost=5)
        assert t.occupied_count == 0

    def test_occupied_count_partial(self):
        """部分座位有人时，occupied_count 应正确计数"""
        t = Table(1, capacity=4, space_cost=6)
        t.seats[0] = 101
        t.seats[2] = 102
        assert t.occupied_count == 2

    def test_occupied_count_full(self):
        """满桌时 occupied_count 应等于 capacity"""
        t = Table(1, capacity=2, space_cost=4)
        t.seats[0] = 1
        t.seats[1] = 2
        assert t.occupied_count == 2

    def test_is_full_false(self):
        """有空位时 is_full 返回 False"""
        t = Table(1, capacity=3, space_cost=5)
        t.seats[0] = 101
        assert t.is_full is False

    def test_is_full_true(self):
        """满桌时 is_full 返回 True"""
        t = Table(1, capacity=2, space_cost=4)
        t.seats[0] = 1
        t.seats[1] = 2
        assert t.is_full is True

    def test_get_free_seats_empty_table(self):
        """空桌应返回所有座位索引"""
        t = Table(1, capacity=3, space_cost=5)
        assert t.get_free_seats() == [0, 1, 2]

    def test_get_free_seats_partial(self):
        """部分有人时只返回空位索引"""
        t = Table(1, capacity=4, space_cost=6)
        t.seats[0] = 101
        t.seats[3] = 104
        assert t.get_free_seats() == [1, 2]

    def test_get_free_seats_full(self):
        """满桌时应返回空列表"""
        t = Table(1, capacity=2, space_cost=4)
        t.seats[0] = 1
        t.seats[1] = 2
        assert t.get_free_seats() == []


# ============================================================
# 四、Table2 / Table4 子类测试
# ============================================================
class TestTable2:
    """双人桌子类"""

    def test_capacity_and_cost(self):
        t = Table2(table_id=5)
        assert t.capacity == 2
        assert t.space_cost == 4
        assert len(t.seats) == 2


class TestTable4:
    """四人桌子类"""

    def test_capacity_and_cost(self):
        t = Table4(table_id=10)
        assert t.capacity == 4
        assert t.space_cost == 6
        assert len(t.seats) == 4


# ============================================================
# 五、Restaurant 容器测试
# ============================================================
class TestRestaurant:
    """测试餐厅容器的初始化与桌子查询"""

    def test_default_init_table_count(self):
        """默认创建 20 张双人桌 + 20 张四人桌 = 40 张"""
        r = Restaurant()
        assert len(r.tables) == 40

    def test_default_init_table_types(self):
        """前 20 张为 Table2，后 20 张为 Table4"""
        r = Restaurant()
        for tid in range(1, 21):
            assert isinstance(r.tables[tid], Table2)
        for tid in range(21, 41):
            assert isinstance(r.tables[tid], Table4)

    def test_default_total_space(self):
        """总空间应为 200（20*4 + 20*6）"""
        r = Restaurant()
        assert r.total_space == 200

    def test_custom_table_counts(self):
        """自定义桌数：5 张双人桌 + 3 张四人桌"""
        r = Restaurant(num_tables_2=5, num_tables_4=3)
        assert len(r.tables) == 8
        assert r.total_space == 200  # total_space 始终不变

    def test_get_table_exists(self):
        """存在的 table_id 应返回正确的 Table 对象"""
        r = Restaurant()
        t = r.get_table(1)
        assert t is not None
        assert t.id == 1
        assert isinstance(t, Table2)

    def test_get_table_not_exists(self):
        """不存在的 table_id 应返回 None"""
        r = Restaurant()
        assert r.get_table(999) is None
