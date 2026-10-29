@echo off
setlocal
cd /d "%~dp0"
if not exist "app.py" goto missing
set "LAMATNA_PY="
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import sys,struct; assert sys.version_info >= (3,11) and struct.calcsize('P') == 8" >nul 2>&1
    if not errorlevel 1 set "LAMATNA_PY=%~dp0.venv\Scripts\python.exe"
)
if defined LAMATNA_PY goto found
for %%V in (3.13 3.12 3.11) do (
    if not defined LAMATNA_PY for /f "delims=" %%P in ('py -%%V -c "import sys,struct; assert struct.calcsize('P') == 8; print(sys.executable)" 2^>nul') do set "LAMATNA_PY=%%P"
)
if defined LAMATNA_PY goto found
for /f "delims=" %%P in ('python -c "import sys,struct; assert sys.version_info >= (3,11) and struct.calcsize('P') == 8; print(sys.executable)" 2^>nul') do set "LAMATNA_PY=%%P"
if not defined LAMATNA_PY goto no_python
:found
for %%P in ("%LAMATNA_PY%") do set "LAMATNA_PYW=%%~dpPpythonw.exe"
if exist "%LAMATNA_PYW%" (
    start "" "%LAMATNA_PYW%" "%~dp0launcher.py"
    exit /b 0
)
"%LAMATNA_PY%" "%~dp0launcher.py"
if errorlevel 1 pause
exit /b
:missing
echo Please extract the ZIP first, then open Lamatna from the folder containing app.py.
pause
exit /b 1
:no_python
echo Lamatna needs Python 3.11, 3.12 or 3.13, 64-bit.
echo Install Python from python.org with the Python launcher, then double-click Lamatna again.
pause
exit /b 1
