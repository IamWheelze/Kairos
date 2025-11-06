@echo off
REM Kairos Web UI Launcher for Windows
REM This batch file launches the Kairos web interface

echo ============================================================
echo Kairos Voice-Activated Presentation Control - Web UI
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Starting Kairos Web Server...
echo.
echo Open your browser and navigate to:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Run the Python launcher
python run_web_ui.py %*

pause
