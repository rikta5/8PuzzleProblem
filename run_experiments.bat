@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo Running AI Puzzle Solver Experiments...
echo This may take a while depending on the number of runs and algorithms.
echo.

python -m src.analysis.experiments

echo.
echo Experiments finished. Generating plots...
python -m src.analysis.plotting

echo.
echo Done! Check the 'results' folder for CSV files and 'results/plots' for graphs.
pause
