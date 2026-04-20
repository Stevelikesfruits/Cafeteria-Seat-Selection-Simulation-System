# models/student.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List


class PreferenceType(Enum):
    """座位偏好类型"""
    SINGLE = "单人单座"
    FACE_TO_FACE = "双人面对面"
    DIAGONAL = "双人斜对角"
    ADJACENT = "双人邻座"


@dataclass
class Student:
    """学生实体类"""
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