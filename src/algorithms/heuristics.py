from __future__ import annotations
from typing import Callable, Tuple

Heuristic = Callable[[Tuple[int, ...]], float]


def misplaced_tiles_heuristic(goal_state: Tuple[int, ...]) -> Heuristic:
    def h(state: Tuple[int, ...]) -> float:
        misplaced = 0
        for i, tile in enumerate(state):
            if tile != 0 and tile != goal_state[i]:
                misplaced += 1
        return float(misplaced)

    return h


def manhattan_distance_heuristic(goal_state: Tuple[int, ...], size: int) -> Heuristic:
    tile_to_pos: dict[int, tuple[int, int]] = {}
    for idx, tile in enumerate(goal_state):
        row, col = divmod(idx, size)
        tile_to_pos[tile] = (row, col)

    def h(state: Tuple[int, ...]) -> float:
        total = 0
        for idx, tile in enumerate(state):
            if tile == 0:
                continue
            row, col = divmod(idx, size)
            goal_row, goal_col = tile_to_pos[tile]
            total += abs(row - goal_row) + abs(col - goal_col)
        return float(total)

    return h


def linear_conflict_heuristic(goal_state: Tuple[int, ...], size: int) -> Heuristic:
    manhattan = manhattan_distance_heuristic(goal_state, size)
    
    tile_to_pos: dict[int, tuple[int, int]] = {}
    for idx, tile in enumerate(goal_state):
        row, col = divmod(idx, size)
        tile_to_pos[tile] = (row, col)

    def h(state: Tuple[int, ...]) -> float:
        h_val = manhattan(state)
        
        conflicts = 0
        
        for r in range(size):
            row_tiles = []
            for c in range(size):
                tile = state[r * size + c]
                if tile != 0:
                    t_r, t_c = tile_to_pos[tile]
                    if t_r == r:
                        row_tiles.append((tile, c, t_c))
            
            for i in range(len(row_tiles)):
                for j in range(i + 1, len(row_tiles)):
                    t1_val, t1_cur, t1_goal = row_tiles[i]
                    t2_val, t2_cur, t2_goal = row_tiles[j]
                    
                    if t1_goal > t2_goal:
                        conflicts += 1

        for c in range(size):
            col_tiles = []
            for r in range(size):
                tile = state[r * size + c]
                if tile != 0:
                    t_r, t_c = tile_to_pos[tile]
                    if t_c == c:
                        col_tiles.append((tile, r, t_r))
            
            for i in range(len(col_tiles)):
                for j in range(i + 1, len(col_tiles)):
                    t1_val, t1_cur, t1_goal = col_tiles[i]
                    t2_val, t2_cur, t2_goal = col_tiles[j]
                    
                    if t1_goal > t2_goal:
                        conflicts += 1

        return h_val + 2 * conflicts

    return h
