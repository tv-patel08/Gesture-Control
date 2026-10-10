@echo off
title JARVIS Neural Gesture OS
echo ========================================================
echo       JARVIS NEURAL GESTURE OS // INSTANT LAUNCHER
echo ========================================================
echo Initializing hardware vision pipeline...
cd /d "%~dp0\GESTURE CONTROL"
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe scifi_gesture_controller.py
) else (
    python scifi_gesture_controller.py
)
if errorlevel 1 (
    echo.
    echo System exited with an alert. Press any key to close.
    pause >nul
)
