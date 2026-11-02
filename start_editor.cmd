@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run_editor.py serve --open
) else (
  python run_editor.py serve --open
)
if errorlevel 1 pause

