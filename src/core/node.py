from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from .problem import Problem


@dataclass(slots=True)
class Node:
    state: Any
    parent: Optional["Node"] = None
    action: Any = None
    path_cost: float = 0.0
    depth: int = 0

    def expand(self, problem: Problem) -> List["Node"]:
        children: List[Node] = []
        for action in problem.actions(self.state):
            next_state = problem.result(self.state, action)
            cost = self.path_cost + problem.step_cost(self.state, action, next_state)
            children.append(
                Node(
                    state=next_state,
                    parent=self,
                    action=action,
                    path_cost=cost,
                    depth=self.depth + 1,
                )
            )
        return children

    def solution_path(self) -> List["Node"]:
        node: Optional[Node] = self
        path: List[Node] = []
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))
