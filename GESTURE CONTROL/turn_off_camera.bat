@echo off
echo ===================================================
echo     Instant Camera Release & Hardware Reset
echo ===================================================
echo Terminating any leftover camera processes...
powershell -Command "& { Stop-Process -Name 'ShellHost' -Force -ErrorAction SilentlyContinue; Get-Process | Where-Object { $_.ProcessName -like '*python*' } | Stop-Process -Force -ErrorAction SilentlyContinue; Restart-Service FrameServer -ErrorAction SilentlyContinue; Write-Host 'Camera successfully released and reset!' -ForegroundColor Green }"
echo Done! Camera light is OFF.
timeout /t 3
