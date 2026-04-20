# core/seat_allocator.py
from typing import Optional, Tuple
from models.restaurant import Restaurant, Table, Table2, Table4
from models.student import Student, PreferenceType


class SeatAllocator:
    def __init__(self, restaurant: Restaurant):
        self.restaurant = restaurant

    def allocate(self, student: Student) -> bool:
        """为单个学生分配座位。返回是否分配成功"""
        # 策略1：寻找完美匹配的空位
        table_id, seat_idx = self._find_perfect_match(student.preference)

        # 策略2：如果找不到完美匹配，寻找任何空位（降级）
        if table_id is None:
            table_id, seat_idx = self._find_any_free_seat()

        if table_id is not None and seat_idx is not None:
            # 执行落座
            table = self.restaurant.get_table(table_id)
            table.seats[seat_idx] = student.id
            student.seated_table_id = table_id
            student.seated_seat_indices = [seat_idx]
            return True

        return False

    def _find_perfect_match(self, pref: PreferenceType) -> Tuple[Optional[int], Optional[int]]:
        """根据偏好寻找最完美的座位（简化版逻辑）"""
        for table in self.restaurant.tables.values():
            if table.is_full:
                continue

            free_seats = table.get_free_seats()

            if pref == PreferenceType.SINGLE:
                # 单人偏好：最好找一张完全空的桌子，或者没有人的那一侧
                if len(free_seats) == table.capacity:
                    return table.id, free_seats[0]

            elif pref == PreferenceType.FACE_TO_FACE:
                if isinstance(table, Table2) and len(free_seats) >= 1:
                    return table.id, free_seats[0]
                elif isinstance(table, Table4):
                    # 简化：假设0和2，1和3是面对面
                    if 0 in free_seats and 2 in free_seats: return table.id, 0
                    if 1 in free_seats and 3 in free_seats: return table.id, 1

            # 这里的斜对角和邻座逻辑可以由成员B继续深入扩展完善
            elif pref in [PreferenceType.DIAGONAL, PreferenceType.ADJACENT]:
                if isinstance(table, Table4) and len(free_seats) > 0:
                    return table.id, free_seats[0]

        return None, None

    def _find_any_free_seat(self) -> Tuple[Optional[int], Optional[int]]:
        """备选方案：找到任何一个空位"""
        for table in self.restaurant.tables.values():
            free_seats = table.get_free_seats()
            if free_seats:
                return table.id, free_seats[0]
        return None, None