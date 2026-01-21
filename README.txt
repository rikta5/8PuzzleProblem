AI Project (8-puzzle and 15-puzzle problem) - Tarik Bašić
================================

Directory Structure:
--------------------
src/
    core/       - Base classes (Node, Problem, Agent)
    domain/     - Puzzle specific logic
    algorithms/ - A*, IDA*, Heuristics
    ui/         - GUI and CLI code
    analysis/   - Experimentation and Plotting tools

How to Run:
-----------
Double-click the .bat files in this root directory:

- run_gui.bat: Starts the visual interface.
- run_cli.bat: Starts the command-line interface.
- run_experiments.bat: Runs the benchmark suite and generates plots in 'results/'.

Dependencies:
-------------
See requirements.txt.
Install via: pip install -r requirements.txt