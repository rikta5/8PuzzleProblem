from __future__ import annotations
from typing import Iterable, List, Tuple
import random
from src.core import Problem

class SlidingPuzzleProblem(Problem):
    def __init__(
        self,
        size: int = 3,
        initial_state: Tuple[int, ...] | None = None,
        goal_state: Tuple[int, ...] | None = None,
    ) -> None:
        assert size >= 2, "Puzzle size must be at least 2x2"
        self.size = size
        self._goal_state: Tuple[int, ...] = (
            goal_state if goal_state is not None else self._default_goal_state()
        )
        self._initial_state: Tuple[int, ...] = (
            initial_state if initial_state is not None else self._goal_state
        )

    def _default_goal_state(self) -> Tuple[int, ...]:
        n = self.size * self.size
        return tuple(list(range(1, n)) + [0])

    @property
    def goal_state(self) -> Tuple[int, ...]:
        return self._goal_state

    def initial_state(self) -> Tuple[int, ...]:
        return self._initial_state

    def _index_to_pos(self, index: int) -> tuple[int, int]:
        return divmod(index, self.size)

    def _pos_to_index(self, row: int, col: int) -> int:
        return row * self.size + col

    def actions(self, state: Tuple[int, ...]) -> Iterable[str]:
        idx_blank = state.index(0)
        row, col = self._index_to_pos(idx_blank)

        if row > 0:
            yield "UP"
        if row < self.size - 1:
            yield "DOWN"
        if col > 0:
            yield "LEFT"
        if col < self.size - 1:
            yield "RIGHT"

    def result(self, state: Tuple[int, ...], action: str) -> Tuple[int, ...]:
        idx_blank = state.index(0)
        row, col = self._index_to_pos(idx_blank)

        if action == "UP":
            new_row, new_col = row - 1, col
        elif action == "DOWN":
            new_row, new_col = row + 1, col
        elif action == "LEFT":
            new_row, new_col = row, col - 1
        elif action == "RIGHT":
            new_row, new_col = row, col + 1
        else:
            raise ValueError(f"Unknown action: {action}")

        idx_swap = self._pos_to_index(new_row, new_col)

        state_list = list(state)
        state_list[idx_blank], state_list[idx_swap] = state_list[idx_swap], state_list[idx_blank]
        return tuple(state_list)

    def is_goal(self, state: Tuple[int, ...]) -> bool:
        return state == self._goal_state

    def display_state(self, state: Tuple[int, ...]) -> str:
        rows: List[str] = []
        for r in range(self.size):
            row_vals = []
            for c in range(self.size):
                val = state[self._pos_to_index(r, c)]
                row_vals.append(" ." if val == 0 else f"{val:2d}")
            rows.append(" ".join(row_vals))
        return "\n".join(rows)

    @classmethod
    def scrambled(
        cls,
        size: int = 3,
        scramble_depth: int = 20,
        seed: int | None = None,
    ) -> "SlidingPuzzleProblem":
        rng = random.Random(seed)
        base = cls(size=size)
        state = base.goal_state
        for _ in range(scramble_depth):
            acts = list(base.actions(state))
            a = rng.choice(acts)
            state = base.result(state, a)
        return cls(size=size, initial_state=state, goal_state=base.goal_state)
