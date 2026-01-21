from __future__ import annotations
import argparse
import sys
from src.domain import SlidingPuzzleProblem
from src.algorithms import (
    misplaced_tiles_heuristic,
    manhattan_distance_heuristic,
    linear_conflict_heuristic,
    AStarSearch,
    GreedyBestFirstSearch,
    HillClimbingSearch,
    SimulatedAnnealingSearch,
    IDAStarSearch,
    GeneticAlgorithmSearch,
)
from src.core import SearchAgent


def get_interactive_input():
    print("\n=== Sliding Tile Puzzle AI CLI ===")
    print("Interactive Mode\n")

    while True:
        try:
            val = input("Enter puzzle size (e.g. 3 for 8-puzzle, 4 for 15-puzzle) [3]: ").strip()
            if not val:
                size = 3
            else:
                size = int(val)
            if size < 2:
                print("Size must be >= 2")
                continue
            break
        except ValueError:
            print("Invalid integer.")

    while True:
        try:
            val = input("Enter scramble depth (difficulty) [20]: ").strip()
            if not val:
                depth = 20
            else:
                depth = int(val)
            if depth < 0:
                print("Depth must be >= 0")
                continue
            break
        except ValueError:
            print("Invalid integer.")

    algorithms = [
        ("A* (Manhattan + Linear Conflict)", "astar_linear"),
        ("A* (Manhattan)", "astar_manhattan"),
        ("A* (Weighted 1.5)", "astar_weighted"),
        ("A* (Misplaced Tiles)", "astar_misplaced"),
        ("IDA* (Manhattan + Linear Conflict)", "idastar_linear"),
        ("IDA* (Manhattan)", "idastar_manhattan"),
        ("Greedy Best-First (Manhattan)", "greedy_manhattan"),
        ("Hill Climbing (Manhattan)", "hill_climbing_manhattan"),
        ("Simulated Annealing (Manhattan)", "sa_manhattan"),
        ("Genetic Algorithm (Manhattan)", "genetic_manhattan"),
    ]
    
    print("\nAvailable Algorithms:")
    for i, (name, key) in enumerate(algorithms, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            val = input(f"Select algorithm (1-{len(algorithms)}) [1]: ").strip()
            if not val:
                algo_name = algorithms[0][1]
            else:
                idx = int(val) - 1
                if 0 <= idx < len(algorithms):
                    algo_name = algorithms[idx][1]
                else:
                    print("Invalid selection.")
                    continue
            break
        except ValueError:
            print("Invalid input.")

    seed = None
    val = input("Enter random seed (optional, press Enter for random): ").strip()
    if val:
        try:
            seed = int(val)
        except ValueError:
            print("Invalid seed, using random.")
            
    return size, depth, algo_name, seed


def run_search(size, scramble_depth, algo_name, seed):
    problem = SlidingPuzzleProblem.scrambled(size=size, scramble_depth=scramble_depth, seed=seed)

    print("\nInitial state:")
    print(problem.display_state(problem.initial_state()))
    print()

    h_misplaced = misplaced_tiles_heuristic(problem.goal_state)
    h_manhattan = manhattan_distance_heuristic(problem.goal_state, problem.size)
    h_linear = linear_conflict_heuristic(problem.goal_state, problem.size)

    if algo_name == "astar_misplaced":
        algo = AStarSearch(heuristic=h_misplaced)
    elif algo_name == "astar_manhattan":
        algo = AStarSearch(heuristic=h_manhattan)
    elif algo_name == "astar_weighted":
        algo = AStarSearch(heuristic=h_manhattan, weight=1.5)
    elif algo_name == "astar_linear":
        algo = AStarSearch(heuristic=h_linear)
    elif algo_name == "greedy_manhattan":
        algo = GreedyBestFirstSearch(heuristic=h_manhattan)
    elif algo_name == "hill_climbing_manhattan":
        algo = HillClimbingSearch(heuristic=h_manhattan, max_steps=2000)
    elif algo_name == "sa_manhattan":
        algo = SimulatedAnnealingSearch(
            heuristic=h_manhattan,
            T0=10.0,
            alpha=0.99,
            max_steps=5000,
        )
    elif algo_name == "idastar_manhattan":
        algo = IDAStarSearch(heuristic=h_manhattan)
    elif algo_name == "idastar_linear":
        algo = IDAStarSearch(heuristic=h_linear)
    elif algo_name == "genetic_manhattan":
        algo = GeneticAlgorithmSearch(
            heuristic=h_manhattan,
            population_size=50,
            mutation_rate=0.1,
            max_generations=100,
            chromosome_length=30
        )
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    print(f"Running {algo_name} on {size}x{size} puzzle (depth {scramble_depth})...")
    agent = SearchAgent(problem, algo)
    result = agent.solve()

    print("-" * 40)
    print(f"Success: {result.success}")
    print(f"Nodes expanded: {result.nodes_expanded}")
    print(f"Runtime: {result.runtime:.4f} s")
    if result.iterations:
        print(f"Iterations: {result.iterations}")
    if result.success:
        path = result.solution_path
        print(f"Solution depth: {len(path) - 1}")
        
        print("\nSolution Steps:")
        for i, node in enumerate(path):
            if i == 0:
                print(f"Step 0 (Start):")
            else:
                print(f"Step {i} (Action: {node.action}):")
            print(problem.display_state(node.state))
            print()
    else:
        print("No solution found.")
    print("-" * 40)


def main() -> None:
    """
    Command line interface to run the search agent.
    
    If arguments are provided, it runs in non-interactive mode.
    If no arguments are provided, it launches an interactive menu.
    """
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Sliding Puzzle Search Agent")
        parser.add_argument("--size", type=int, default=3, help="Puzzle size N (N x N)")
        parser.add_argument("--scramble-depth", type=int, default=20, help="Scramble depth")
        parser.add_argument(
            "--algorithm",
            type=str,
            default="astar_manhattan",
            choices=[
                "astar_misplaced",
                "astar_manhattan",
                "astar_linear",
                "astar_weighted",
                "idastar_manhattan",
                "idastar_linear",
                "greedy_manhattan",
                "hill_climbing_manhattan",
                "sa_manhattan",
                "genetic_manhattan",
            ],
            help="Algorithm to run",
        )
        parser.add_argument("--seed", type=int, default=None, help="Random seed")
        args = parser.parse_args()
        
        run_search(args.size, args.scramble_depth, args.algorithm, args.seed)
    else:
        size, depth, algo, seed = get_interactive_input()
        run_search(size, depth, algo, seed)


if __name__ == "__main__":
    main()
