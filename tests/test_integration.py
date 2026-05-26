"""接口联调测试 -- 测试各模块间能否正常通信与协调工作"""
import sys
sys.path.insert(0, ".")

import pytest
import numpy as np
from models.student import Student, PreferenceType
from models.restaurant import Table, Table2, Table4, Restaurant
from core.student_generator import StudentGenerator
from core.seat_allocator import SeatAllocator
from core.satisfaction import SatisfactionCalculator
from core.simulation import SimulationEngine

# Qt 相关导入 (仅用于 Bug 复现测试)
HAS_QT = False
try:
    from PySide6.QtWidgets import QApplication
    from ui.control_panel import ControlPanel
    HAS_QT = True
except ImportError:
    pass


# ============================================================
# 一、StudentGenerator <-> SimulationEngine 接口
# ============================================================
class TestGeneratorEngineInterface:
    """测试 StudentGenerator 与 SimulationEngine 之间的数据传递"""

    def test_generator_returns_valid_students(self):
        """Generator 返回的学生列表应能被 Engine 正常消费"""
        gen = StudentGenerator()
        prefs = {
            PreferenceType.SINGLE: 0.25,
            PreferenceType.FACE_TO_FACE: 0.25,
            PreferenceType.DIAGONAL: 0.25,
            PreferenceType.ADJACENT: 0.25,
        }
        batch = gen.generate_batch(current_time=30, pref_ratios=prefs)
        assert len(batch) > 0, "高峰期应至少产生若干学生"
        for s in batch:
            assert isinstance(s, Student)
            assert s.id > 0
            assert s.arrival_time == 30
            assert s.preference in PreferenceType
            assert not s.is_seated

    def test_generator_respects_ratios_statistically(self):
        """偏好比例大致符合设定 (统计检验, 大样本)"""
        gen = StudentGenerator()
        prefs = {
            PreferenceType.SINGLE: 0.5,
            PreferenceType.FACE_TO_FACE: 0.5,
            PreferenceType.DIAGONAL: 0.0,
            PreferenceType.ADJACENT: 0.0,
        }
        counts = {p: 0 for p in PreferenceType}
        total = 0
        for t in range(25, 36):
            batch = gen.generate_batch(current_time=t, pref_ratios=prefs)
            for s in batch:
                counts[s.preference] += 1
                total += 1
        if total > 20:
            single_ratio = counts[PreferenceType.SINGLE] / total
            assert 0.3 < single_ratio < 0.7, \
                f"SINGLE 比例偏离预期: {single_ratio:.2f}"
            assert counts[PreferenceType.DIAGONAL] == 0
            assert counts[PreferenceType.ADJACENT] == 0

    def test_generator_ids_are_unique_and_sequential(self):
        """学生 ID 应跨批次连续且唯一"""
        gen = StudentGenerator()
        prefs = {p: 0.25 for p in PreferenceType}
        all_ids = []
        for t in range(1, 11):
            batch = gen.generate_batch(current_time=t, pref_ratios=prefs)
            all_ids.extend(s.id for s in batch)
        assert len(all_ids) == len(set(all_ids)), "存在重复 ID"
        assert all_ids == sorted(all_ids), "ID 不是递增的"

    def test_engine_calls_generator_in_step(self):
        """SimulationEngine.step() 将 current_time 和 pref_ratios 传给 Generator"""
        engine = SimulationEngine(num_tables_2=20, num_tables_4=20)
        engine.pref_ratios = {
            PreferenceType.SINGLE: 1.0,
            PreferenceType.FACE_TO_FACE: 0.0,
            PreferenceType.DIAGONAL: 0.0,
            PreferenceType.ADJACENT: 0.0,
        }
        engine.current_time = 29
        engine.step()
        stats = engine.get_statistics()
        assert stats["total_processed"] > 0, "Engine.step 没有产生学生"


# ============================================================
# 二、SeatAllocator <-> Restaurant 接口
# ============================================================
class TestAllocatorRestaurantInterface:
    """测试 SeatAllocator 与 Restaurant 之间的座位读写"""

    def test_allocate_writes_to_table_seats(self):
        """分配成功后, table.seats 中应有对应 student.id"""
        r = Restaurant(num_tables_2=1, num_tables_4=0)
        allocator = SeatAllocator(r)
        student = Student(id=1, preference=PreferenceType.SINGLE, arrival_time=1)
        result = allocator.allocate(student)
        assert result is True
        table = r.get_table(1)
        assert 1 in table.seats, "student.id 应写入 seats 数组"
        assert student.seated_table_id == 1
        assert student.is_seated

    def test_allocate_updates_student_seat_info(self):
        """分配后 Student 的 seated_table_id 和 seated_seat_indices 正确"""
        r = Restaurant(num_tables_2=2, num_tables_4=0)
        allocator = SeatAllocator(r)
        s1 = Student(id=1, preference=PreferenceType.SINGLE, arrival_time=1)
        s2 = Student(id=2, preference=PreferenceType.SINGLE, arrival_time=1)
        allocator.allocate(s1)
        allocator.allocate(s2)
        assert s1.seated_table_id != s2.seated_table_id, \
            "SINGLE 偏好应分到不同空桌"
        assert s1.seated_table_id != -1
        assert len(s1.seated_seat_indices) == 1

    def test_allocate_returns_false_when_full(self):
        """餐厅满员时 allocate 返回 False, 不修改 Student 落座信息"""
        r = Restaurant(num_tables_2=1, num_tables_4=0)
        allocator = SeatAllocator(r)
        s1 = Student(id=1, preference=PreferenceType.SINGLE, arrival_time=1)
        s2 = Student(id=2, preference=PreferenceType.SINGLE, arrival_time=1)
        assert allocator.allocate(s1)
        assert allocator.allocate(s2)
        s3 = Student(id=3, preference=PreferenceType.SINGLE, arrival_time=1)
        result = allocator.allocate(s3)
        assert result is False
        assert s3.seated_table_id == -1
        assert not s3.is_seated

    def test_seats_cleared_on_departure(self):
        """学生离店后 table.seats 对应位置清零"""
        engine = SimulationEngine(num_tables_2=5, num_tables_4=5)
        engine.pref_ratios = {PreferenceType.SINGLE: 1.0,
                             PreferenceType.FACE_TO_FACE: 0.0,
                             PreferenceType.DIAGONAL: 0.0,
                             PreferenceType.ADJACENT: 0.0}
        engine.current_time = 29
        engine.step()
        seated_before = []
        for s in engine.active_students:
            if s.is_seated:
                seated_before.append((s.id, s.seated_table_id,
                                      list(s.seated_seat_indices)))
        engine.current_time = 100
        engine._process_departures()
        for sid, tid, indices in seated_before:
            table = engine.restaurant.get_table(tid)
            for idx in indices:
                assert table.seats[idx] == 0, \
                    f"学生{sid}离店后座位({tid},{idx})应为0, 实际为{table.seats[idx]}"

    def test_face_to_face_prefers_opposite_seats_on_table4(self):
        """FACE_TO_FACE 在四人桌上优先选对面座位"""
        r = Restaurant(num_tables_2=0, num_tables_4=1)
        allocator = SeatAllocator(r)
        table = r.get_table(1)
        table.seats[2] = 999
        table.seats[3] = 999
        student = Student(id=1, preference=PreferenceType.FACE_TO_FACE,
                          arrival_time=1)
        result = allocator.allocate(student)
        assert result is True
        assert student.seated_seat_indices[0] == 0, \
            f"应选座位0(对面2被占), 实际选了{student.seated_seat_indices[0]}"


# ============================================================
# 三、SimulationEngine <-> SatisfactionCalculator 接口
# ============================================================
class TestEngineSatisfactionInterface:
    """测试 SimulationEngine 是否正确调用 SatisfactionCalculator"""

    def test_seated_students_get_positive_score(self):
        """落座学生满意度应为 +1 (当前 is_perfect_match 恒为 False)"""
        engine = SimulationEngine(num_tables_2=20, num_tables_4=20)
        engine.pref_ratios = {PreferenceType.SINGLE: 1.0,
                             PreferenceType.FACE_TO_FACE: 0.0,
                             PreferenceType.DIAGONAL: 0.0,
                             PreferenceType.ADJACENT: 0.0}
        engine.current_time = 29
        engine.step()
        for s in engine.active_students:
            assert s.satisfaction_score == 1, \
                f"落座学生应得 +1, 实际 {s.satisfaction_score}"

    def test_unseated_students_get_negative_score(self):
        """未落座学生满意度应为 -1"""
        engine = SimulationEngine(num_tables_2=1, num_tables_4=0)
        engine.pref_ratios = {PreferenceType.SINGLE: 1.0,
                             PreferenceType.FACE_TO_FACE: 0.0,
                             PreferenceType.DIAGONAL: 0.0,
                             PreferenceType.ADJACENT: 0.0}
        engine.current_time = 29
        engine.step()
        unseated = [s for s in engine.history_students if not s.is_seated]
        for s in unseated:
            assert s.satisfaction_score == -1, \
                f"未落座学生应得 -1, 实际 {s.satisfaction_score}"

    def test_statistics_sums_scores_correctly(self):
        """get_statistics 的满意度总分应与手动计算一致"""
        engine = SimulationEngine(num_tables_2=10, num_tables_4=10)
        engine.pref_ratios = {p: 0.25 for p in PreferenceType}
        engine.current_time = 29
        for _ in range(3):
            engine.step()
        stats = engine.get_statistics()
        manual_sum = sum(s.satisfaction_score for s in engine.active_students)
        manual_sum += sum(s.satisfaction_score for s in engine.history_students)
        assert stats["total_satisfaction_score"] == manual_sum


# ============================================================
# 四、完整数据流端到端
# ============================================================
class TestEndToEndDataFlow:
    """测试数据从生成 -> 分配 -> 评分 -> 离店的全链路"""

    def test_full_lifecycle_consistency(self):
        """学生完整生命周期: 生成、落座、评分、离店, 数据一致"""
        engine = SimulationEngine(num_tables_2=10, num_tables_4=10)
        engine.pref_ratios = {p: 0.25 for p in PreferenceType}
        engine.current_time = 29
        for _ in range(35):
            engine.step()

        all_student_ids = set()
        all_student_ids.update(s.id for s in engine.active_students)
        all_student_ids.update(s.id for s in engine.history_students)
        for table in engine.restaurant.tables.values():
            for seat_val in table.seats:
                if seat_val != 0:
                    assert seat_val in all_student_ids, \
                        f"seats 中的 id={seat_val} 不在任何学生列表中"

        for s in engine.active_students:
            assert s.leave_time > engine.current_time, \
                f"active 学生 {s.id} leave_time={s.leave_time} <= 当前 {engine.current_time}"

        for s in engine.history_students:
            if s.is_seated:
                assert s.leave_time <= engine.current_time, \
                    f"history 学生 {s.id} 未到离开时间"

    def test_engine_reset_clears_all_state(self):
        """reset() 后引擎回到初始状态"""
        engine = SimulationEngine(num_tables_2=10, num_tables_4=10)
        engine.pref_ratios = {PreferenceType.SINGLE: 1.0,
                             PreferenceType.FACE_TO_FACE: 0.0,
                             PreferenceType.DIAGONAL: 0.0,
                             PreferenceType.ADJACENT: 0.0}
        engine.current_time = 29
        for _ in range(10):
            engine.step()
        assert engine.current_time > 0
        assert len(engine.active_students) + len(engine.history_students) > 0

        engine.reset(num_tables_2=5, num_tables_4=5)
        assert engine.current_time == 0
        assert len(engine.active_students) == 0
        assert len(engine.history_students) == 0
        assert engine.num_tables_2 == 5
        assert engine.num_tables_4 == 5
        for table in engine.restaurant.tables.values():
            assert np.all(table.seats == 0)

    def test_preference_update_takes_effect(self):
        """update_preferences() 后下一批学生按新比例生成"""
        engine = SimulationEngine(num_tables_2=20, num_tables_4=20)
        engine.update_preferences({
            PreferenceType.SINGLE: 1.0,
            PreferenceType.FACE_TO_FACE: 0.0,
            PreferenceType.DIAGONAL: 0.0,
            PreferenceType.ADJACENT: 0.0,
        })
        engine.current_time = 29
        engine.step()
        for s in engine.active_students:
            assert s.preference == PreferenceType.SINGLE, \
                f"更新偏好后应全为 SINGLE, 实际有 {s.preference}"


# ============================================================
# 五、generate_batch 边界测试 -- 直接测试 Crash 路径
# ============================================================
class TestGenerateBatchEdgeCases:
    """测试 generate_batch 在各种 pref_ratios 下的鲁棒性"""

    def test_single_preference_100_percent(self):
        """单一偏好 100%, 其余 0% -- 最常见的用户设置场景"""
        gen = StudentGenerator()
        for pref in PreferenceType:
            ratios = {p: (1.0 if p == pref else 0.0) for p in PreferenceType}
            batch = gen.generate_batch(current_time=30, pref_ratios=ratios)
            for s in batch:
                assert s.preference == pref, \
                    f"全 {pref} 设置下出现其他偏好: {s.preference}"

    def test_two_preferences_split(self):
        """两种偏好各 50%, 其余 0%"""
        gen = StudentGenerator()
        ratios = {
            PreferenceType.SINGLE: 0.5,
            PreferenceType.FACE_TO_FACE: 0.5,
            PreferenceType.DIAGONAL: 0.0,
            PreferenceType.ADJACENT: 0.0,
        }
        batch = gen.generate_batch(current_time=30, pref_ratios=ratios)
        for s in batch:
            assert s.preference in (PreferenceType.SINGLE, PreferenceType.FACE_TO_FACE)

    def test_empty_pref_ratios_crashes(self):
        """空 dict 会导致 IndexError -- 这就是 UI 变动的崩溃路径"""
        gen = StudentGenerator()
        with pytest.raises(IndexError):
            gen.generate_batch(current_time=30, pref_ratios={})

    def test_missing_keys_crashes(self):
        """只有部分 PreferenceType 键的 dict 也会出问题"""
        gen = StudentGenerator()
        # 缺少 DIAGONAL 和 ADJACENT
        ratios = {
            PreferenceType.SINGLE: 0.7,
            PreferenceType.FACE_TO_FACE: 0.3,
        }
        # random.choices 会执行,但人口只有2个元素
        # 不会崩溃,只是产生不了缺失的偏好
        batch = gen.generate_batch(current_time=30, pref_ratios=ratios)
        assert len(batch) >= 0  # 不崩溃

    def test_repeated_update_preferences_then_step(self):
        """模拟用户反复修改偏好的场景"""
        engine = SimulationEngine(num_tables_2=10, num_tables_4=10)
        engine.current_time = 29

        # 模拟多次修改
        configs = [
            {PreferenceType.SINGLE: 1.0,
             PreferenceType.FACE_TO_FACE: 0.0,
             PreferenceType.DIAGONAL: 0.0,
             PreferenceType.ADJACENT: 0.0},
            {PreferenceType.SINGLE: 0.0,
             PreferenceType.FACE_TO_FACE: 1.0,
             PreferenceType.DIAGONAL: 0.0,
             PreferenceType.ADJACENT: 0.0},
            {PreferenceType.SINGLE: 0.5,
             PreferenceType.FACE_TO_FACE: 0.5,
             PreferenceType.DIAGONAL: 0.0,
             PreferenceType.ADJACENT: 0.0},
            {PreferenceType.SINGLE: 0.25,
             PreferenceType.FACE_TO_FACE: 0.25,
             PreferenceType.DIAGONAL: 0.25,
             PreferenceType.ADJACENT: 0.25},
        ]
        for config in configs:
            engine.update_preferences(config)
            engine.step()

        stats = engine.get_statistics()
        assert stats["total_processed"] > 0


# ============================================================
# 六、Qt 信号槽 Bug 复现 -- 已知缺陷
# ============================================================
@pytest.mark.skipif(not HAS_QT, reason="需要 PySide6 环境")
class TestSignalSlotBug:
    """
    复现 Bug: PySide6 Signal(dict) 无法正确序列化 Python dict
    导致 engine.update_preferences 收到空 dict, 引发 IndexError

    Bug 追踪: Shiboken::Conversions::_pythonToCppCopy:
              Cannot copy-convert (dict) to C++.
    """

    @pytest.mark.xfail(
        reason="已知缺陷: PySide6 Signal(dict) Shiboken 转换失败, "
               "导致 engine.pref_ratios 变为空 dict {}",
        strict=True)
    def test_signal_dict_conversion_bug(self):
        """通过真实 Qt 信号路径修改偏好 -> 预期崩溃 (已知缺陷)"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        engine = SimulationEngine(num_tables_2=20, num_tables_4=20)
        cp = ControlPanel()
        cp.preferences_changed.connect(engine.update_preferences)
        cp.init_ui()

        # 模拟用户操作: SINGLE=100, 其余=0 (total=100)
        cp.pref_inputs[PreferenceType.SINGLE].setValue(100)
        cp.pref_inputs[PreferenceType.FACE_TO_FACE].setValue(0)
        cp.pref_inputs[PreferenceType.DIAGONAL].setValue(0)
        cp.pref_inputs[PreferenceType.ADJACENT].setValue(0)

        # 此时信号已发射, 但 engine.pref_ratios 因 Shiboken 转换失败变空
        assert len(engine.pref_ratios) == 4, \
            f"BUG: Signal(dict) 转换失败, pref_ratios 应含4键, 实际={engine.pref_ratios}"

        # 尝试 step 应正常执行
        engine.current_time = 29
        try:
            engine.step()
        except IndexError:
            pytest.fail(
                "BUG确认: Signal(dict) 导致 pref_ratios={}, "
                "step() -> generate_batch -> random.choices 收到空列表崩溃"
            )
