@echo off
title STOP JARVIS Gesture Controller
color 0C
echo ========================================================
echo        TURNING OFF GESTURE CONTROL & CAMERA...
echo ========================================================
echo.
powershell -Command "& { Get-Process | Where-Object { $_.ProcessName -like '*python*' } | Stop-Process -Force -ErrorAction SilentlyContinue; Stop-Process -Name 'ShellHost' -Force -ErrorAction SilentlyContinue; Write-Host 'Gesture controller stopped. Camera turned OFF.' -ForegroundColor Green }"
echo.
echo ========================================================
echo [SUCCESS] Gesture Control is OFF and Camera light is OFF!
echo ========================================================
timeout /t 3
