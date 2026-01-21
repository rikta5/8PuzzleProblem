# Project Architecture and File Structure Analysis

This document provides a detailed breakdown of the project's file structure, the purpose of each component, and how they interact to form the complete AI search framework. This information is intended to support the "System Architecture" and "Implementation" sections of your academic report.

## 1. Core Abstractions

These files define the fundamental building blocks of the search system, following standard AI textbook definitions (e.g., Russell & Norvig).

### `src/core/problem.py`

- **Purpose**: Defines the abstract base class `Problem`.
- **Key Components**:
  - `initial_state()`: Returns the starting state.
  - `actions(state)`: Returns valid moves from a given state.
  - `result(state, action)`: Returns the new state after an action.
  - `is_goal(state)`: Checks if the goal has been reached.
  - `step_cost(...)`: Calculates the cost of a move (default is 1).
- **Usage**: This is a template. It allows the search algorithms to work on _any_ problem (puzzle, route finding, etc.) without knowing the specific details, as long as the problem implements these methods.

### `src/core/node.py`

- **Purpose**: Represents a node in the search tree.
- **Key Components**:
  - `state`: The snapshot of the world at this node.
  - `parent`: A reference to the previous node (essential for reconstructing the path).
  - `action`: The move taken to get here.
  - `path_cost`: The total cost ($g(n)$) from the start to this node.
  - `expand(problem)`: A helper method that generates all child nodes.
- **Optimization**: Uses `__slots__` to reduce memory overhead per node by ~40%. This is critical for solving large instances (like the 15-puzzle) where A\* can store millions of nodes.
- **Usage**: Search algorithms manage collections of `Node` objects (e.g., the "frontier" or "open set") rather than raw states.

## 2. Domain Implementation

These files apply the core abstractions to the specific problem of the Sliding Tile Puzzle.

### `src/domain/puzzle_problem.py`

- **Purpose**: The concrete implementation of the Sliding Tile Puzzle (8-puzzle, 15-puzzle).
- **Inheritance**: Inherits from `Problem`.
- **Key Logic**:
  - **State Representation**: A flat tuple, e.g., `(1, 2, 3, 4, 5, 6, 7, 8, 0)`. This is immutable and hashable, making it efficient for storage in sets.
  - **Actions**: Logic to determine if "UP", "DOWN", "LEFT", or "RIGHT" are valid based on the blank tile's position.
  - **Transitions**: Logic to swap the blank tile with a neighbor.
  - **Scrambling**: A utility to generate solvable random puzzles by walking backwards from the goal.

### `src/algorithms/heuristics.py`

- **Purpose**: Contains heuristic functions ($h(n)$) that estimate the distance to the goal.
- **Implemented Heuristics**:
  - `misplaced_tiles_heuristic`: Counts tiles in the wrong spot. (Admissible but weak).
  - `manhattan_distance_heuristic`: Sums the vertical and horizontal distances of each tile to its target. (Admissible and much stronger).
  - **`linear_conflict_heuristic`**: Adds a penalty for tiles that are in the correct row/column but in the wrong order. This dominates Manhattan distance.
- **Usage**: These functions are passed to informed search algorithms (A*, Greedy, IDA*) to guide the search.

## 3. Search Algorithms

### `src/algorithms/search_algorithms.py`

- **Purpose**: Implements the actual search strategies.
- **Algorithms**:
  - **`AStarSearch`**: The gold standard. Uses $f(n) = g(n) + w \cdot h(n)$. Includes infinite parameter $w$ (weight) to trade optimality for speed.
  - **`GreedyBestFirstSearch`**: Uses $f(n) = h(n)$. Fast but not optimal.
  - **`HillClimbingSearch`**: A local search that only looks at immediate neighbors. Fast but gets stuck in local optima.
  - **`SimulatedAnnealingSearch`**: A probabilistic local search that can escape local optima by accepting worse moves occasionally.
  - **`IDAStarSearch`**: Iterative Deepening A*. Uses recursion and a cost threshold. Memory-efficient ($O(d)$) compared to A*.
  - **`GeneticAlgorithmSearch`**: An evolutionary approach that evolves a population of action sequences.
- **Usage**: Each class implements a `search(problem)` method that returns a `SearchResult`.

## 4. Execution & Management

### `src/core/agent.py`

- **Purpose**: A wrapper class `SearchAgent`.
- **Role**: It binds a specific `Problem` instance with a specific `SearchAlgorithm`.
- **Usage**: It simplifies the calling code: `agent = SearchAgent(problem, algo); result = agent.solve()`.

### `src/core/results.py`

- **Purpose**: Defines the `SearchResult` data class.
- **Data Stored**:
  - `solution_node`: The final node (if found).
  - `success`: Boolean flag.
  - `nodes_expanded`: The efficiency metric.
  - `runtime`: Time taken.
  - `solution_path`: A property that backtracks from the solution node to the root to return the full list of moves.

## 5. User Interfaces & Experiments

### `src/ui/cli.py`

- **Purpose**: The Command Line Interface.
- **Features**:
  - Interactive menu for selecting puzzle size, algorithm, and difficulty.
  - Prints the initial state, search metrics, and the step-by-step solution.
- **Usage**: The primary tool for manual testing and demonstration.

### `src/ui/gui.py`

- **Purpose**: The Graphical User Interface (Tkinter).
- **Features**:
  - **Modern Flat UI**: styled using `ttk.Style`, custom colors (Emerald Green/Slate Blue), and improved layouts for a professional look.
  - **Manual Mode**: Fully interactive gameplay. Users can click tiles to move them, with valid move detection and "You Won" state tracking.
  - **Hybrid Solving**: The "AI Solve" function seamlessly picks up from the user's current manual state to finish the puzzle.
  - **Visualizations**: Animates the AI's solution path step-by-step.
  - **Interactive Help**: Built-in instructions for game rules and algorithm comparisons.
- **Usage**: For visual demonstration, manual play, and verifying logic interactively.

### `src/analysis/experiments.py`

- **Purpose**: The batch testing engine.
- **Logic**:
  - Runs every algorithm multiple times (e.g., 20 runs) on different random seeds.
  - Tests both 3x3 (8-puzzle) and 4x4 (15-puzzle).
  - Collects raw data (time, nodes, success rate).
- **Output**: Writes CSV files to the `results/` folder.

### `src/analysis/plotting.py`

- **Purpose**: Data visualization.
- **Logic**: Reads the CSV files generated by `experiments.py` and uses `matplotlib` to create graphs.
- **Output**: Generates images (bar charts, box plots) in `results/plots/` for use in the report.

## 6. Data & Output Files

### CSV Files (`results/*.csv`)

These files contain the raw data from the batch experiments. Each row represents a single run of an algorithm on a specific puzzle.

- **`algorithm`**: The name of the search strategy used (e.g., `astar_manhattan`).
- **`size`**: The dimension of the puzzle (e.g., `3` for 8-puzzle, `4` for 15-puzzle).
- **`scramble_depth`**: The difficulty level (number of random moves from the goal).
- **`seed`**: The random seed used. This ensures that every algorithm solves the **exact same** set of puzzles for a fair comparison.
- **`success`**: `1` if the algorithm found a solution, `0` if it failed or timed out.
- **`solution_cost`**: The number of moves in the solution path found.
- **`nodes_expanded`**: The total number of nodes visited. This is the primary metric for **efficiency** (memory and computational work).
- **`runtime`**: The wall-clock time taken to solve the puzzle (in seconds).
- **`iterations`**: Used for local search algorithms (like Hill Climbing) to track how many main loop cycles were performed.

## 7. Configuration & Scripts

To make the project easy to run and manage, several helper files are included:

- **`requirements.txt`**: Lists the external Python libraries required (`pandas`, `matplotlib`, `tkinter` is usually built-in).
- **`run_gui.bat`**: A Windows batch script to launch the GUI with a single double-click.
- **`run_cli.bat`**: A Windows batch script to launch the command-line interface.
- **`run_experiments.bat`**: A Windows batch script that runs the full suite of experiments and then automatically generates the plots.

### Plots (`results/plots/*.png`)

Generated by `plotting.py` to visualize the CSV data.

- **`success_rate.png`**: A bar chart showing the percentage of puzzles successfully solved by each algorithm.
- **`runtime_boxplot.png`**: A box plot showing the distribution of time taken. Useful for seeing the median speed and outliers.
- **`nodes_expanded_boxplot.png`**: A box plot (often on a log scale) showing how much work each algorithm did. This usually shows the massive advantage of A\* over uninformed search.
- **`solution_cost_boxplot.png`**: Compares the quality of solutions. A\* will always be at the bottom (optimal), while Greedy or Hill Climbing might be higher (suboptimal).

## 8. Data Flow Summary

1.  **User** starts `cli.py` or `gui.py`.
2.  **System** creates a `SlidingPuzzleProblem` (using `puzzle_problem.py`).
3.  **System** selects a heuristic (from `heuristics.py`) and an algorithm (from `search_algorithms.py`).
4.  **Agent** (`agent.py`) runs the algorithm on the problem.
5.  **Algorithm** explores the state space by creating `Node` objects (`node.py`).
6.  **Result** (`results.py`) is returned containing the path and stats.
7.  **Interface** displays the result to the user.

## 9. Experimental Methodology & Design Decisions

This section directly addresses the key questions required for your report's "Methodology" and "Results" chapters.

### Q1: What is the puzzle size you focused on most?

**Answer:**
The experiments were conducted in two distinct phases to demonstrate different aspects of search complexity:

1.  **Primary Focus: 8-Puzzle (3x3)**

    - **Reason**: The state space is small enough (~181,000 states) to allow **all** algorithms, including weaker ones like Hill Climbing and A\* with Misplaced Tiles, to be compared fairly.
    - **Usage**: Used for the majority of the statistical analysis (success rates, runtime comparisons).

2.  **Secondary Focus: 15-Puzzle (4x4)**
    - **Reason**: The state space is massive (~10 trillion states). This was used to "stress test" the system and demonstrate why advanced algorithms (IDA\*) and strong heuristics (Manhattan) are necessary for real-world problems.
    - **Outcome**: Weaker algorithms (A\* Misplaced, Hill Climbing) typically fail or timeout here, highlighting the scalability limits.

### Q2: Which search algorithms did you compare?

**Answer:**
The project implements and compares a diverse set of algorithms. Note that the set of algorithms tested differs between the 3x3 and 4x4 experiments due to complexity constraints.

**1. Algorithms Tested on 8-Puzzle (3x3):**

- **A\* (Manhattan)**: To show the improvement of a strong heuristic.
- **A\* (Linear Conflict)**: To show the impact of an advanced heuristic.
- **Greedy Best-First**: To demonstrate speed vs. optimality trade-offs.
- **Hill Climbing**: To demonstrate local search limitations (getting stuck).
- **Simulated Annealing**: To show probabilistic escape from local optima.
- **IDA\***: To compare memory usage with A\*.
- **Genetic Algorithm**: To test evolutionary approaches.

**2. Algorithms Tested on 15-Puzzle (4x4):**

- **A\* (Manhattan)**: The standard benchmark.
- **A\* (Linear Conflict)**: Shows significant pruning power on large state spaces.
- **A\* (Weighted 1.5)**: Trade-off for speed on hard puzzles.
- **IDA\* (Linear Conflict)**: Ideally suited for 15-puzzle
- **IDA\* (Manhattan)**: The only algorithm capable of solving hard 4x4 instances reliably without running out of memory.
- **Greedy Best-First**: Included to see if it can find _any_ solution quickly, even if very long.
- **Hill Climbing**: Included as a baseline for failure (it almost always fails on 4x4).

_Note: Weaker algorithms like A_ (Misplaced) and Genetic Algorithm were excluded from 4x4 experiments because they are too slow or memory-intensive for the massive state space.\*

### Q3: Did you run experiments using both heuristics?

**Answer:**
Yes, the framework implements multiple heuristics to demonstrate the concept of "heuristic dominance":

1.  **Misplaced Tiles ($h_1$)**:

    - **Definition**: Count of tiles not in their goal position.
    - **Performance**: Weak. It guides the search poorly, leading to many more node expansions. Used primarily with A\* on the 3x3 puzzle to show baseline performance.

2.  **Manhattan Distance ($h_2$)**:

    - **Definition**: Sum of the vertical and horizontal distances of each tile from its goal.
    - **Performance**: Strong. It is much closer to the true cost, allowing A* and IDA* to prune the search tree aggressively.
    - **Result**: Experiments show $h_2$ expands orders of magnitude fewer nodes than $h_1$.

3.  **Linear Conflict ($h_3$)**:
    - **Definition**: Manhattan Distance + penalty for conflicting tiles in the same row/column.
    - **Performance**: Very Strong. It catches cases where Manhattan underestimates the cost because tiles must move around each other.
    - **Result**: Vital for 15-puzzle efficiency.

### Q4: What plots or metrics are emphasized?

**Answer:**
The `plotting.py` script generates four key visualizations to analyze performance from different angles:

1.  **Success Rate (Robustness)**:

    - _Question_: "Does it find a solution?"
    - _Insight_: A* and IDA* are 100% successful. Local search (Hill Climbing) often fails (0-50% success) depending on the scramble depth.

2.  **Nodes Expanded (Efficiency)**:

    - _Question_: "How much work did it do?"
    - _Insight_: This is the most critical academic metric. It proves that Manhattan Distance is better than Misplaced Tiles, and that Greedy search is "lazier" (expands fewer nodes) than A\* but at a cost.

3.  **Runtime (Speed)**:

    - _Question_: "How long did it take?"
    - _Insight_: Greedy is often the fastest. A* is slower due to memory management. IDA* is fast for hard problems but can be slow for easy ones due to re-visiting nodes.

4.  **Solution Cost (Optimality)**:
    - _Question_: "Is the solution the shortest possible?"
    - _Insight_: A* and IDA* always have the lowest cost (optimal). Greedy and Genetic Algorithms produce much longer paths (suboptimal).
