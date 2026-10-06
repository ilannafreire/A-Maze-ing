"""Build the optional closed-cell 42 pattern."""

from mazegen.errors import MazeGenerationError
from mazegen.grid import Coordinate

_FORTY_TWO = (
    "#...#.#####",
    "#...#.....#",
    "#...#.....#",
    "#####.#####",
    "....#.#....",
    "....#.#....",
    "....#.#####",
)


def make_42_mask(
    width: int,
    height: int,
    entry: Coordinate,
    exit: Coordinate,
    perfect: bool,
) -> set[Coordinate]:
    """Place the pattern without covering endpoints or the playable center."""
    pattern_width = len(_FORTY_TWO[0])
    pattern_height = len(_FORTY_TWO)
    if width < pattern_width + 2 or height < pattern_height + 2:
        return set()

    preferred = ((width - pattern_width) // 2, (height - pattern_height) // 2)
    center = (width // 2, height // 2)
    origins = [
        (x, y)
        for y in range(1, height - pattern_height)
        for x in range(1, width - pattern_width)
    ]
    origins.sort(
        key=lambda point: (
            abs(point[0] - preferred[0]) + abs(point[1] - preferred[1]),
            point[1],
            point[0],
        )
    )
    for origin_x, origin_y in origins:
        blocked = {
            (origin_x + x, origin_y + y)
            for y, row in enumerate(_FORTY_TWO)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        endpoints_open = entry not in blocked and exit not in blocked
        center_open = perfect or center not in blocked
        if endpoints_open and center_open:
            return blocked
    raise MazeGenerationError("The 42 pattern overlaps a required maze cell.")
