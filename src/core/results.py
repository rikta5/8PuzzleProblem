from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from .node import Node

@dataclass
class SearchResult:
    """
    Container for search outcomes.

    Attributes:
        solution_node:  Node that reached the goal, or None if no solution.
        success:        True if a goal was reached.
        nodes_expanded: Number of nodes that were expanded during search.
        runtime:        Wall clock runtime in seconds.
        iterations:     For iterative algorithms (hill climbing, SA), the
                        number of outer loop iterations. Zero for tree search.
    """
    solution_node: Optional[Node]
    success: bool
    nodes_expanded: int
    runtime: float
    iterations: int = 0

    @property
    def solution_path(self) -> List[Node]:
        """Return the sequence of nodes from root to goal, or [] if no solution."""
        if self.solution_node is None:
            return []
        return self.solution_node.solution_path()

    @property
    def solution_cost(self) -> float:
        """Return the path cost of the solution, or +inf if there is no solution."""
        if self.solution_node is None:
            return float("inf")
        return self.solution_node.path_cost
