@echo off
title PyPAKMA - Physics Simulation Studio
echo ========================================================
echo       Starting PyPAKMA (Python Physics Studio)          
echo ========================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b
)

:: Check and install dependencies from requirements.txt
echo [INFO] Checking and installing dependencies...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

:: Launch Application
echo [INFO] Launching PyPAKMA Application...
python main.py

if %errorlevel% neq 0 (
    echo [ERROR] Application exited with an error.
    pause
)
