"""Shared coordinate, wall, and grid operations."""

from collections import deque

Coordinate = tuple[int, int]
Direction = tuple[int, int, int, int, str]
MazeGrid = list[list[int]]

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

DIRECTIONS: tuple[Direction, ...] = (
    (0, -1, NORTH, SOUTH, "N"),
    (1, 0, EAST, WEST, "E"),
    (0, 1, SOUTH, NORTH, "S"),
    (-1, 0, WEST, EAST, "W"),
)


def neighbors(
    width: int,
    height: int,
    blocked: set[Coordinate],
    cell: Coordinate,
) -> list[tuple[Coordinate, Direction]]:
    """Return in-bounds, traversable neighbors and their directions."""
    x, y = cell
    result: list[tuple[Coordinate, Direction]] = []
    for direction in DIRECTIONS:
        neighbor = (x + direction[0], y + direction[1])
        if (
            0 <= neighbor[0] < width
            and 0 <= neighbor[1] < height
            and neighbor not in blocked
        ):
            result.append((neighbor, direction))
    return result


def open_edge(
    grid: MazeGrid, cell: Coordinate, direction: Direction
) -> None:
    """Open a passage and update both cells' shared wall bits."""
    x, y = cell
    dx, dy, wall, opposite_wall, _ = direction
    grid[y][x] &= ~wall
    grid[y + dy][x + dx] &= ~opposite_wall


def is_connected(
    grid: MazeGrid,
    width: int,
    height: int,
    blocked: set[Coordinate],
    start: Coordinate,
) -> bool:
    """Return whether every non-blocked cell is reachable from start."""
    visited = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for neighbor, direction in neighbors(width, height, blocked, (x, y)):
            if grid[y][x] & direction[2] or neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append(neighbor)
    return len(visited) == width * height - len(blocked)