@echo off
title JARVIS Neural Gesture OS
echo ========================================================
echo     JARVIS NEURAL GESTURE OS // ZERO-LAG CONTROLLER
echo ========================================================
echo Launching system with full hardware drivers...
cd /d "%~dp0"
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe scifi_gesture_controller.py
) else (
    python scifi_gesture_controller.py
)
pause
