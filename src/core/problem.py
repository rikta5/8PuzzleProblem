from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Hashable


class Problem(ABC):
    
    @abstractmethod
    def initial_state(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def actions(self, state: Any) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def result(self, state: Any, action: Any) -> Any:
        raise NotImplementedError

    def step_cost(self, state: Any, action: Any, next_state: Any) -> float:
        return 1.0

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        raise NotImplementedError

    def state_key(self, state: Any) -> Hashable:
        return state

    def display_state(self, state: Any) -> str:
        return str(state)
