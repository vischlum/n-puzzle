"""
Contains the various heuristics used by A-star to solve the puzzle
"""

from functools import cache
from dataclass import HeuristicCallback


def select_heuristic(
    arg: str,
) -> HeuristicCallback:
    """
    Returns the appropriate heuristic function depending on the flag passed as argument
    """
    heuristics = {
        "uniform": generate_uniform_cost,
        "hamming": generate_hamming_distance,
        "manhattan": generate_manhattan_distance,
        "linear": generate_linear_conflicts,
    }

    return heuristics.get(arg, generate_manhattan_distance)


def generate_uniform_cost(  # pylint: disable=unused-argument
    size: int, grid: tuple[int, ...], goal: tuple[int, ...]
) -> int:
    """
    Uniform-cost is not really a heuristic, it's in fact the absence of heuristic.
    Uniform-cost search is uninformed search: f(n) = g(n) (there's no h(n))
    """
    return 0


def generate_hamming_distance(
    size: int, grid: tuple[int, ...], goal: tuple[int, ...]
) -> int:
    """
    The Hamming Distance is the number of tiles not in their final position.

    The blank tile is ignored, to ensure that this heuristic is not an underestimate.
    """
    hamming_distance: int = 0

    for index in range(size * size):
        if grid[index] != goal[index] and grid[index] != 0:
            hamming_distance += 1

    return hamming_distance


def generate_manhattan_distance(
    size: int, grid: tuple[int, ...], goal: tuple[int, ...]
) -> int:
    """
    The Manhattan Distance is the sum of the minimal number of moves necessary
    for each tile to get to its final position.

    The blank tile is ignored, to ensure that this heuristic is not an underestimate.
    """
    manhattan_distance: int = 0

    for index in range(size * size):
        if grid[index] != goal[index] and grid[index] != 0:
            goal_tile = goal.index(grid[index])
            manhattan_distance += abs(index % size - goal_tile % size) + abs(
                index // size - goal_tile // size
            )

    return manhattan_distance


@cache
def get_conflicts_in_line(
    size: int,
    grid_line: tuple[int, ...],
    goal_line: tuple[int, ...],
    conflicts_in_line: int = 0,
) -> int:
    """
    Returns the minimal number of conflicts to be solved in a given line.

    To make sure that the _minimal_ number is returned:
    - the tile with the most conflits is deleted
    - the number of conflicts (without that tile) is recomputed using recursion

    Using tuples instead of lists allows the use of `@cache`
    """
    conflicts = [0 for x in range(size)]

    # pylint: disable=too-many-nested-blocks
    for index_j, value_j in enumerate(grid_line):
        if value_j in goal_line and value_j != 0:
            for index_k, value_k in enumerate(grid_line):
                if value_k in goal_line and value_k != 0:
                    if value_j != value_k:
                        if (
                            goal_line.index(value_j) > goal_line.index(value_k)
                        ) and index_j < index_k:
                            conflicts[index_j] += 1
                        elif (
                            goal_line.index(value_j) < goal_line.index(value_k)
                        ) and index_j > index_k:
                            conflicts[index_j] += 1

    if max(conflicts) != 0:
        index = conflicts.index(max(conflicts))
        tmp = list(grid_line)
        tmp[index] = -1
        grid_line = tuple(tmp)
        conflicts_in_line += 1
        return get_conflicts_in_line(size, grid_line, goal_line, conflicts_in_line)

    return conflicts_in_line


def generate_linear_conflicts(
    size: int, grid: tuple[int, ...], goal: tuple[int, ...]
) -> int:
    """
    Two tiles tj and tk are in linear conflict if (cumulatively):
    - they are in the same line
    - their goal positions are both in that line
    - tj is to the right of tk and its goal is to the left of tk's (or vice versa)

    Linear conflict is combined with the Manhattan Distance to get h(n).

    The blank tile is ignored, to ensure that this heuristic is not an underestimate.
    """
    linear_conflicts: int = 0
    manhattan_distance: int = generate_manhattan_distance(size, grid, goal)

    grid_columns: list[list[int]] = [[] for x in range(size)]
    goal_columns: list[list[int]] = [[] for x in range(size)]
    grid_rows: list[list[int]] = [[] for y in range(size)]
    goal_rows: list[list[int]] = [[] for y in range(size)]

    for row in range(size):
        for col in range(size):
            index = col + (row * size)
            grid_columns[col].append(grid[index])
            goal_columns[col].append(goal[index])
            grid_rows[row].append(grid[index])
            goal_rows[row].append(goal[index])

    for i in range(size):
        linear_conflicts += get_conflicts_in_line(
            size, tuple(grid_columns[i]), tuple(goal_columns[i])
        )
        linear_conflicts += get_conflicts_in_line(
            size, tuple(grid_rows[i]), tuple(goal_rows[i])
        )

    return (linear_conflicts * 2) + manhattan_distance
