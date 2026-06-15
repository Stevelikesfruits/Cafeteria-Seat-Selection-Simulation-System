# core/student_generator.py
import random
import math
from enum import Enum
from typing import List, Dict
from models.student import Student, PreferenceType


class DistributionType(Enum):
    """学生到达人数分布类型枚举"""
    QUADRATIC = "二次函数(倒U型)"
    NORMAL = "正态分布(单峰)"
    TRI_MODAL = "三峰正态分布"


#生成学生对象
class StudentGenerator:

    #初始化
    def __init__(self):
        self.current_student_id = 1                 #current_student_id：学生id

    #生成一批学生
    def generate_batch(self, current_time: int, pref_ratios: Dict[PreferenceType, float],
                       distribution: DistributionType = DistributionType.QUADRATIC) -> List[Student]:
        """
        根据当前时间、偏好比例和人数分布类型生成一批学生
        current_time: 当前时刻
        pref_ratios: 各偏好人群占比列表（偏好:占比）
        distribution: 人数分布类型，默认二次函数倒U型
        """

        # 根据分布类型调用对应的计算函数得到基础人数
        if distribution == DistributionType.QUADRATIC:
            base_count = self._quadratic_count(current_time)
        elif distribution == DistributionType.NORMAL:
            base_count = self._normal_count(current_time)
        elif distribution == DistributionType.TRI_MODAL:
            base_count = self._tri_modal_count(current_time)
        else:
            base_count = self._quadratic_count(current_time)

        base_count = max(0, int(base_count))  # 不能为负数

        #随机扰动
        noise = random.randint(-2, 3)
        actual_count = max(0, base_count + noise)

        #返回的学生列表
        students = []

        for _ in range(actual_count):
            # 根据用户设定的比例随机决定该学生的偏好
            #将偏好和占比分别提取为列表 按照比例随机设定该学生的偏好
            prefs = list(pref_ratios.keys())
            weights = list(pref_ratios.values())
            chosen_pref = random.choices(prefs, weights=weights, k=1)[0]

            #将id，偏好，当前时刻赋值给该学生并存入students列表
            student = Student(
                id=self.current_student_id,
                preference=chosen_pref,
                arrival_time=current_time
            )
            students.append(student)
            self.current_student_id += 1

        return students

    @staticmethod
    def _quadratic_count(current_time: int) -> float:
        """二次函数倒U型：峰值在30分钟，模拟午餐时段集中的人流高峰
        函数形式 y = -0.05*(x-30)^2 + 15，x=30时峰值15人"""
        return -0.05 * ((current_time - 30) ** 2) + 15

    @staticmethod
    def _normal_count(current_time: int) -> float:
        """正态分布单峰：期望μ=30分钟，标准差σ=8，峰值约20人/分钟
        模拟以午餐时间为中心、前后逐渐衰减的到达模式"""
        mu = 30       # 期望值：第30分钟为峰值
        sigma = 8     # 标准差：大部分人流集中在30±16分钟内
        return 20 * math.exp(-((current_time - mu) ** 2) / (2 * sigma ** 2))

    @staticmethod
    def _tri_modal_count(current_time: int) -> float:
        """三峰正态分布：三个峰值分别位于第10、第30、第50分钟
        模拟早餐、午餐、晚餐三个时段的人流特征，σ=6使得每个峰较为集中
        早餐峰值10人、午餐峰值20人、晚餐峰值10人"""
        sigma = 6     # 标准差：每个峰集中在峰值±12分钟内
        return (10 * math.exp(-((current_time - 10) ** 2) / (2 * sigma ** 2)) +
                20 * math.exp(-((current_time - 30) ** 2) / (2 * sigma ** 2)) +
                10 * math.exp(-((current_time - 50) ** 2) / (2 * sigma ** 2)))
