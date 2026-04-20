import sys
import os

# 将当前目录加入系统路径，确保能正确导入 models 和 core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.simulation import SimulationEngine


def run_backend_test():
    print("=" * 40)
    print("🚀 餐厅仿真后端脱机测试开始")
    print("=" * 40)

    # 1. 初始化仿真引擎
    engine = SimulationEngine()

    # 设定模拟时长，例如模拟中午高峰期 60 分钟
    total_simulation_time = 60
    print(f"设定仿真时长: {total_simulation_time} 分钟\n")

    # 2. 开始时间循环
    for current_minute in range(1, total_simulation_time + 1):
        # 推进一分钟的仿真
        engine.step()

        # 获取实时统计数据
        stats = engine.get_statistics()

        # 为了避免控制台刷屏，我们选择每 5 分钟或者在第 1 分钟时打印一次状态
        if current_minute % 5 == 0 or current_minute == 1:
            print(f"[第 {current_minute:02d} 分钟] 状态快照:")
            print(f"  🍽️  当前正在就餐人数: {stats['active_diners']}")
            print(f"  🚶  累计处理总人数: {stats['total_processed']}")
            print(f"  ⭐  当前综合满意度: {stats['total_satisfaction_score']}")
            print("-" * 30)

    # 3. 输出最终结果报告
    print("\n" + "=" * 40)
    print("📊 仿真脱机测试结束 - 最终报告")
    print("=" * 40)
    final_stats = engine.get_statistics()
    print(f"总计仿真时间: {final_stats['current_time']} 分钟")
    print(f"总计接待/处理学生数: {final_stats['total_processed']} 人")
    print(f"结束时仍在就餐人数: {final_stats['active_diners']} 人")
    print(f"最终综合满意度得分: {final_stats['total_satisfaction_score']} 分")

    # 简单验证一下逻辑是否正常
    if final_stats['total_processed'] > 0:
        print("\n✅ 测试结论: 引擎成功生成并处理了学生数据。")
    else:
        print("\n❌ 测试结论: 没有处理任何学生，请检查 student_generator 的逻辑。")


if __name__ == "__main__":
    run_backend_test()