# deploy/runtime_hook.py
# PyInstaller 自定义运行时钩子 — 修复 PySide6 DLL 搜索路径问题
# 在 main_ui.py 执行前运行，确保 Windows 能找到所有必要的 DLL

import os
import sys


def _pyi_rthook():
    # sys._MEIPASS 是 PyInstaller 解压/存放所有依赖的临时/持久目录
    # one-folder 模式下即 _internal 文件夹
    base = sys._MEIPASS

    # Windows 上使用 os.add_dll_directory() 添加 DLL 搜索路径 (Python 3.8+)
    if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
        # PySide6 的 Qt DLL 和 Python 绑定 (.pyd)
        dll_dirs = [
            base,                              # 根目录 (vcruntime140.dll 等)
            os.path.join(base, 'PySide6'),     # Qt6*.dll, pyside6.abi3.dll
            os.path.join(base, 'shiboken6'),   # shiboken6.abi3.dll (PySide6 依赖)
        ]
        for d in dll_dirs:
            if os.path.isdir(d):
                try:
                    os.add_dll_directory(d)
                except Exception:
                    pass


_pyi_rthook()
del _pyi_rthook
