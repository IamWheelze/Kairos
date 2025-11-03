@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0..
set VENV=%ROOT%\.venv
set PY=%VENV%\Scripts\python.exe

if not exist "%VENV%" (
  echo [+] Creating virtualenv (.venv) with Python 3.11
  py -3.11 -m venv "%VENV%"
)

if not exist "%PY%" (
  echo [x] venv python not found at %PY%
  exit /b 1
)

echo [+] Upgrading pip, setuptools, wheel
"%PY%" -m pip install --upgrade pip setuptools wheel

echo [+] Installing dependencies
"%PY%" -m pip install -r "%ROOT%\backend\requirements.txt"

if not exist "%ROOT%\backend\.env" (
  if exist "%ROOT%\backend\.env.example" copy "%ROOT%\backend\.env.example" "%ROOT%\backend\.env" >nul
)

echo.
echo [!] Configure ProPresenter in backend\.env if needed, then press any key to start the server...
pause >nul

echo [+] Starting Kairos at http://127.0.0.1:8000
"%PY%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

endlocal

