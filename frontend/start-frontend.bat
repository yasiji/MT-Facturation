@echo off
setlocal
cd /d %~dp0
if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=5173"
npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT% --strictPort
