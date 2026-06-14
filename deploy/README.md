# 午餐座位仿真系统 — 部署指南

## 整体流程

```
源代码 (.py)
    │
    ▼  PyInstaller (build.bat)
独立可执行文件夹 (dist/)
    │
    ▼  Inno Setup (setup.iss)
Windows 安装包 (Setup.exe + 卸载工具)
```

## 所需工具

| 工具 | 用途 | 下载 |
|------|------|------|
| Python 环境 | 开发时已有 | `D:\anaconda_24.10.1\envs_dirs\project_26_3_28` |
| PyInstaller 6.19 | 已安装在项目环境 | -- |
| Inno Setup 6+ | 制作安装包 | https://jrsoftware.org/isinfo.php |

## 步骤一: 打包 Python 程序

运行构建脚本:
```
双击 deploy\build.bat
```

或在终端中执行:
```bat
cd /d D:\软件实训\App
D:\anaconda_24.10.1\envs_dirs\project_26_3_28\python.exe -m PyInstaller deploy\LunchroomSimulator.spec
```

产物位于 `deploy\dist\午餐座位仿真系统\` (约 257 MB，包含 Python 运行时 + 所有依赖库)。

## 步骤二: 制作 Windows 安装包

1. 下载安装 [Inno Setup](https://jrsoftware.org/isinfo.php)
2. 打开 `deploy\setup.iss`
3. 点击菜单 **Build → Compile** (或按 Ctrl+F9)
4. 安装包生成到 `deploy\Output\`

生成的文件: `午餐座位仿真系统_Setup_v1.0.0.exe`

## 安装包特性

- ✅ 双击安装，标准 Windows 安装向导
- ✅ 自动创建开始菜单快捷方式
- ✅ 可选创建桌面快捷方式
- ✅ **内置卸载工具** (开始菜单 → 卸载，或控制面板 → 程序和功能)
- ✅ 无需安装 Python，新机器可直接运行
- ✅ 中文安装界面

## 在新机器上运行

1. 将 `午餐座位仿真系统_Setup_v1.0.0.exe` 复制到目标机器
2. 双击运行，按向导安装
3. 安装完成后即可使用

卸载方式:
- 开始菜单 → 午餐座位仿真系统 → 卸载
- 或: 控制面板 → 程序和功能 → 午餐座位仿真系统 → 卸载

## 自定义版本号

编辑 `deploy\setup.iss`，修改:
```
#define MyAppVersion     "1.0.0"     ← 改这里
```

编辑 `deploy\LunchroomSimulator.spec`，修改 `name=` 可改应用名称。

## 目录结构

```
App/
├── deploy/
│   ├── build.bat                   ← 一键构建脚本
│   ├── LunchroomSimulator.spec     ← PyInstaller 配置
│   ├── setup.iss                   ← Inno Setup 安装脚本
│   ├── app.ico                     ← 应用图标
│   ├── dist/                       ← PyInstaller 产物 (build.bat 自动生成)
│   └── Output/                     ← 最终安装包 (Inno Setup 编译生成)
├── models/                         ← 数据模型
├── core/                           ← 核心算法
├── ui/                             ← 用户界面
├── tests/                          ← 测试
└── main_ui.py                      ← 程序入口
```
