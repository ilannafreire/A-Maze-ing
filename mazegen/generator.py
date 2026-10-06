"""Public maze generator API composed from focused modules."""

from random import Random

from mazegen.braiding import braid
from mazegen.errors import MazeGenerationError
from mazegen.carving import generate_tree
from mazegen.grid import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    Coordinate,
    Direction,
    MazeGrid,
    is_connected,
)
from mazegen.pattern import make_42_mask
from mazegen.solver import find_shortest_path
from mazegen.validation import validate_configuration

__all__ = [
    "EAST",
    "MazeGenerationError",
    "MazeGenerator",
    "NORTH",
    "SOUTH",
    "WEST",
    "Direction",
]


class MazeGenerator:
    """Generate a maze and expose its grid and shortest solution.

    ``grid[y][x]`` stores a wall mask. ``solution`` is a list of cardinal
    direction letters. BFS and backtracker create the initial spanning tree;
    non-perfect mazes are then braided.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coordinate,
        exit: Coordinate,
        perfect: bool = False,
        seed: int | None = None,
        algorithm: str = "backtracker",
        include_42: bool = True,
    ) -> None:
        """Validate options and generate the initial maze."""
        algorithm = algorithm.lower()
        validate_configuration(width, height, entry, exit, algorithm)
        self.width, self.height = width, height
        self.entry, self.exit = entry, exit
        self.perfect, self.seed = perfect, seed
        self.algorithm = algorithm
        self.grid: MazeGrid = []
        self.solution: list[str] = []
        self.blocked_cells: set[Coordinate] = set()
        self.has_42 = False
        self._random = Random(seed)
        self.generate(include_42)

    def generate(self, include_42: bool = True) -> None:
        """Generate a fresh maze using the stored options and seed."""
        self._random = Random(self.seed)
        self.blocked_cells = (
            make_42_mask(
                self.width, self.height, self.entry, self.exit, self.perfect
            )
            if include_42 else set()
        )
        self.has_42 = bool(self.blocked_cells)
        self.grid = generate_tree(
            self.width,
            self.height,
            self.blocked_cells,
            self.algorithm,
            self._random,
        )
        if not is_connected(
            self.grid,
            self.width,
            self.height,
            self.blocked_cells,
            self.entry,
        ):
            raise MazeGenerationError("The generated maze is disconnected.")
        if not self.perfect:
            braid(
                self.grid,
                self.width,
                self.height,
                self.blocked_cells,
                self._random,
            )
        self.solution = self.shortest_path()

    def shortest_path(self) -> list[str]:
        """Find the shortest route from entry to exit using BFS."""
        return find_shortest_path(
            self.grid,
            self.width,
            self.height,
            self.blocked_cells,
            self.entry,
            self.exit,
        )
