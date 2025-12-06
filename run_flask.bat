@echo off
REM Building Defect Detection System - Quick Start Script

echo ========================================
echo Building Defect Detection System
echo Advanced AI-Powered Analysis
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip list | find "Flask" >nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed!
    echo.
)

REM Create necessary directories
if not exist "uploads\" mkdir uploads
if not exist "chat_history\" mkdir chat_history
if not exist "static\temp\" mkdir static\temp

echo.
echo ========================================
echo Starting Flask Application...
echo ========================================
echo.
echo Server will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run Flask app
python flask_app.py

pause
