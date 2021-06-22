"""
A* is a graph traversal algorithm, here used to solve n-puzzles
Its main drawback is its memory use (as it stores all generated nodes).
"""

import heapq
import time

from typing import Any
from dataclass import Puzzle, Node


def swap_tile(grid: tuple[int, ...], move: int) -> tuple[int, ...]:
    """
    Moves the blank tile according to the move given as argument.
    """
    tile_to_swap: int = grid.index(0) + move
    value_to_swap: int = grid[tile_to_swap]

    mutable_grid: list[int] = list(grid)
    mutable_grid[grid.index(0)] = value_to_swap
    mutable_grid[tile_to_swap] = 0
    swapped_grid = tuple(mutable_grid)

    return swapped_grid


def solve(puzzle: Puzzle, greedy_search: bool) -> tuple[float, list[tuple[int, ...]]]:
    """
    Our A* implementation:
    - `visited` is a set to make sure there are no duplicate nodes in it
    - `opened` is a priority queue so pop always returns the node with the smallest f(n)
    - `time_complexity` is the total number of states ever selected in opened
    - `size_complexity` is the maximum number of states ever represented in memory

    Returns two values:
    - the time spent to solve the puzzle
    - the list of all the moves uesd to solve the puzzle
    """
    time_before_solve = time.process_time()
    visited: set[tuple[int, ...]] = set()
    starting_node: Node[Any] = Node(puzzle, None, puzzle.start, 0)
    opened: list[Node[Any]] = []
    heapq.heappush(opened, starting_node)
    path_cost_increment: int = 1
    if greedy_search:
        path_cost_increment = 0
    time_complexity: int = 0
    size_complexity: int = 1

    while opened:
        current_node: Node[Any] = heapq.heappop(opened)
        time_complexity += 1
        if current_node.grid == puzzle.goal:
            break
        if current_node.grid in visited:
            continue
        visited.add(current_node.grid)

        valid_moves_for_zero = puzzle.valid_moves[current_node.grid.index(0)]
        for move in valid_moves_for_zero:
            next_grid = swap_tile(current_node.grid, move)

            if next_grid in visited:
                continue
            heapq.heappush(
                opened,
                Node(
                    puzzle,
                    current_node,
                    next_grid,
                    current_node.path_cost + path_cost_increment,
                ),
            )

        if size_complexity < len(opened) + len(visited):
            size_complexity = len(opened) + len(visited)

    time_after_solve = time.process_time()

    solution: list[tuple[int, ...]] = []
    while current_node.parent:
        solution.append(current_node.grid)
        current_node = current_node.parent
    solution.append(puzzle.start)
    solution.reverse()

    print_solution(solution, time_complexity, size_complexity)

    return (time_after_solve - time_before_solve, solution)


def print_solution(
    solution: list[tuple[int, ...]], time_complexity: int, size_complexity: int
) -> None:
    """
    Print the solution to the puzzle (ie all the required moves)
    and the complexity metrics (in time and size)
    """
    print("\033[32;1m🎉 The puzzle was solved 🎉\033[m")
    print(
        f"\033[35;1m{len(solution)-1:,} moves\033[m were necessary to get to the solution:"
    )
    for move in solution:
        print(f"\t{move}")
    print(
        f"""Time complexity = \033[33;1m{time_complexity
        :,}\033[m | Size complexity = \033[33;1m{size_complexity:,}\033[m"""
    )
