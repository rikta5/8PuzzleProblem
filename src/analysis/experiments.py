from __future__ import annotations
import csv
from pathlib import Path
from typing import List
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
from src.core import SearchAgent, SearchResult


def build_algorithm(name: str, problem: SlidingPuzzleProblem):
    h_misplaced = misplaced_tiles_heuristic(problem.goal_state)
    h_manhattan = manhattan_distance_heuristic(problem.goal_state, problem.size)
    h_linear = linear_conflict_heuristic(problem.goal_state, problem.size)

    if name == "astar_misplaced":
        return AStarSearch(heuristic=h_misplaced)
    if name == "astar_manhattan":
        return AStarSearch(heuristic=h_manhattan)
    if name == "astar_weighted":
        return AStarSearch(heuristic=h_manhattan, weight=1.5)
    if name == "astar_linear":
        return AStarSearch(heuristic=h_linear)
    if name == "greedy_manhattan":
        return GreedyBestFirstSearch(heuristic=h_manhattan)
    if name == "hill_climbing_manhattan":
        return HillClimbingSearch(heuristic=h_manhattan, max_steps=2000)
    if name == "sa_manhattan":
        return SimulatedAnnealingSearch(
            heuristic=h_manhattan,
            T0=10.0,
            alpha=0.99,
            max_steps=5000,
        )
    if name == "idastar_manhattan":
        return IDAStarSearch(heuristic=h_manhattan)
    if name == "idastar_linear":
        return IDAStarSearch(heuristic=h_linear)
    if name == "genetic_manhattan":
        return GeneticAlgorithmSearch(
            heuristic=h_manhattan,
            population_size=50,
            mutation_rate=0.1,
            max_generations=100,
            chromosome_length=30
        )

    raise ValueError(f"Unknown algorithm: {name}")


def run_single_experiment(
    size: int,
    scramble_depth: int,
    seed: int,
    algo_name: str,
) -> SearchResult:
    problem = SlidingPuzzleProblem.scrambled(size=size, scramble_depth=scramble_depth, seed=seed)
    algo = build_algorithm(algo_name, problem)
    agent = SearchAgent(problem, algo)
    result = agent.solve()
    return result


def run_batch_and_write_csv(
    algo_names: List[str],
    size: int,
    scramble_depth: int,
    runs: int,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "algorithm",
                "size",
                "scramble_depth",
                "seed",
                "success",
                "solution_cost",
                "nodes_expanded",
                "runtime",
                "iterations",
            ]
        )

        for algo in algo_names:
            for seed in range(runs):
                result = run_single_experiment(size, scramble_depth, seed, algo)
                writer.writerow(
                    [
                        algo,
                        size,
                        scramble_depth,
                        seed,
                        int(result.success),
                        result.solution_cost,
                        result.nodes_expanded,
                        result.runtime,
                        result.iterations,
                    ]
                )


def main() -> None:
    algo_names = [
        "astar_misplaced",
        "astar_manhattan",
        "astar_linear",
        "idastar_manhattan",
        "idastar_linear",
        "greedy_manhattan",
        "hill_climbing_manhattan",
        "sa_manhattan",
        "genetic_manhattan",
    ]
    runs = 20

    print("Running 3x3 Experiments...")
    output_3x3 = Path("results") / "puzzle_experiments_size3_depth20.csv"
    run_batch_and_write_csv(algo_names, 3, 20, runs, output_3x3)
    print(f"Finished 3x3. Results written to {output_3x3}")

    print("Running 4x4 Experiments...")
    algo_names_4x4 = [
        "astar_manhattan",
        "astar_linear",
        "idastar_manhattan",
        "idastar_linear",
        "greedy_manhattan",
        "hill_climbing_manhattan",
    ]
    output_4x4 = Path("results") / "puzzle_experiments_size4_depth40.csv"
    run_batch_and_write_csv(algo_names_4x4, 4, 40, runs, output_4x4)
    print(f"Finished 4x4. Results written to {output_4x4}")


if __name__ == "__main__":
    main()
