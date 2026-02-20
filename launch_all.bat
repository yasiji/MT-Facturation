@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==============================================
REM MT-Facturation one-shot launcher (Windows)
REM - Bootstraps backend virtualenv if missing
REM - Installs dependencies
REM - Performs dependency checks
REM - Starts backend and frontend
REM ==============================================

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "BACKEND_DIR=%ROOT_DIR%\backend"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"
set "BACKEND_VENV=%BACKEND_DIR%\.venv"

set "BACKEND_START_BAT=%BACKEND_DIR%\start-backend.bat"
set "FRONTEND_START_BAT=%FRONTEND_DIR%\start-frontend.bat"

set "BACKEND_APP=app.main:app"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

set "DB_HOST=localhost"
set "DB_PORT=5432"
set "DB_USER=postgres"
set "DB_PASSWORD=Yassine1@;"
set "DB_NAME=mt_facturation"
set "PYTHONHOME="

set "PY_BOOTSTRAP="
set "STARTED_ANY=0"
set "SMOKE_TIMEOUT_SECONDS=45"

echo [INFO] Root directory: %ROOT_DIR%
echo [INFO] Checking required tooling...

where py >nul 2>nul
if not errorlevel 1 (
    set "PY_BOOTSTRAP=py -3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PY_BOOTSTRAP=python"
    ) else (
        echo [ERROR] Python was not found. Install Python 3.12+ and retry.
        exit /b 1
    )
)

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js was not found. Install Node.js and retry.
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm was not found. Install npm and retry.
    exit /b 1
)

echo [INFO] Tooling check passed.
echo [INFO] Cleaning stale launcher windows and port listeners...
call :stop_window_title "MT-Facturation Backend"
call :stop_window_title "MT-Facturation Frontend"
call :stop_backend_runtime_processes
powershell -NoProfile -Command "$port=%BACKEND_PORT%; for($i=0; $i -lt 8; $i++){ $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if(-not $conns){ break }; $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; $kill = New-Object 'System.Collections.Generic.HashSet[int]'; foreach($pid in $pids){ if($pid -gt 0){ [void]$kill.Add([int]$pid); try { $proc = Get-CimInstance Win32_Process -Filter \"ProcessId=$pid\" -ErrorAction Stop; if($proc.ParentProcessId -gt 0){ [void]$kill.Add([int]$proc.ParentProcessId) } } catch {} } }; foreach($k in $kill){ Stop-Process -Id $k -Force -ErrorAction SilentlyContinue }; Start-Sleep -Milliseconds 500 }" >nul 2>nul
powershell -NoProfile -Command "$port=%FRONTEND_PORT%; for($i=0; $i -lt 8; $i++){ $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if(-not $conns){ break }; $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; foreach($pid in $pids){ if($pid -gt 0){ Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } }; Start-Sleep -Milliseconds 500 }" >nul 2>nul
powershell -NoProfile -Command "$port=%BACKEND_PORT%; $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($conn) { exit 0 } else { exit 1 }" >nul 2>nul
if not errorlevel 1 (
    echo [WARN] Backend port %BACKEND_PORT% is still busy after cleanup. Falling back to port 8010.
    set "BACKEND_PORT=8010"
    powershell -NoProfile -Command "$port=%BACKEND_PORT%; for($i=0; $i -lt 8; $i++){ $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if(-not $conns){ break }; $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; foreach($pid in $pids){ if($pid -gt 0){ Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } }; Start-Sleep -Milliseconds 500 }" >nul 2>nul
)
powershell -NoProfile -Command "$port=%FRONTEND_PORT%; $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($conn) { exit 0 } else { exit 1 }" >nul 2>nul
if not errorlevel 1 (
    echo [WARN] Frontend port %FRONTEND_PORT% is still busy after cleanup. Falling back to port 5174.
    set "FRONTEND_PORT=5174"
    powershell -NoProfile -Command "$port=%FRONTEND_PORT%; for($i=0; $i -lt 8; $i++){ $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if(-not $conns){ break }; $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; foreach($pid in $pids){ if($pid -gt 0){ Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } }; Start-Sleep -Milliseconds 500 }" >nul 2>nul
)

REM ---------------------------
REM Backend bootstrap + checks
REM ---------------------------
if exist "%BACKEND_DIR%" (
    echo [INFO] Backend directory found: %BACKEND_DIR%

    pushd "%BACKEND_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to enter backend directory.
        exit /b 1
    )

    if not exist ".venv\Scripts\python.exe" (
        echo [INFO] Backend virtual environment missing, creating: %BACKEND_VENV%
        call %PY_BOOTSTRAP% -m venv "%BACKEND_VENV%"
        if errorlevel 1 (
            popd
            echo [ERROR] Failed to create backend virtual environment.
            exit /b 1
        )
    ) else (
        echo [INFO] Backend virtual environment found.
    )

    call ".venv\Scripts\activate.bat"
    if errorlevel 1 (
        popd
        echo [ERROR] Failed to activate backend virtual environment.
        exit /b 1
    )

    python -m pip install --upgrade pip
    if errorlevel 1 (
        popd
        echo [ERROR] Failed to upgrade pip.
        exit /b 1
    )

    if exist "requirements.txt" (
        echo [INFO] Installing backend dependencies from requirements.txt
        python -m pip install -r "requirements.txt"
        if errorlevel 1 (
            popd
            echo [ERROR] Backend dependency installation failed.
            exit /b 1
        )
    ) else (
        if exist "pyproject.toml" (
            echo [INFO] Installing backend package from pyproject.toml
            python -m pip install -e "."
            if errorlevel 1 (
                popd
                echo [ERROR] Backend package installation failed.
                exit /b 1
            )
        ) else (
            echo [WARN] No backend dependency file found: requirements.txt or pyproject.toml.
        )
    )

    echo [INFO] Running backend dependency check: pip check
    python -m pip check
    if errorlevel 1 (
        popd
        echo [ERROR] Backend dependency check failed.
        exit /b 1
    )

    set "PGHOST=%DB_HOST%"
    set "PGPORT=%DB_PORT%"
    set "PGUSER=%DB_USER%"
    set "PGPASSWORD=%DB_PASSWORD%"
    set "PGDATABASE=%DB_NAME%"
    set "PYTHONPATH=%BACKEND_DIR%"

    echo [INFO] Running backend DB bootstrap: create database and initialize schema
    python -m app.db.bootstrap
    if errorlevel 1 (
        popd
        echo [ERROR] Backend DB bootstrap failed. Ensure PostgreSQL is running and credentials are valid.
        exit /b 1
    )

    popd

    if exist "%BACKEND_START_BAT%" (
        echo [INFO] Starting backend using custom starter: %BACKEND_START_BAT%
        start "MT-Facturation Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && call ""%BACKEND_VENV%\Scripts\activate.bat"" && set ""PGHOST=%DB_HOST%"" && set ""PGPORT=%DB_PORT%"" && set ""PGUSER=%DB_USER%"" && set ""PGPASSWORD=%DB_PASSWORD%"" && set ""PGDATABASE=%DB_NAME%"" && set ""BACKEND_ENABLE_RELOAD=false"" && set ""BACKEND_PORT=%BACKEND_PORT%"" && call ""%BACKEND_START_BAT%"""
        set "STARTED_ANY=1"
    ) else (
        if exist "%BACKEND_DIR%\app\main.py" (
            echo [INFO] Starting backend with uvicorn fallback...
            start "MT-Facturation Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && call ""%BACKEND_VENV%\Scripts\activate.bat"" && set ""PGHOST=%DB_HOST%"" && set ""PGPORT=%DB_PORT%"" && set ""PGUSER=%DB_USER%"" && set ""PGPASSWORD=%DB_PASSWORD%"" && set ""PGDATABASE=%DB_NAME%"" && python -m uvicorn %BACKEND_APP% --host 0.0.0.0 --port %BACKEND_PORT%"
            set "STARTED_ANY=1"
        ) else (
            echo [WARN] No backend start file found. Expected:
            echo        - %BACKEND_START_BAT%
            echo        - or %BACKEND_DIR%\app\main.py
        )
    )
) else (
    echo [WARN] Backend directory not found at %BACKEND_DIR%. Backend launch skipped.
)

REM ----------------------------
REM Frontend bootstrap + checks
REM ----------------------------
if exist "%FRONTEND_DIR%" (
    echo [INFO] Frontend directory found: %FRONTEND_DIR%

    pushd "%FRONTEND_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to enter frontend directory.
        exit /b 1
    )

    if not exist "node_modules" (
        if exist "package-lock.json" (
            echo [INFO] Frontend node_modules missing. Installing with npm ci...
            call npm ci
        ) else (
            echo [INFO] Frontend node_modules missing. Installing with npm install...
            call npm install
        )
        if errorlevel 1 (
            popd
            echo [ERROR] Frontend dependency installation failed.
            exit /b 1
        )
    ) else (
        echo [INFO] Frontend node_modules found. Verifying dependency health...
        call npm ls --depth=0 >nul
        if errorlevel 1 (
            echo [WARN] Frontend dependency health check failed. Repairing with npm install...
            call npm install
            if errorlevel 1 (
                popd
                echo [ERROR] Frontend dependency repair failed.
                exit /b 1
            )
        ) else (
            echo [INFO] Frontend dependencies are healthy. Skipping reinstall.
        )
    )

    echo [INFO] Running frontend dependency check: npm ls --depth=0
    call npm ls --depth=0 >nul
    if errorlevel 1 (
        popd
        echo [ERROR] Frontend dependency check failed.
        exit /b 1
    )
    popd

    if exist "%FRONTEND_START_BAT%" (
        echo [INFO] Starting frontend using custom starter: %FRONTEND_START_BAT%
        start "MT-Facturation Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && set ""VITE_API_BASE_URL=http://localhost:%BACKEND_PORT%"" && set ""FRONTEND_PORT=%FRONTEND_PORT%"" && call ""%FRONTEND_START_BAT%"""
        set "STARTED_ANY=1"
    ) else (
        if exist "%FRONTEND_DIR%\package.json" (
            echo [INFO] Starting frontend with npm run dev fallback...
            start "MT-Facturation Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && set ""VITE_API_BASE_URL=http://localhost:%BACKEND_PORT%"" && npm run dev -- --host 0.0.0.0 --port %FRONTEND_PORT% --strictPort"
            set "STARTED_ANY=1"
        ) else (
            echo [WARN] No frontend start file found. Expected:
            echo        - %FRONTEND_START_BAT%
            echo        - or %FRONTEND_DIR%\package.json
        )
    )
) else (
    echo [WARN] Frontend directory not found at %FRONTEND_DIR%. Frontend launch skipped.
)

if "%STARTED_ANY%"=="0" (
    echo [ERROR] No service was started. Ensure backend/frontend project folders exist.
    exit /b 1
)

echo [INFO] Running smoke checks...
call :wait_for_http_get "Backend health" "http://127.0.0.1:%BACKEND_PORT%/api/v1/health" 200 %SMOKE_TIMEOUT_SECONDS%
if errorlevel 1 exit /b 1

call :wait_for_http_get_with_auth "Backend customers list" "http://127.0.0.1:%BACKEND_PORT%/api/v1/customers?page=1&size=1" 200 %SMOKE_TIMEOUT_SECONDS%
if errorlevel 1 exit /b 1

call :wait_for_openapi_path "Backend catalog API contract" "http://127.0.0.1:%BACKEND_PORT%/openapi.json" "/api/v1/offer-categories" %SMOKE_TIMEOUT_SECONDS%
if errorlevel 1 exit /b 1

call :wait_for_http_get "Frontend root" "http://127.0.0.1:%FRONTEND_PORT%" 200 %SMOKE_TIMEOUT_SECONDS%
if errorlevel 1 exit /b 1

echo [INFO] Launch sequence completed.
echo [INFO] Backend default URL:  http://localhost:%BACKEND_PORT%
echo [INFO] Frontend default URL: http://localhost:%FRONTEND_PORT%
exit /b 0

:stop_window_title
taskkill /F /T /FI "WINDOWTITLE eq %~1*" >nul 2>nul
exit /b 0

:stop_backend_runtime_processes
for /f "tokens=*" %%P in ('powershell -NoProfile -Command "$pids = Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*.exe' -and $_.CommandLine -like '*uvicorn*app.main:app*' } | Select-Object -ExpandProperty ProcessId -Unique; if ($pids) { $pids -join ' ' }"') do (
    for %%Q in (%%P) do (
        if not "%%Q"=="0" (
            taskkill /F /T /PID %%Q >nul 2>nul
        )
    )
)
exit /b 0

:is_port_listening
powershell -NoProfile -Command "$port=%~1; $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($conn) { exit 0 } else { exit 1 }" >nul 2>nul
exit /b %errorlevel%

:stop_port_listener
set "TARGET_PORT=%~1"
powershell -NoProfile -Command "$port=%TARGET_PORT%; for($i=0; $i -lt 8; $i++){ $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; if(-not $conns){ break }; $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; $kill = New-Object 'System.Collections.Generic.HashSet[int]'; foreach($pid in $pids){ if($pid -gt 0){ [void]$kill.Add([int]$pid); try { $proc = Get-CimInstance Win32_Process -Filter \"ProcessId=$pid\" -ErrorAction Stop; if($proc.ParentProcessId -gt 0){ [void]$kill.Add([int]$proc.ParentProcessId) } } catch {} } }; foreach($k in $kill){ Stop-Process -Id $k -Force -ErrorAction SilentlyContinue }; Start-Sleep -Milliseconds 500 }" >nul 2>nul
exit /b 0

:wait_for_http_get
powershell -NoProfile -Command "$name='%~1'; $url='%~2'; $expected=%~3; $timeout=%~4; $deadline=(Get-Date).AddSeconds($timeout); while((Get-Date) -lt $deadline){ try { $resp = Invoke-WebRequest -UseBasicParsing -Method Get -Uri $url -TimeoutSec 4; if([int]$resp.StatusCode -eq $expected){ Write-Host \"[INFO] $name smoke check passed ($([int]$resp.StatusCode)).\"; exit 0 } } catch { if ($_.Exception.Response) { $code=[int]$_.Exception.Response.StatusCode } else { $code=0 } }; Start-Sleep -Milliseconds 800 }; Write-Host \"[ERROR] $name smoke check failed (expected status $expected).\"; exit 1"
exit /b %errorlevel%

:wait_for_http_get_with_auth
powershell -NoProfile -Command "$name='%~1'; $url='%~2'; $expected=%~3; $timeout=%~4; $deadline=(Get-Date).AddSeconds($timeout); $headers=@{ Authorization='Bearer launch-smoke:admin,ops' }; while((Get-Date) -lt $deadline){ try { $resp = Invoke-WebRequest -UseBasicParsing -Method Get -Uri $url -Headers $headers -TimeoutSec 4; if([int]$resp.StatusCode -eq $expected){ Write-Host \"[INFO] $name smoke check passed ($([int]$resp.StatusCode)).\"; exit 0 } } catch { if ($_.Exception.Response) { $code=[int]$_.Exception.Response.StatusCode } else { $code=0 } }; Start-Sleep -Milliseconds 800 }; Write-Host \"[ERROR] $name smoke check failed (expected status $expected).\"; exit 1"
exit /b %errorlevel%

:wait_for_openapi_path
powershell -NoProfile -Command "$name='%~1'; $url='%~2'; $path='%~3'; $timeout=%~4; $deadline=(Get-Date).AddSeconds($timeout); while((Get-Date) -lt $deadline){ try { $resp = Invoke-RestMethod -Method Get -Uri $url -TimeoutSec 4; if ($resp.paths.PSObject.Properties.Name -contains $path){ Write-Host \"[INFO] $name smoke check passed (path found: $path).\"; exit 0 } } catch {}; Start-Sleep -Milliseconds 800 }; Write-Host \"[ERROR] $name smoke check failed (missing path: $path).\"; exit 1"
exit /b %errorlevel%
