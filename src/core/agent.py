from __future__ import annotations
from .problem import Problem
from .results import SearchResult
from src.algorithms import SearchAlgorithm


class SearchAgent:
    def __init__(self, problem: Problem, algorithm: SearchAlgorithm) -> None:
        self.problem = problem
        self.algorithm = algorithm

    def solve(self) -> SearchResult:
        return self.algorithm.search(self.problem)
