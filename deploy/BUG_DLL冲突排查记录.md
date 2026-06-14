# PySide6 DLL 加载失败排查记录

## 症状

打包后的 exe 启动报错：

```
ImportError: DLL load failed while importing QtWidgets: 找不到指定的程序。
```

注意错误信息是 **"找不到指定的程序"**（The specified procedure could not be found），不是 "找不到指定的模块"（The specified module could not be found）。前者意味着 DLL 文件本身被找到了，但其中缺少某个函数 —— 这是**版本冲突**的典型信号。

## 根因

**conda 将 PySide6 拆成多个独立包**，各自携带不同版本的 MSVC 运行时 DLL：

```
conda site-packages/
├── PySide6/           ← Qt C++ 库 + 一套 MSVC DLL
├── PySide6_Addons/    ← Qt 扩展
├── PySide6_Essentials/
└── shiboken6/         ← 底层胶水库 + 另一套 MSVC DLL
```

PyInstaller 打包时从三个不同来源收集 MSVC 运行时：

| DLL 文件 | 来源 | 大小 |
|----------|------|------|
| `_internal/msvcp140.dll` | conda Python 根目录 | 557 KB |
| `_internal/vcruntime140.dll` | conda Python 根目录 | 124 KB |
| `_internal/PySide6/msvcp140.dll` | shiboken6 包 | 549 KB |
| `_internal/PySide6/vcruntime140.dll` | shiboken6 包 | 116 KB |

**同一个 DLL 存在两个不兼容版本**，分别放在两个目录。

Windows 加载 DLL 的搜索顺序：先搜 `_internal/`（exe 同级目录），再搜 `_internal/PySide6/`。因此根目录的旧版 MSVC 先被加载，Qt6Core.dll 需要的函数在旧版中不存在 → 报错。

## 排查过程（弯路记录）

1. **误判一：以为是 shiboken6.abi3.dll 路径问题** — 因为 conda 把它放在独立目录，以为 Windows 搜索不到。创建了 `runtime_hook.py` 用 `os.add_dll_directory()` 注册路径，无效。

2. **误判二：以为是 PyInstaller 选择性收集导致缺文件** — 写 spec 强制收集全部 PySide6 DLL，仍然无效。

3. **误判三：以为替换 MSVC DLL 能解决** — 用 shiboken6 的版本覆盖根目录，但 PySide6 自己还有第三套版本（既不同于 conda 根也不同于 shiboken6），三套版本互不兼容。

4. **误判四：以为合并所有 DLL 到同一目录即可** — 把根目录 DLL 全移入 PySide6 目录，结果 `python39.dll` 也被移走，PyInstaller 引导程序找不到 Python 解释器。

5. **关键发现**：用 `subprocess.run` 测试 exe，看到 "进程仍在运行" 就认为成功了。实际上进程没退出是因为 Qt 弹出了错误对话框在等待用户点击 OK —— **假阳性**。

## 最终方案

三步修复：

### 1. 换用 pip 版 PySide6

conda 的拆分打包是万恶之源。pip 版是单一 wheel，所有文件同源同版本：

```bash
pip uninstall PySide6 PySide6_Addons PySide6_Essentials shiboken6 -y
pip install PySide6
```

### 2. 构建后完整替换

`fix_msvc.py` 在 PyInstaller 构建完成后，用完整的 pip 源目录覆盖冷冻版的 PySide6：

```python
# 删除 PyInstaller 选择性收集的残缺版
shutil.rmtree(frozen_py6)
# 复制 pip 源的完整版
shutil.copytree(src_pyside6, frozen_py6)
# 补充 shiboken6.abi3.dll（唯一不在 PySide6 目录的文件）
shutil.copy2(shiboken6.abi3.dll, frozen_py6)
```

### 3. 合并非 Python DLL

把所有非 Python 系统 DLL（MSVC、api-ms-*、ucrtbase 等）从根目录移入 PySide6/，消除多目录搜索带来的版本冲突。**保留 python39.dll 在根目录**（PyInstaller 引导程序需要它在原位）。

## 教训

1. **"找不到指定的程序" ≠ 找不到文件**，而是函数缺失 → 版本冲突
2. **不要相信 subprocess.poll() 判断 GUI 程序是否正常**，弹窗错误不会让进程退出
3. **conda + PyInstaller + PySide6 是高风险组合**，优先级：pip wheel > conda
4. **先查 MD5**：`_internal/*.dll` 和 `_internal/PySide6/*.dll` 是否一致
