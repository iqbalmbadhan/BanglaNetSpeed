@echo off
cd /d "%~dp0"
set "PY="
if exist ".venv\Scripts\pythonw.exe" set "PY=.venv\Scripts\pythonw.exe"
if not defined PY if exist ".venv-build\Scripts\pythonw.exe" set "PY=.venv-build\Scripts\pythonw.exe"

if not defined PY (
  echo Dependencies are not installed yet. Run install_and_run.bat first.
  pause
  exit /b 1
)
start "" "%PY%" src\widget.py
