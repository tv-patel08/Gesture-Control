@echo off
title Reset Windows Desktop Icons
color 0A
echo =================================================================
echo        WINDOWS DESKTOP ICON RESTORER (MEDIUM / DEFAULT)
echo =================================================================
echo.
echo Restoring Desktop Icon size to standard Medium (48px)...
powershell -Command "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\Shell\Bags\1\Desktop' -Name IconSize -Value 48; Stop-Process -Name explorer -Force; Start-Sleep -Seconds 1; Start-Process explorer"
echo.
echo [OK] Windows Explorer refreshed!
echo Your desktop icons have been restored to their original Medium size.
echo.
pause
