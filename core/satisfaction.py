# core/satisfaction.py

'''
导入Student类
其中在本文件中用到的成员参数：
is_seated：bool类型，指示学生是否落座
satisfaction_score：int类型，满意度得分
'''

from models.student import Student

#满意度计算类
class SatisfactionCalculator:
    @staticmethod
    def calculate_and_assign(student: Student, is_perfect_match: bool):
        """
        计算并赋值满意度
        - 落座且完全满足偏好：+2分
        - 落座但未满足偏好：+1分
        - 因餐厅满员未能落座：-1分
        """

        #学生未能及时落座时满意度-1
        if not student.is_seated:
            student.satisfaction_score = -1

        #学生落座且满足偏好满意度+1
        elif is_perfect_match:
            student.satisfaction_score = 2

        #学生落座但未满足偏好满意度+2
        else:
            student.satisfaction_score = 1
