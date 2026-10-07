"""Terminal rendering for generated mazes."""

import sys
from time import sleep

from mazegen.generator import EAST, NORTH, SOUTH, WEST, MazeGenerator

_COLORS = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "gray": "90",
    "bright_red": "91",
    "bright_green": "92",
    "bright_yellow": "93",
    "bright_blue": "94",
    "bright_magenta": "95",
    "bright_cyan": "96",
    "bright_white": "97",
}
_STEPS = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}


def _paint(text: str, color: str, use_color: bool) -> str:
    """Apply an ANSI color when color output is enabled."""
    if not use_color:
        return text
    return f"\033[{_COLORS[color]}m{text}\033[0m"


def _path_cells(maze: MazeGenerator) -> set[tuple[int, int]]:
    """Return the cells visited by the current solution."""
    x, y = maze.entry
    cells = {(x, y)}
    for step in maze.solution:
        dx, dy = _STEPS[step]
        x += dx
        y += dy
        cells.add((x, y))
    return cells


def _cell_cursor(cell: tuple[int, int]) -> str:
    """Return the terminal cursor sequence for one maze cell's label."""
    x, y = cell
    return f"\033[{2 * y + 2};{4 * x + 2}H"


def animate_solution(
    maze: MazeGenerator,
    color: str = "magenta",
    delay: float = 0.045,
) -> bool:
    """Animate the route in place when stdout is interactive.

    Return false when stdout is redirected.
    """
    if not sys.stdout.isatty():
        return False

    x, y = maze.entry
    positions = [(x, y)]
    for step in maze.solution:
        dx, dy = _STEPS[step]
        x += dx
        y += dy
        if (x, y) in maze.blocked_cells:
            raise ValueError("The maze solution crosses a blocked 42 cell.")
        positions.append((x, y))

    print("\033[2J\033[H", end="")
    print(render_maze(maze, show_path=False, color=color))
    for cell in positions[1:-1]:
        print(
            _cell_cursor(cell) + _paint(" * ", "bright_yellow", True),
            end="",
            flush=True,
        )
        sleep(delay)
    print(f"\033[{2 * maze.height + 3};1H", end="", flush=True)
    return True


def render_maze(
    maze: MazeGenerator,
    show_path: bool = True,
    color: str = "magenta",
    use_color: bool = True,
) -> str:
    """Render walls, the 42 pattern, endpoints, and optional shortest route."""
    normalized_color = color.lower()
    if normalized_color not in _COLORS:
        valid = ", ".join(_COLORS)
        message = f"Unknown wall color '{color}'. Choose from: {valid}."
        raise ValueError(message)

    path = _path_cells(maze) if show_path else set()
    lines: list[str] = []
    for y, row in enumerate(maze.grid):
        top = [_paint("+", normalized_color, use_color)]
        for walls in row:
            segment = "---" if walls & NORTH else "   "
            top.append(_paint(segment, normalized_color, use_color))
            top.append(_paint("+", normalized_color, use_color))
        lines.append("".join(top))

        middle: list[str] = []
        for x, walls in enumerate(row):
            left = "|" if walls & WEST else " "
            middle.append(_paint(left, normalized_color, use_color))
            cell = (x, y)
            if cell in maze.blocked_cells:
                label = "███"
                label_color = "gray"
            elif cell == maze.entry:
                label = " E "
                label_color = "bright_green"
            elif cell == maze.exit:
                label = " X "
                label_color = "bright_red"
            elif show_path and cell in path:
                label = " * "
                label_color = "bright_yellow"
            else:
                label = "   "
                label_color = normalized_color
            middle.append(_paint(label, label_color, use_color))
        right = "|" if row[-1] & EAST else " "
        middle.append(_paint(right, normalized_color, use_color))
        lines.append("".join(middle))

    bottom = [_paint("+", normalized_color, use_color)]
    for walls in maze.grid[-1]:
        segment = "---" if walls & SOUTH else "   "
        bottom.append(_paint(segment, normalized_color, use_color))
        bottom.append(_paint("+", normalized_color, use_color))
    lines.append("".join(bottom))
    return "\n".join(lines)
