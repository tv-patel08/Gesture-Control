@echo off
title Push to GitHub - Gesture Control
echo ========================================================
echo       PUSHING TO GITHUB: tv-patel08/Gesture-Control
echo ========================================================
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ----------------------------------------------------
    echo If the push failed with 'Repository not found':
    echo 1. Make sure you have created the repository 'Gesture-Control'
    echo    on GitHub: https://github.com/new
    echo 2. Run this script again!
    echo ----------------------------------------------------
) else (
    echo.
    echo ========================================================
    echo Successfully pushed to https://github.com/tv-patel08/Gesture-Control!
    echo ========================================================
)
pause
