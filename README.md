# AI Project - Sliding Tile Puzzle Solver

This project implements a comprehensive framework for solving Sliding Tile Puzzles (8-puzzle and 15-puzzle) using various Artificial Intelligence search algorithms. It provides a modular architecture allowing for easy comparison of different search strategies, heuristics, and performance metrics.

## Features

- **Puzzle Support**: Solves both 8-puzzle (3x3) and 15-puzzle (4x4) configurations.
- **Search Algorithms**:
  - **A\* Search**: Optimal pathfinding using $f(n) = g(n) + w \cdot h(n)$. Supports weighted A\* for trading optimality for speed.
  - **IDA* (Iterative Deepening A*)**: Memory-efficient optimal search suitable for larger state spaces like the 15-puzzle.
  - **Greedy Best-First Search**: Prioritizes speed over optimality.
  - **Local Search**: Hill Climbing and Simulated Annealing.
  - **Evolutionary**: Genetic Algorithm approach.
- **Heuristics**:
  - **Manhattan Distance**: Admissible heuristic summing vertical and horizontal distances.
  - **Linear Conflict**: An improvement over Manhattan distance that accounts for tile conflicts within rows/cols.
  - **Misplaced Tiles**: Basic admissible heuristic.
- **Interfaces**:
  - **GUI**: Interactive visualization using Tkinter.
  - **CLI**: Robust command-line interface for experimentation.
- **Analysis**: Tools for running batch experiments and generating performance plots.

## Project Structure

The project is organized into a modular architecture to separate core abstractions, domain logic, and algorithmic implementations.

### 1. Core Abstractions (`src/core/`)

These files define the fundamental building blocks of the search system.

- **`problem.py`**: Defines the abstract base class `Problem`. It outlines the interface for any search problem (initial state, successor generation, goal testing), allowing algorithms to remain problem-agnostic.
- **`node.py`**: Represents a node in the search tree. Optimized with `__slots__` to reduce memory overhead during large-scale searches. It tracks the state, parent path, action, and path cost.
- **`agent.py`**: Implements the `SearchAgent`, a wrapper that binds a specific problem instance with a search algorithm to execute the solving process.
- **`results.py`**: Defines the `SearchResult` data class, standardizing the output metrics (success, nodes expanded, runtime, path cost) across all algorithms.

### 2. Domain Implementation (`src/domain/`)

- **`puzzle_problem.py`**: The concrete implementation of the Sliding Tile Puzzle. It handles state representation (using immutable tuples for hash ability), valid move generation, and transition logic.

### 3. Algorithms (`src/algorithms/`)

- **`search_algorithms.py`**: Contains the implementation of all search strategies (A*, IDA*, BFS, Hill Climbing, Simulated Annealing, Genetic Algorithm).
- **`heuristics.py`**: Implements heuristic functions ($h(n)$) used by informed search algorithms. Includes Manhattan Distance, Linear Conflict, and Misplaced Tiles.

### 4. Interfaces & Tools

- **`src/ui/`**: Contains the user interfaces.
  - `gui.py`: Graphical User Interface for visual demonstration.
  - `cli.py`: Command Line Interface for quick testing.
- **`src/analysis/`**: Tools for scientific evaluation.
  - `experiments.py`: Runs benchmarks across multiple puzzle instances.
  - `plotting.py`: Generates charts to compare algorithm performance.

## Setup & Installation

1. **Prerequisites**: Ensure you have Python 3.8+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The project includes batch scripts for easy execution. Run these from the project root.

### Graphical User Interface

Launch the visual solver:

```bash
./run_gui.bat
```

_(Or `python src/ui/gui.py` on non-Windows systems)_

### Command Line Interface

Launch the interactive text-based solver:

```bash
./run_cli.bat
```

### Running Experiments

To run the benchmark suite and generate analysis plots (stored in `results/`):

```bash
./run_experiments.bat
```
