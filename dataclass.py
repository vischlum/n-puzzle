"""
Define the Puzzle and Node dataclasses
"""

import random

from dataclasses import InitVar, dataclass, field

# pylint doesn't detect `Any` usage when declaring the NodeType TypeVar
from typing import (  # pylint: disable=unused-import
    Optional,
    Protocol,
    TypeVar,
    Generic,
    Any,
)


class HeuristicCallback(Protocol):  # pylint: disable=too-few-public-methods
    """
    mypy has a long-standing issue when assigning to a field of Callable type
    (see https://github.com/python/mypy/issues/708)
    This class is a workaround to ensure we still have static typing
    for the `heuristic` field of the `Puzzle` dataclass
    """

    def __call__(self, size: int, grid: tuple[int, ...], goal: tuple[int, ...]) -> int:
        pass


@dataclass
class Puzzle:
    """
    Utility class to store all the values needed to solve the puzzle
    """

    size: int
    start: tuple[int, ...]
    goal: tuple[int, ...] = field(init=False)
    valid_moves: tuple[tuple[int, ...], ...] = field(init=False)
    heuristic: HeuristicCallback = field(init=False)
    shape: InitVar[str]

    def __post_init__(self, shape: str) -> None:
        """
        Automatically generates the goal and the valid moves based on the size
        """
        self.goal = self.generate_goal(self.size, shape)
        self.valid_moves = self.generate_movelist(self.size)

    @staticmethod
    def generate_goal(size: int, shape: str) -> tuple[int, ...]:
        """
        Generates the desired end state of the puzzle,
        according to the shape given as argument
        """

        if shape == "ascending":
            grid = list(range(size ** 2))
        elif shape == "descending":
            grid = list(reversed(range(size ** 2)))
        elif shape == "random":
            grid = list(range(size ** 2))
            random.shuffle(grid)
        else:  # Spiral shape
            grid = [0] * size ** 2
            move_x, move_y = [0, 1, 0, -1], [1, 0, -1, 0]
            tile_x, tile_y, number = 0, -1, 1

            for i in range(size + size - 2):
                for _ in range((size + size - i) // 2):
                    tile_x += move_x[i % 4]
                    tile_y += move_y[i % 4]
                    index = tile_x * size + tile_y
                    grid[index] = number
                    number += 1

        return tuple(grid)

    @staticmethod
    def generate_movelist(size: int) -> tuple[tuple[int, ...], ...]:
        """
        Generates a tuple containing all the valid move for a given grid position:
        +1 = move right     | -1 = move left
        +size = move down   | -size = move up
        """
        movelist = []
        for tile in range(size * size):
            tile_x, tile_y = tile % size, tile // size
            moves = []
            if tile_x > 0:
                moves.append(-1)
            if tile_x < size - 1:
                moves.append(+1)
            if tile_y > 0:
                moves.append(-size)
            if tile_y < size - 1:
                moves.append(+size)
            movelist.append(tuple(moves))

        return tuple(movelist)


# This is necessary so that mypy knows how to type-check our Node class inside itself
NodeType = TypeVar("NodeType", bound="Node[Any]")


@dataclass
class Node(Generic[NodeType]):
    """
    Utility class used for each node of our graph
    Overriding __lt__ allows heapq to work for us
    """

    puzzle: Puzzle
    parent: Optional[NodeType]
    grid: tuple[int, ...]
    path_cost: int
    heuristic_cost: int = field(init=False)

    def __lt__(self: NodeType, other: NodeType) -> bool:
        return (
            self.path_cost + self.heuristic_cost
            < other.path_cost + other.heuristic_cost
        )

    def __post_init__(self) -> None:
        """
        Automatically generate h(n) on Node initialisation
        """
        self.heuristic_cost = self.puzzle.heuristic(
            self.puzzle.size, self.grid, self.puzzle.goal
        )
