@echo off
set HOST=127.0.0.1
set PORT=8000

if exist backend\.env (
  for /f "usebackq tokens=1,2 delims==" %%i in (backend\.env) do set %%i=%%j
)

python -m uvicorn backend.main:app --host %HOST% --port %PORT% --reload

