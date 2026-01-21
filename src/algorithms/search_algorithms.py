from __future__ import annotations
import heapq
import math
import random
import time
from abc import ABC, abstractmethod
from typing import Any, List, Tuple
from src.core import Problem, Node, SearchResult
from src.algorithms.heuristics import Heuristic


class SearchAlgorithm(ABC):
    @abstractmethod
    def search(self, problem: Problem) -> SearchResult:
        raise NotImplementedError


class AStarSearch(SearchAlgorithm):
    def __init__(self, heuristic: Heuristic, weight: float = 1.0) -> None:
        self.heuristic = heuristic
        self.weight = weight

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        start_state = problem.initial_state()
        start_node = Node(start_state)

        frontier: List[Tuple[float, int, Node]] = []
        counter = 0

        def f(n: Node) -> float:
            # f(n) = g(n) + w * h(n)
            return n.path_cost + self.weight * self.heuristic(n.state)

        heapq.heappush(frontier, (f(start_node), counter, start_node))

        best_g: dict[Any, float] = {}
        nodes_expanded = 0

        while frontier:
            _, _, node = heapq.heappop(frontier)

            if problem.is_goal(node.state):
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=node,
                    success=True,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time,
                )

            state_key = problem.state_key(node.state)
            if state_key in best_g and best_g[state_key] <= node.path_cost:
                continue

            best_g[state_key] = node.path_cost
            nodes_expanded += 1

            for child in node.expand(problem):
                sk = problem.state_key(child.state)
                if sk not in best_g or child.path_cost < best_g[sk]:
                    counter += 1
                    heapq.heappush(frontier, (f(child), counter, child))

        end_time = time.perf_counter()
        return SearchResult(
            solution_node=None,
            success=False,
            nodes_expanded=nodes_expanded,
            runtime=end_time - start_time,
        )


class GreedyBestFirstSearch(SearchAlgorithm):
    def __init__(self, heuristic: Heuristic) -> None:
        self.heuristic = heuristic

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        start_state = problem.initial_state()
        start_node = Node(start_state)

        frontier: List[Tuple[float, int, Node]] = []
        counter = 0

        def f(n: Node) -> float:
            return self.heuristic(n.state)

        heapq.heappush(frontier, (f(start_node), counter, start_node))
        visited: set[Any] = set()
        nodes_expanded = 0

        while frontier:
            _, _, node = heapq.heappop(frontier)
            state_key = problem.state_key(node.state)

            if state_key in visited:
                continue
            visited.add(state_key)

            if problem.is_goal(node.state):
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=node,
                    success=True,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time,
                )

            nodes_expanded += 1

            for child in node.expand(problem):
                ck = problem.state_key(child.state)
                if ck not in visited:
                    counter += 1
                    heapq.heappush(frontier, (f(child), counter, child))

        end_time = time.perf_counter()
        return SearchResult(
            solution_node=None,
            success=False,
            nodes_expanded=nodes_expanded,
            runtime=end_time - start_time,
        )


class HillClimbingSearch(SearchAlgorithm):
    def __init__(self, heuristic: Heuristic, max_steps: int = 1000) -> None:
        self.heuristic = heuristic
        self.max_steps = max_steps

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        current_state = problem.initial_state()
        current_node = Node(current_state)
        current_h = self.heuristic(current_state)

        nodes_expanded = 0
        iterations = 0

        for _ in range(self.max_steps):
            iterations += 1
            if problem.is_goal(current_state):
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=current_node,
                    success=True,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time,
                    iterations=iterations,
                )

            neighbors: list[Node] = []
            for action in problem.actions(current_state):
                next_state = problem.result(current_state, action)
                nodes_expanded += 1
                neighbors.append(
                    Node(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=current_node.path_cost
                        + problem.step_cost(current_state, action, next_state),
                        depth=current_node.depth + 1,
                    )
                )

            if not neighbors:
                break

            best_neighbor = min(neighbors, key=lambda n: self.heuristic(n.state))
            best_h = self.heuristic(best_neighbor.state)

            if best_h >= current_h:
                break

            current_node = best_neighbor
            current_state = best_neighbor.state
            current_h = best_h

        end_time = time.perf_counter()
        success = problem.is_goal(current_state)
        return SearchResult(
            solution_node=current_node if success else None,
            success=success,
            nodes_expanded=nodes_expanded,
            runtime=end_time - start_time,
            iterations=iterations,
        )


class SimulatedAnnealingSearch(SearchAlgorithm):
    def __init__(
        self,
        heuristic: Heuristic,
        T0: float = 10.0,
        alpha: float = 0.99,
        max_steps: int = 5000,
    ) -> None:
        self.heuristic = heuristic
        self.T0 = T0
        self.alpha = alpha
        self.max_steps = max_steps

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        current_state = problem.initial_state()
        current_node = Node(current_state)
        current_h = self.heuristic(current_state)

        T = self.T0
        nodes_expanded = 0
        iterations = 0

        for _ in range(self.max_steps):
            iterations += 1

            if problem.is_goal(current_state):
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=current_node,
                    success=True,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time,
                    iterations=iterations,
                )

            if T <= 1e-8:
                break

            actions = list(problem.actions(current_state))
            if not actions:
                break

            action = random.choice(actions)
            next_state = problem.result(current_state, action)
            nodes_expanded += 1

            next_h = self.heuristic(next_state)
            delta = next_h - current_h

            if delta < 0:
                current_node = Node(
                    state=next_state,
                    parent=current_node,
                    action=action,
                    path_cost=current_node.path_cost
                    + problem.step_cost(current_state, action, next_state),
                    depth=current_node.depth + 1,
                )
                current_state = next_state
                current_h = next_h
            else:
                p = math.exp(-delta / T)
                if random.random() < p:
                    current_node = Node(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=current_node.path_cost
                        + problem.step_cost(current_state, action, next_state),
                        depth=current_node.depth + 1,
                    )
                    current_state = next_state
                    current_h = next_h

            T *= self.alpha

        end_time = time.perf_counter()
        success = problem.is_goal(current_state)
        return SearchResult(
            solution_node=current_node if success else None,
            success=success,
            nodes_expanded=nodes_expanded,
            runtime=end_time - start_time,
            iterations=iterations,
        )


class IDAStarSearch(SearchAlgorithm):
    def __init__(self, heuristic: Heuristic) -> None:
        self.heuristic = heuristic

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        root = Node(problem.initial_state())
        bound = self.heuristic(root.state)
        nodes_expanded = 0

        def search_recursive(node: Node, g: float, bound: float) -> tuple[float, Node | None]:
            nonlocal nodes_expanded
            f = g + self.heuristic(node.state)
            
            if f > bound:
                return f, None
            
            if problem.is_goal(node.state):
                return -1.0, node
            
            min_val = float('inf')
            nodes_expanded += 1
            
            for action in problem.actions(node.state):
                next_state = problem.result(node.state, action)
                
                if node.parent and node.parent.state == next_state:
                    continue
                
                step_cost = problem.step_cost(node.state, action, next_state)
                child = Node(
                    state=next_state,
                    parent=node,
                    action=action,
                    path_cost=g + step_cost,
                    depth=node.depth + 1
                )
                
                t, solution = search_recursive(child, g + step_cost, bound)
                
                if t == -1.0:
                    return -1.0, solution
                
                if t < min_val:
                    min_val = t
            
            return min_val, None

        while True:
            t, solution = search_recursive(root, 0.0, bound)
            
            if t == -1.0:
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=solution,
                    success=True,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time
                )
            
            if t == float('inf'):
                end_time = time.perf_counter()
                return SearchResult(
                    solution_node=None,
                    success=False,
                    nodes_expanded=nodes_expanded,
                    runtime=end_time - start_time
                )
            
            bound = t


class GeneticAlgorithmSearch(SearchAlgorithm):
    def __init__(
        self,
        heuristic: Heuristic,
        population_size: int = 50,
        mutation_rate: float = 0.1,
        max_generations: int = 100,
        chromosome_length: int = 30
    ) -> None:
        self.heuristic = heuristic
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.chromosome_length = chromosome_length

    def search(self, problem: Problem) -> SearchResult:
        start_time = time.perf_counter()
        
        all_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

        def random_individual() -> List[str]:
            return [random.choice(all_actions) for _ in range(self.chromosome_length)]

        def evaluate(individual: List[str]) -> tuple[float, Node]:
            """
            Run the individual's plan. Return (fitness, final_node).
            Fitness = 1 / (h(state) + 1).
            """
            current_state = problem.initial_state()
            current_node = Node(current_state)
            
            for action in individual:
                valid_actions = list(problem.actions(current_state))
                if action in valid_actions:
                    next_state = problem.result(current_state, action)
                    current_node = Node(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=current_node.path_cost + 1,
                        depth=current_node.depth + 1
                    )
                    current_state = next_state
                    if problem.is_goal(current_state):
                        return float('inf'), current_node
                else:
                    pass
            
            h_val = self.heuristic(current_state)
            return 1.0 / (h_val + 1.0), current_node

        population = [random_individual() for _ in range(self.population_size)]
        
        nodes_expanded = 0
        best_solution: Node | None = None
        scored_population = []
        
        for generation in range(self.max_generations):
            scored_population = []
            for ind in population:
                fitness, final_node = evaluate(ind)
                nodes_expanded += self.chromosome_length
                scored_population.append((fitness, ind))
                
                if fitness == float('inf'):
                    end_time = time.perf_counter()
                    return SearchResult(
                        solution_node=final_node,
                        success=True,
                        nodes_expanded=nodes_expanded,
                        runtime=end_time - start_time,
                        iterations=generation
                    )
            
            scored_population.sort(key=lambda x: x[0], reverse=True)
            
            new_population = [scored_population[0][1]]
            
            while len(new_population) < self.population_size:
                parent1 = self._select(scored_population)
                parent2 = self._select(scored_population)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, all_actions)
                new_population.append(child)
            
            population = new_population

        best_fitness, best_ind = scored_population[0]
        _, best_node = evaluate(best_ind)
        
        end_time = time.perf_counter()
        return SearchResult(
            solution_node=best_node if problem.is_goal(best_node.state) else None,
            success=problem.is_goal(best_node.state),
            nodes_expanded=nodes_expanded,
            runtime=end_time - start_time,
            iterations=self.max_generations
        )

    def _select(self, scored_population: List[Tuple[float, List[str]]]) -> List[str]:
        k = 3
        candidates = random.sample(scored_population, k)
        return max(candidates, key=lambda x: x[0])[1]

    def _crossover(self, p1: List[str], p2: List[str]) -> List[str]:
        point = random.randint(1, len(p1) - 1)
        return p1[:point] + p2[point:]

    def _mutate(self, ind: List[str], all_actions: List[str]) -> List[str]:
        if random.random() < self.mutation_rate:
            idx = random.randint(0, len(ind) - 1)
            ind[idx] = random.choice(all_actions)
        return ind
