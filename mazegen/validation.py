"""Validation for public maze generator options."""

from mazegen.errors import MazeGenerationError
from mazegen.grid import Coordinate


def validate_configuration(
    width: int,
    height: int,
    entry: Coordinate,
    exit: Coordinate,
    algorithm: str,
) -> None:
    """Reject invalid dimensions, coordinates, or algorithm names."""
    if width < 1 or height < 1:
        raise MazeGenerationError("Maze width and height must be positive.")
    if width * height < 2:
        raise MazeGenerationError("The maze must contain at least two cells.")
    if algorithm not in {"bfs", "backtracker"}:
        raise MazeGenerationError(
            "Algorithm must be 'bfs' or 'backtracker'."
        )
    for name, cell in (("entry", entry), ("exit", exit)):
        if (
            len(cell) != 2
            or not 0 <= cell[0] < width
            or not 0 <= cell[1] < height
        ):
            raise MazeGenerationError(
                f"The {name} coordinate must be inside the maze."
            )
    if entry == exit:
        raise MazeGenerationError("Entry and exit must be different cells.")