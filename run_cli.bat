@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo Starting Sliding Puzzle CLI...
python -m src.ui.cli
pause
