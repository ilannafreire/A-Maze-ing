"""Post-process spanning trees into playable, low-dead-end boards."""

from random import Random

from mazegen.errors import MazeGenerationError
from mazegen.grid import (
    EAST,
    SOUTH,
    Coordinate,
    Direction,
    MazeGrid,
    neighbors,
    open_edge,
)


def _degree(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    cell: Coordinate,
) -> int:
    """Count open passages from a traversable cell."""
    x, y = cell
    return sum(
        not grid[y][x] & direction[2]
        for _, direction in neighbors(width, height, blocked, cell)
    )


def _would_open_3x3(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    cell: Coordinate,
    direction: Direction,
) -> bool:
    """Temporarily open an edge and detect a fully open 3-by-3 block."""
    open_edge(grid, cell, direction)
    creates_area = any(
        all(
            (left + x, top + y) not in blocked
            for x in range(3)
            for y in range(3)
        )
        and all(
            not grid[top + y][left + x] & EAST
            for y in range(3)
            for x in range(2)
        )
        and all(
            not grid[top + y][left + x] & SOUTH
            for y in range(2)
            for x in range(3)
        )
        for top in range(height - 2)
        for left in range(width - 2)
    )
    if creates_area:
        x, y = cell
        dx, dy, wall, opposite_wall, _ = direction
        grid[y][x] |= wall
        grid[y + dy][x + dx] |= opposite_wall
    return creates_area


def _safe_candidates(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    cell: Coordinate,
    randomizer: Random,
) -> list[Direction]:
    """Find closed edges that can open without a fully open 3-by-3 block."""
    x, y = cell
    candidates = [
        direction
        for neighbor, direction in neighbors(width, height, blocked, cell)
        if grid[y][x] & direction[2]
        and grid[neighbor[1]][neighbor[0]] & direction[3]
    ]
    randomizer.shuffle(candidates)
    safe: list[Direction] = []
    for direction in candidates:
        if _would_open_3x3(
            grid, width, height, blocked, cell, direction
        ):
            continue
        safe.append(direction)
        dx, dy = direction[0], direction[1]
        grid[y][x] |= direction[2]
        grid[y + dy][x + dx] |= direction[3]
    return safe


def _cycle_rank(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
) -> int:
    """Count independent loops in a connected maze graph."""
    vertices = width * height - len(blocked)
    edges = sum(
        _degree(grid, width, height, blocked, (x, y))
        for y in range(height)
        for x in range(width)
    ) // 2
    return edges - vertices + 1


def braid(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    randomizer: Random,
) -> None:
    """Remove dead ends and add at least two safe independent loops."""
    cells = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked
    ]
    dead_ends = [
        cell for cell in cells
        if _degree(grid, width, height, blocked, cell) == 1
    ]
    randomizer.shuffle(dead_ends)
    for cell in dead_ends:
        if _degree(grid, width, height, blocked, cell) != 1:
            continue
        options = _safe_candidates(
            grid, width, height, blocked, cell, randomizer
        )
        if options:
            open_edge(grid, cell, options[0])

    while _cycle_rank(grid, width, height, blocked) < 2:
        edges = [
            (cell, direction)
            for cell in cells
            for neighbor, direction in neighbors(
                width, height, blocked, cell
            )
            if direction[0] >= 0
            and direction[1] >= 0
            and grid[cell[1]][cell[0]] & direction[2]
        ]
        randomizer.shuffle(edges)
        for cell, direction in edges:
            if _would_open_3x3(
                grid, width, height, blocked, cell, direction
            ):
                continue
            open_edge(grid, cell, direction)
            break
        else:
            raise MazeGenerationError(
                "This maze cannot provide two loops without a 3-by-3 area."
            )
