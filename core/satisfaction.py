# core/satisfaction.py
from models.student import Student

class SatisfactionCalculator:
    @staticmethod
    def calculate_and_assign(student: Student, is_perfect_match: bool):
        """
        计算并赋值满意度
        - 落座且完全满足偏好：+2分
        - 落座但未满足偏好：+1分
        - 因餐厅满员未能落座：-1分
        """
        if not student.is_seated:
            student.satisfaction_score = -1
        elif is_perfect_match:
            student.satisfaction_score = 2
        else:
            student.satisfaction_score = 1