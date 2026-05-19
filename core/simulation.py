# core/simulation.py
from typing import Dict, List
from models.restaurant import Restaurant
from models.student import Student, PreferenceType
from core.student_generator import StudentGenerator
from core.seat_allocator import SeatAllocator
from core.satisfaction import SatisfactionCalculator


class SimulationEngine:
    def __init__(self):
        self.restaurant = Restaurant()
        self.generator = StudentGenerator()
        self.allocator = SeatAllocator(self.restaurant)

        self.current_time = 0
        self.active_students: List[Student] = []
        self.history_students: List[Student] = []  # 用于最后统计

        # 默认偏好配置
        self.pref_ratios = {
            PreferenceType.SINGLE: 0.25,
            PreferenceType.FACE_TO_FACE: 0.25,
            PreferenceType.DIAGONAL: 0.25,
            PreferenceType.ADJACENT: 0.25
        }

    def update_preferences(self, new_ratios: Dict[PreferenceType, float]):
        """UI传入新的偏好比例"""
        self.pref_ratios = new_ratios

    def step(self):
        """执行一个时间步长（如1分钟）"""
        self.current_time += 1

        # 1. 检查并移除就餐结束的学生 (固定20分钟)
        self._process_departures()

        # 2. 生成新学生
        new_batch = self.generator.generate_batch(self.current_time, self.pref_ratios)

        # 3. 为新学生分配座位
        for student in new_batch:
            success = self.allocator.allocate(student)

            if success:
                # 根据任务书，就餐时间固定为20分钟
                student.leave_time = self.current_time + 20
                # TODO: 让allocator返回是否是perfect_match，这里为了演示暂时都算作非完美(+1)
                SatisfactionCalculator.calculate_and_assign(student, is_perfect_match=False)
                self.active_students.append(student)
            else:
                SatisfactionCalculator.calculate_and_assign(student, is_perfect_match=False)  # 未落座得-1分
                self.history_students.append(student)  # 未落座直接进入历史记录

    def _process_departures(self):
        """处理就餐完毕离开的学生"""
        remaining_students = []
        for student in self.active_students:
            if student.leave_time <= self.current_time:
                # 释放座位
                if student.is_seated:
                    table = self.restaurant.get_table(student.seated_table_id)
                    for seat_idx in student.seated_seat_indices:
                        table.seats[seat_idx] = 0
                self.history_students.append(student)
            else:
                remaining_students.append(student)
        self.active_students = remaining_students

    def get_statistics(self) -> dict:
        """供UI层或数据分析模块获取当前统计信息"""
        total_score = sum(s.satisfaction_score for s in self.history_students + self.active_students)
        return {
            "current_time": self.current_time,
            "active_diners": len(self.active_students),
            "total_processed": len(self.history_students) + len(self.active_students),
            "total_satisfaction_score": total_score
        }


    # 添加重置函数，同时重置偏好比例
    def reset(self):
        """重置模拟引擎到初始状态"""
        # 重置餐厅实例（清空所有座位占用）
        self.restaurant = Restaurant()
        # 重置生成器和分配器（分配器需要关联新的restaurant实例）
        self.generator = StudentGenerator()
        self.allocator = SeatAllocator(self.restaurant)

        # 重置时间和学生列表
        self.current_time = 0
        self.active_students = []
        self.history_students = []

        # 重置偏好比例到默认值
        self.pref_ratios = {
            PreferenceType.SINGLE: 0.25,
            PreferenceType.FACE_TO_FACE: 0.25,
            PreferenceType.DIAGONAL: 0.25,
            PreferenceType.ADJACENT: 0.25
        }