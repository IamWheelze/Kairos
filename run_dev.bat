@echo off
REM Kairos Web UI - Development Mode (with detailed error messages)

echo ============================================================
echo Kairos Web UI - Development Mode
echo ============================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python found!
echo.

REM Check current directory
echo [2/5] Checking current directory...
echo Current directory: %CD%
if not exist "run_web_ui.py" (
    echo [ERROR] run_web_ui.py not found!
    echo Make sure you're in the Kairos directory
    pause
    exit /b 1
)
echo [OK] In correct directory
echo.

REM Check dependencies
echo [3/5] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FastAPI not installed!
    echo Run: pip install -r requirements-webui.txt
    echo.
    set /p INSTALL="Do you want to install now? (y/n): "
    if /i "%INSTALL%"=="y" (
        echo Installing dependencies...
        pip install -r requirements-webui.txt
        if errorlevel 1 (
            echo [ERROR] Installation failed!
            pause
            exit /b 1
        )
    ) else (
        echo Please install dependencies manually
        pause
        exit /b 1
    )
)
echo [OK] Dependencies installed
echo.

REM Check port availability
echo [4/5] Checking if port 8000 is available...
netstat -ano | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use!
    echo Will try port 3000 instead...
    set PORT=3000
) else (
    echo [OK] Port 8000 is available
    set PORT=8000
)
echo.

REM Start the server
echo [5/5] Starting Kairos Web Server...
echo ============================================================
echo.
echo Server will start on: http://localhost:%PORT%
echo.
echo OPEN YOUR BROWSER and go to:
echo   http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python run_web_ui.py --port %PORT% --reload

pause
