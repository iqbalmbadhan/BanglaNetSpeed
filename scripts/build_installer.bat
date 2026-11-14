@echo off
setlocal
cd /d "%~dp0\.."

echo ========================================================
echo  Bangla Net Speed Meter - Setup Installer Builder
echo ========================================================
echo.

if not exist "dist\BanglaNetSpeed.exe" (
  echo [1/3] Building BanglaNetSpeed.exe first...
  call scripts\build_release.bat
  if errorlevel 1 (
    echo Error: Failed to build EXE.
    exit /b 1
  )
) else (
  echo [1/3] Found existing dist\BanglaNetSpeed.exe
)

echo [2/3] Checking for Inno Setup 6 compiler (ISCC.exe)...
set "ISCC="

where iscc.exe >nul 2>&1
if not errorlevel 1 set "ISCC=iscc.exe"

if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
  set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
  set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
  set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if not defined ISCC (
  echo.
  echo Inno Setup 6 compiler was not found on your computer.
  echo To build the classic installer locally, install Inno Setup 6:
  echo   1. Download from: https://jrsoftware.org/isdl.php
  echo      or run: winget install JRSoftware.InnoSetup
  echo   2. Re-run this script: scripts\build_installer.bat
  echo.
  echo Note: GitHub Actions will also build this installer automatically on tag push.
  exit /b 1
)

echo Compiling installer with: "%ISCC%"
"%ISCC%" installer\installer.iss
if errorlevel 1 (
  echo Error: Inno Setup compilation failed.
  exit /b 1
)

echo [3/3] Generating SHA256 checksum for installer...
powershell -NoProfile -Command "$h=(Get-FileHash '.\dist\BanglaNetSpeed-Setup.exe' -Algorithm SHA256).Hash.ToLower(); Set-Content -Encoding ASCII '.\dist\BanglaNetSpeed-Setup.exe.sha256.txt' ($h+'  BanglaNetSpeed-Setup.exe')"

echo.
echo ========================================================
echo  Installer created successfully!
echo    dist\BanglaNetSpeed-Setup.exe
echo    dist\BanglaNetSpeed-Setup.exe.sha256.txt
echo ========================================================
exit /b 0
