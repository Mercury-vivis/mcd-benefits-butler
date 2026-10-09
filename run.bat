@echo off
chcp 65001 >nul 2>&1
setlocal

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.8+ and tick "Add to PATH", then retry.
    echo [ERROR] See the install guide inside the docs/ folder (小白安装指南.md).
    pause
    exit /b 1
)

python src/run_wizard.py
if errorlevel 1 pause

endlocal
