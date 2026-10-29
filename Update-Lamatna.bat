@echo off
cd /d "%~dp0"
echo Close Lamatna before updating. Installed packages, models and saved games will be kept.
echo Downloading the latest application files...
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $rallyTemp=Join-Path ([IO.Path]::GetTempPath()) ('lamatna-update-'+[guid]::NewGuid().ToString()); New-Item -ItemType Directory -Path $rallyTemp | Out-Null; try { $zip=Join-Path $rallyTemp 'source.zip'; Invoke-WebRequest -Uri 'https://github.com/stem-team105/STEM-COMP/archive/refs/heads/main.zip' -OutFile $zip; Expand-Archive -LiteralPath $zip -DestinationPath $rallyTemp; Get-ChildItem -LiteralPath (Join-Path $rallyTemp 'STEM-COMP-main') -Force | Copy-Item -Destination (Get-Location).Path -Recurse -Force; Write-Host 'Update complete. Open Start-Game-Day.bat.' } finally { Remove-Item -LiteralPath $rallyTemp -Recurse -Force -ErrorAction SilentlyContinue }"
if errorlevel 1 echo Update failed. Keep this window open and share the error.
pause
