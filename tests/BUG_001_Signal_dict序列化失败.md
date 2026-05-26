# Bug 追踪: Signal(dict) 序列化失败导致偏好更新崩溃

**编号**: BUG-001
**发现日期**: 2026-05-23
**严重程度**: 高 (阻断核心功能)
**状态**: 未修复 / 待处理

---

## 现象

用户在 GUI 中修改偏好占比后启动仿真，程序崩溃：

```
IndexError: list index out of range
  File "random.py", line 500, in choices
    total = cum_weights[-1] + 0.0
```

伴随 stderr 警告：
```
Shiboken::Conversions::_pythonToCppCopy: Cannot copy-convert (dict) to C++.
```

**触发条件**: 只要偏好占比总和达到 100%（即触发 `preferences_changed` 信号发射），就会崩溃。

---

## 根因

`ui/control_panel.py` 第 13 行：

```python
preferences_changed = Signal(dict)
```

**PySide6 的 Shiboken 绑定层无法将 Python `dict` 类型序列化为 C++ 类型以通过 Qt 信号槽传递。** 当 `preferences_changed.emit(dict_value)` 执行时：

1. Shiboken 尝试将 Python dict 复制转换为 C++ 等价类型 — 失败
2. 但信号**仍然触发了槽函数**
3. 槽函数 `engine.update_preferences` 收到的参数是 **空 dict `{}`**
4. `engine.pref_ratios = {}` — 偏好字典被覆盖为空
5. 下一次 `step()` → `generate_batch(current_time, {})` → `random.choices([], weights=[])` → `IndexError`

## 完整崩溃链

```
用户调整 SpinBox -> total == 100%
  -> on_pref_changed() 构造 new_ratios = {SINGLE: 0.3, ...}
  -> preferences_changed.emit(new_ratios)    # Shiboken dict 转换失败
  -> engine.update_preferences({})           # 槽函数收到空 dict
  -> engine.step() -> generate_batch(t, {})  # pref_ratios = {}
  -> random.choices([], weights=[])          # 空列表
  -> cum_weights[-1]                         # IndexError
```

## 复现测试

`tests/test_integration.py::TestSignalSlotBug::test_signal_dict_conversion_bug`

该测试通过创建 QApplication + ControlPanel + Signal 连接的完整 Qt 路径复现，标记为 `pytest.mark.xfail` (expected failure)。

## 修复方案

将 `Signal(dict)` 改为 `Signal(object)`：

```python
# ui/control_panel.py 第 13 行
# 修改前:
preferences_changed = Signal(dict)

# 修改后:
preferences_changed = Signal(object)
```

`Signal(object)` 允许传递任意 Python 对象，不会触发 Shiboken 的类型转换。

## 影响范围

| 文件 | 行号 | 影响 |
|------|------|------|
| `ui/control_panel.py` | 13 | Signal 声明 |
| `ui/control_panel.py` | 117 | emit 调用 (无需修改) |
| `ui/main_window.py` | 116 | connect 调用 (无需修改) |
| `core/simulation.py` | 31-33 | update_preferences 无需修改 |
