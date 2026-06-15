# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 文件 — 午餐餐厅座位分配仿真系统
构建命令: pyinstaller deploy/LunchroomSimulator.spec
"""

import sys
import os
from pathlib import Path

# 项目根目录 — PyInstaller 从项目根目录运行, 直接使用 os.getcwd()
# 注意: build.bat 会先 cd 到项目根目录再调用 PyInstaller
PROJECT_ROOT = Path(os.getcwd())

# ---------- PyInstaller 隐藏导入 ----------
# PySide6 框架相关 (确保 Qt 插件和 DLL 被收集)
hidden_imports = [
    # PySide6 核心
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtCharts',
    # numpy C 扩展
    'numpy._core._methods',
    'numpy._core.multiarray',
    'numpy._core.umath',
    'numpy.random._common',
    'numpy.random.bit_generator',
    'numpy.random._bounded_integers',
    'numpy.random._mt19937',
    'numpy.random._pcg64',
    'numpy.random._philox',
    'numpy.random._sfc64',
    'numpy.random._generator',
    'numpy.linalg',
    # matplotlib 后端
    'matplotlib',
    'matplotlib.backends.backend_qtagg',
    'matplotlib.backends.backend_svg',
    # pandas
    'pandas._libs',
    # PyYAML
    'yaml',
    # loguru
    'loguru',
]

# ---------- 排除不必要的模块 (减小体积) ----------
excluded_imports = [
    'black',
    'flake8',
    'pytest',
    'pip',
    'setuptools',
    'tkinter',
    'test',
    'email',
    'http',
    'xmlrpc',
    'pydoc',
]

# ---------- 收集的数据文件 ----------
# matplotlib 字体数据 + Qt 配置文件
datas = [
    # matplotlib 字体（确保图表中文显示）
    (str(Path(sys.base_prefix) / 'Lib' / 'site-packages' / 'matplotlib' / 'mpl-data'), 'matplotlib/mpl-data'),
    # qt.conf — 告诉 Qt 去哪里找插件（修复 DLL load failed 问题）
    (str(PROJECT_ROOT / 'deploy' / 'qt.conf'), 'PySide6/qt.conf'),
]

# ---------- 收集的二进制文件 ----------
# 完整复制 PySide6 + shiboken6 的所有 .dll/.pyd 到同一目录
# 避免 PyInstaller hook 选择性收集导致缺文件
_pyside6_dir = Path(sys.base_prefix) / 'Lib' / 'site-packages' / 'PySide6'
_shiboken6_dir = Path(sys.base_prefix) / 'Lib' / 'site-packages' / 'shiboken6'

binaries = (
    # shiboken6 全部二进制 → PySide6/
    [(str(_shiboken6_dir / f), 'PySide6')
     for f in os.listdir(str(_shiboken6_dir))
     if f.endswith(('.dll', '.pyd'))]
    +
    # PySide6 全部二进制 → PySide6/ (force-include 整个包)
    [(str(_pyside6_dir / f), 'PySide6')
     for f in os.listdir(str(_pyside6_dir))
     if f.endswith(('.dll', '.pyd'))]
    +
    # 用 shiboken6 的 MSVC 运行时覆盖根目录（解决版本冲突！）
    [(str(_shiboken6_dir / f), '.')
     for f in os.listdir(str(_shiboken6_dir))
     if f.startswith(('vcruntime', 'msvcp', 'vcomp', 'vcamp', 'vccorlib', 'concrt'))
     and f.endswith('.dll')]
)

# ---------- spec 入口 ----------
a = Analysis(
    [str(PROJECT_ROOT / 'main_ui.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(PROJECT_ROOT / 'deploy' / 'runtime_hook.py')],
    excludes=excluded_imports,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 过滤掉不需要的大文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ---------- EXE 配置 (one-folder 模式) ----------
exe = EXE(
    pyz,
    a.scripts,
    [],      # one-folder: binaries 留给 COLLECT
    [],
    [],      # one-folder: datas 留给 COLLECT
    name='午餐座位仿真系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / 'deploy' / 'app.ico') if (PROJECT_ROOT / 'deploy' / 'app.ico').exists() else None,
)

# ---------- COLLECT: 收集所有文件到输出目录 ----------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='午餐座位仿真系统',
)
