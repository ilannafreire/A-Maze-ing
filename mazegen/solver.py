"""Breadth-first shortest-path search for maze grids."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from mazegen.errors import MazeGenerationError
from mazegen.grid import Coordinate, MazeGrid, neighbors

if TYPE_CHECKING:
    from mazegen.generator import MazeGenerator


def find_shortest_path(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    entry: Coordinate,
    exit: Coordinate,
) -> list[str]:
    """Find the shortest route using BFS and parent links."""
    queue = deque([entry])
    previous: dict[Coordinate, tuple[Coordinate, str] | None] = {entry: None}
    while queue:
        cell = queue.popleft()
        if cell == exit:
            break
        x, y = cell
        for neighbor, direction in neighbors(width, height, blocked, cell):
            if grid[y][x] & direction[2] or neighbor in previous:
                continue
            previous[neighbor] = (cell, direction[4])
            queue.append(neighbor)
    if exit not in previous:
        raise MazeGenerationError("No path connects entry and exit.")

    path: list[str] = []
    cell = exit
    while cell != entry:
        step = previous[cell]
        if step is None:
            break
        cell, direction = step
        path.append(direction)
    path.reverse()
    return path


def shortest_path(maze: MazeGenerator) -> list[str]:
    """Return a generated maze's shortest route, preserving the old helper."""
    return find_shortest_path(
        maze.grid,
        maze.width,
        maze.height,
        maze.blocked_cells,
        maze.entry,
        maze.exit,
    )
