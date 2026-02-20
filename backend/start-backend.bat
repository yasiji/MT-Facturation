@echo off
setlocal
cd /d "%~dp0"
set "PYTHONHOME="
if "%BACKEND_PORT%"=="" set "BACKEND_PORT=8000"
set "BACKEND_RELOAD_FLAG="
if /I "%BACKEND_ENABLE_RELOAD%"=="true" set "BACKEND_RELOAD_FLAG=--reload"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% %BACKEND_RELOAD_FLAG%
  exit /b %errorlevel%
)

python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT% %BACKEND_RELOAD_FLAG%
