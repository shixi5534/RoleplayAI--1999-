@echo off
setlocal
title Roleplay AI Launcher
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "PY=%ROOT%.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
set "PORT=8000"
set "PYTHONPATH=%ROOT%src"

echo ============================================
echo   Roleplay AI Launcher
echo ============================================
echo.

if not exist "%ROOT%logs" mkdir "%ROOT%logs"

netstat -aon | findstr ":11434" | findstr "LISTEN" >nul
if errorlevel 1 (
    echo [WARN] Ollama not detected on port 11434. Chat may not work.
    echo        Start Ollama first, then rerun this launcher.
) else (
    echo [OK]   Ollama service running
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTEN"') do (
    echo [INFO] Port 8000 held by PID %%a, releasing...
    taskkill /f /pid %%a >nul 2>&1
)

echo [START] Booting Roleplay AI...
start "RoleplayAI" /min cmd /c ""%PY%" -m uvicorn roleplay.main:app --host 127.0.0.1 --port %PORT% --log-level info >>"%ROOT%logs\server.log" 2>&1"

set "READY="
for /l %%i in (1,1,30) do (
    ping -n 2 127.0.0.1 >nul
    netstat -aon | findstr ":8000" | findstr "LISTEN" >nul
    if not errorlevel 1 (
        set "READY=1"
        goto ready
    )
)
:ready
if defined READY (
    echo [OK]   Server ready, opening browser...
    start "" "http://localhost:%PORT%/"
) else (
    echo [ERROR] Startup timeout, see log: %ROOT%logs\server.log
)

echo.
echo URL:  http://localhost:%PORT%/
echo LOG:  %ROOT%logs\server.log
echo.
echo Press any key to stop the server...
pause >nul

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTEN"') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo [OK]   Server stopped
endlocal
