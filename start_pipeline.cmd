@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo The project Python environment is missing. Set up the project environment first.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "run_control.py"
