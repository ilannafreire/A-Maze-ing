"""Spanning-tree maze carving algorithms."""

from collections import deque
from random import Random

from mazegen.errors import MazeGenerationError
from mazegen.grid import (
    Coordinate,
    Direction,
    MazeGrid,
    neighbors,
    open_edge,
)


def generate_tree(
    width: int,
    height: int,
    blocked: set[Coordinate],
    algorithm: str,
    randomizer: Random,
) -> MazeGrid:
    """Build a connected spanning tree using BFS or iterative backtracking."""
    grid = [[15 for _ in range(width)] for _ in range(height)]
    visited = {(0, 0)}
    if algorithm == "bfs":
        _carve_bfs(grid, width, height, blocked, randomizer, visited)
    else:
        _carve_backtracker(grid, width, height, blocked, randomizer, visited)

    expected = width * height - len(blocked)
    if len(visited) != expected:
        raise MazeGenerationError(
            "The 42 pattern leaves the traversable maze disconnected."
        )
    return grid


def _unvisited_neighbors(
    width: int,
    height: int,
    blocked: set[Coordinate],
    cell: Coordinate,
    visited: set[Coordinate],
) -> list[tuple[Coordinate, Direction]]:
    """Return available neighbors that are not already in the tree."""
    return [
        (neighbor, direction)
        for neighbor, direction in neighbors(width, height, blocked, cell)
        if neighbor not in visited
    ]


def _carve_bfs(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    randomizer: Random,
    visited: set[Coordinate],
) -> None:
    """Carve a randomized breadth-first spanning tree."""
    queue = deque(visited)
    while queue:
        cell = queue.popleft()
        options = _unvisited_neighbors(width, height, blocked, cell, visited)
        randomizer.shuffle(options)
        for neighbor, direction in options:
            if neighbor in visited:
                continue
            open_edge(grid, cell, direction)
            visited.add(neighbor)
            queue.append(neighbor)


def _carve_backtracker(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    randomizer: Random,
    visited: set[Coordinate],
) -> None:
    """Carve a randomized depth-first spanning tree without recursion."""
    stack = list(visited)
    while stack:
        cell = stack[-1]
        options = _unvisited_neighbors(width, height, blocked, cell, visited)
        if not options:
            stack.pop()
            continue
        randomizer.shuffle(options)
        neighbor, direction = options[0]
        open_edge(grid, cell, direction)
        visited.add(neighbor)
        stack.append(neighbor)