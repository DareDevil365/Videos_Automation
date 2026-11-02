@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" run_pipeline.py --env-file .env batch-run --plan Resources\Plans\repo-upgrade-final.json
pause
