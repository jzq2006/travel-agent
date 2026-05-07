@echo off
chcp 65001 >nul 2>&1
title AI Travel Agent

echo.
echo  ================================
echo   AI 出行规划 Agent - 一键启动
echo  ================================
echo.

:: Check Python
where python >nul 2>&1 || (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

:: Check Node
where node >nul 2>&1 || (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

:: ---- Backend ----
echo [1/4] Installing backend dependencies...
cd /d "%~dp0backend"
pip install uv >nul 2>&1
uv sync --quiet 2>nul || pip install -r requirements.txt 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo [2/4] Starting backend server (port 8000)...
start "Backend Server" cmd /c "uv run python main.py"
timeout /t 3 /nobreak >nul

:: ---- Frontend ----
echo [3/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent 2>nul

echo [4/4] Starting frontend dev server (port 5173)...
start "Frontend Server" cmd /c "npx vite --open"

echo.
echo  ================================
echo   All servers started!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo  ================================
echo.
echo  Close the terminal windows to stop.
pause
