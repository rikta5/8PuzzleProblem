@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo Starting Sliding Puzzle GUI...
python -m src.ui.gui
pause
