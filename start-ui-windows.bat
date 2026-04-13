@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python is not installed or not in PATH.
  echo Install it from: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\pip.exe" install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies.
  pause
  exit /b 1
)

echo Starting app at http://127.0.0.1:5000
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
  set "HTML2PDF_BROWSER=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) else if exist "%PROGRAMFILES%\Google\Chrome\Application\chrome.exe" (
  set "HTML2PDF_BROWSER=%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"
) else if exist "%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe" (
  set "HTML2PDF_BROWSER=%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe" (
  set "HTML2PDF_BROWSER=%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe" (
  set "HTML2PDF_BROWSER=%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe" (
  set "HTML2PDF_BROWSER=%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"
)
start "" "http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py

endlocal
