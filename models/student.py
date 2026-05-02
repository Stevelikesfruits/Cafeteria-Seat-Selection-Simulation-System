# models/student.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List


class PreferenceType(Enum):
    """座位偏好类型"""
    """
        座位偏好类型枚举。
        每个成员有两个属性：
        - name:  代码中的名字，例如 SINGLE、FACE_TO_FACE
        - value: 赋予的值，这里是中文描述，用于输出、日志等
        例如 PreferenceType.SINGLE.value 会得到字符串 "单人单座"
    """
    SINGLE = "单人单座"
    FACE_TO_FACE = "双人面对面"
    DIAGONAL = "双人斜对角"
    ADJACENT = "双人邻座"

# @dataclass 是 Python3.7引入的一个装饰器，放在类定义前，作用是自动生成常见的特殊方法，让写数据类时省去大量重复的样板代码。
@dataclass
class Student:
    """学生实体类"""
    """
        设计时,学生并不是按照单个学生来进行设计的,而是按组来设计
        'id'是一个或者多个学生共用的
        group_id暂未使用,留作后期可能会有拓展使用
        seated_seat_indices是个学生座位序号列表,这里使用field是为了防止python共用一个列表
    """
    id: int
    preference: PreferenceType
    arrival_time: int
    group_id: int = -1
    seated_table_id: int = -1
    seated_seat_indices: List[int] = field(default_factory=list)
    leave_time: int = 0
    satisfaction_score: int = 0  # 满意度得分 (+2, +1, -1)

    @property
    def is_seated(self) -> bool:
        return self.seated_table_id != -1