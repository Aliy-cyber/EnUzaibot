@echo off
chcp 65001 >nul
echo ==========================================
echo    ENG-UZB Dictionary Bot ishga tushmoqda
echo ==========================================
echo.

cd /d "%~dp0"

REM Kutubxonalar o'rnatilganligini tekshirish
pip show aiogram >nul 2>&1
if errorlevel 1 (
    echo [*] Kutubxonalar o'rnatilmoqda...
    pip install -r requirements.txt
    echo.
)

echo [+] Bot ishga tushmoqda...
echo [+] To'xtatish uchun Ctrl+C bosing
echo.
set PYTHONIOENCODING=utf-8
python bot.py

pause
