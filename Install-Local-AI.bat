@echo off
cd /d "%~dp0"
echo Installing CPU-based local AI. Keep internet connected during first setup.
echo This downloads Python packages and pretrained models and may take several minutes.
if not exist ".venv\Scripts\python.exe" (
    py -m venv .venv
    if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements-local.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -c "from local_ai import download_models; download_models(print)"
if errorlevel 1 goto failed
echo.
echo Local AI is ready. Open Start-Game-Day.bat and select Local AI in Match setup.
pause
exit /b 0
:failed
echo.
echo Installation failed. Share the error text so we can fix it.
pause
