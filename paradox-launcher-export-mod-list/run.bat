@echo off
title Paradox Mod List Extractor
echo Starting Mod List Extractor...
echo.

:: Try running with the standard 'python' command
python "paradox-launcher-export-mod-list.py"

:: If the previous command failed (ERRORLEVEL 9009 means command not found), try the 'py' launcher
if %ERRORLEVEL% NEQ 0 (
    echo 'python' command not found, trying 'py' launcher...
    py "paradox-launcher-export-mod-list.py"
)

:: If that also fails, show a helpful message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo ERROR: Could not find Python.
    echo Please make sure Python is installed and added to your PATH.
    echo You can download it from https://www.python.org/downloads/
    echo ========================================================
    echo.
)

pause