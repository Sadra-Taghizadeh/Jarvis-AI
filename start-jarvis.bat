@echo off
echo Starting Jarvis AI Assistant...
echo.

set JARVIS_ROOT=D:\GitHub\test\jarvis

echo [1/2] Starting Backend...
cd /d "%JARVIS_ROOT%\backend"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
    start "Jarvis Backend" python main.py
    echo      Backend started on ws://localhost:8765
) else (
    echo ERROR: Backend not found at %JARVIS_ROOT%\backend
    pause
    exit /b 1
)

echo [2/2] Starting Frontend...
cd /d "%JARVIS_ROOT%\frontend"
if exist "release\Jarvis AI Assistant-win32-x64\Jarvis AI Assistant.exe" (
    start "" "release\Jarvis AI Assistant-win32-x64\Jarvis AI Assistant.exe"
    echo      Frontend started
) else (
    echo ERROR: Frontend exe not found.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Jarvis AI Assistant is running!
echo   Ctrl+Shift+J = Focus Jarvis
echo   Ctrl+Shift+Q = Quit Jarvis
echo ========================================
echo.
echo Close this window - Jarvis runs in background.
