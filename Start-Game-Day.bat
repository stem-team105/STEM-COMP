@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -m venv .venv
    if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Installing the desktop interface. This only happens once...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto failed
)
.venv\Scripts\python.exe studio.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Setup or startup failed. Keep this window open and share the error text.
pause
