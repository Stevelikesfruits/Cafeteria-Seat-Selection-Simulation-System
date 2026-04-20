# core/student_generator.py
import random
import math
from typing import List, Dict
from models.student import Student, PreferenceType


class StudentGenerator:
    def __init__(self):
        self.current_student_id = 1

    def generate_batch(self, current_time: int, pref_ratios: Dict[PreferenceType, float]) -> List[Student]:
        """
        根据当前时间和偏好比例生成一批学生
        使用倒U型函数模拟人流：假设高峰期在第30分钟左右
        """
        # 倒U型函数：例如 y = -0.05 * (x - 30)^2 + 15，加上正负3的随机扰动
        base_count = -0.05 * ((current_time - 30) ** 2) + 15
        base_count = max(0, int(base_count))  # 不能为负数

        noise = random.randint(-2, 3)
        actual_count = max(0, base_count + noise)

        students = []
        for _ in range(actual_count):
            # 根据用户设定的比例随机决定该学生的偏好
            prefs = list(pref_ratios.keys())
            weights = list(pref_ratios.values())
            chosen_pref = random.choices(prefs, weights=weights, k=1)[0]

            student = Student(
                id=self.current_student_id,
                preference=chosen_pref,
                arrival_time=current_time
            )
            students.append(student)
            self.current_student_id += 1

        return students