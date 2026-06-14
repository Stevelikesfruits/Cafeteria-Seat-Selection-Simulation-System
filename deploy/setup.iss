; ============================================================
; Inno Setup 安装脚本 — 午餐座位分配仿真系统
;
; 使用方法:
;   1. 先运行 build.bat 完成 PyInstaller 打包
;   2. 用 Inno Setup 打开此文件, 点击"编译" (Compile)
;   3. 生成的安装包在 deploy\Output\ 目录
;
; Inno Setup 下载: https://jrsoftware.org/isinfo.php
; ============================================================

#define MyAppName        "午餐座位仿真系统"
#define MyAppNameEn      "LunchroomSeatSim"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Steve"
#define MyAppURL         ""
#define MyAppExeName     "午餐座位仿真系统.exe"
; 源文件路径 (build.bat 会将 PyInstaller 输出复制到此)
#define MyAppSource      "dist\午餐座位仿真系统\"

[Setup]
; 安装包标识 (GUID — 每个应用应该唯一, 换新项目时重新生成)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 默认安装路径: C:\Program Files\午餐座位仿真系统
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; 禁止选择其他安装路径 (可改为 yes 允许用户修改)
DisableDirPage=no

; 输出目录
OutputDir=Output
; 输出文件名
OutputBaseFilename=午餐座位仿真系统_Setup_v{#MyAppVersion}

; 安装包图标
SetupIconFile=app.ico

; 压缩方式
Compression=lzma2/ultra64
SolidCompression=yes

; 界面设置
WizardStyle=modern
WizardSizePercent=100,100

; 安装程序的管理员权限请求
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

; 语言
[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

; ------------------------ 安装的文件 ------------------------
[Files]
; 主程序和所有依赖文件从 PyInstaller 输出目录复制
Source: "{#MyAppSource}*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ------------------------ 开始菜单快捷方式 ------------------------
[Icons]
; 开始菜单
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; 开始菜单 — 卸载
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"

; ------------------------ 可选: 桌面快捷方式 ------------------------
[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ------------------------ 注册表 (用于控制面板→程序和功能) ------------------------
; Inno Setup 会自动写入卸载信息，这里补充版本号等信息
[Registry]
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEn}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEn}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEn}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"

; ------------------------ 安装后运行 ------------------------
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent
