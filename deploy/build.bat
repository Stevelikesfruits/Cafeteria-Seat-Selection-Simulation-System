@echo off
chcp 65001 >nul
echo ============================================
echo   LunchroomSeatSim - Build Script
echo ============================================
echo.

REM Switch to project root
cd /d "%~dp0\.."

set PYTHON=D:\anaconda_24.10.1\envs_dirs\project_26_3_28\python.exe
echo Python: %PYTHON%
echo.

echo [1/3] Clean old builds...
if exist "build"   rmdir /s /q "build"
if exist "dist"    rmdir /s /q "dist"
if exist "deploy\dist"  rmdir /s /q "deploy\dist"

echo [2/3] PyInstaller build...
"%PYTHON%" -m PyInstaller deploy\LunchroomSimulator.spec
if %errorlevel% neq 0 (
    echo PyInstaller FAILED!
    pause
    exit /b %errorlevel%
)

echo [3/3] Fix MSVC DLL conflict + copy to deploy...
"%PYTHON%" deploy\fix_msvc.py
if %errorlevel% neq 0 (
    echo MSVC fix FAILED!
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================
echo   Build complete!
echo.
echo   Next: open deploy\setup.iss in Inno Setup
echo   Build -^> Compile (Ctrl+F9)
echo ============================================
pause
