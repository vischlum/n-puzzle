"""
All the necessary functions to check if a given n-puzzle is solvable.
"""

from dataclass import Puzzle


def get_inversion_sum(puzzle: Puzzle) -> int:
    """
    Compute how many inversions are necessary
    to go from the starting state to the target solution
    """
    inversion_sum: int = 0

    for index, number in enumerate(puzzle.start):
        previous_numbers_in_grid = puzzle.start[:index]
        previous_numbers_in_goal = puzzle.goal[: puzzle.goal.index(number)]
        permutation_inversions = [
            x for x in previous_numbers_in_goal if x not in previous_numbers_in_grid
        ]
        inversion_sum += len(permutation_inversions)

    return inversion_sum


def check_solvability(puzzle: Puzzle) -> bool:
    """
    To be solvable, the parity of the inversion sum must be the same
    as that of the number of moves for the blank tile
    """
    inversion_sum = get_inversion_sum(puzzle)

    zero_in_grid_x = puzzle.start.index(0) % puzzle.size
    zero_in_grid_y = puzzle.start.index(0) // puzzle.size
    zero_in_goal_x = puzzle.goal.index(0) % puzzle.size
    zero_in_goal_y = puzzle.goal.index(0) // puzzle.size
    diff_zero = abs(zero_in_grid_x - zero_in_goal_x) + abs(
        zero_in_grid_y - zero_in_goal_y
    )

    if inversion_sum % 2 != 0 and diff_zero % 2 != 0:
        return True
    if inversion_sum % 2 == 0 and diff_zero % 2 == 0:
        return True
    return False
