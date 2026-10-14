@echo off
title Pathfinding Visualizer - Python Source Code
cd /d "%~dp0"
echo ========================================================
echo   KHOI DONG MO PHONG THUAT TOAN TU SOURCE PYTHON...
echo ========================================================
python main.py
if errorlevel 1 (
    echo.
    echo [LOI] Khong the khoi dong. Hay kiem tra xem may da cai Python va cac thu vien:
    echo        pip install -r requirements.txt
    echo.
    pause
)

