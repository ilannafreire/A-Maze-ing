"""Write maze data in the subject's hexadecimal text format."""

from pathlib import Path

from mazegen.generator import MazeGenerator


def serialize_maze(maze: MazeGenerator) -> str:
    """Return the maze and its solution in the required output format."""
    rows = [
        "".join(f"{walls:X}" for walls in row)
        for row in maze.grid
    ]
    rows.extend(
        (
            "",
            f"{maze.entry[0]},{maze.entry[1]}",
            f"{maze.exit[0]},{maze.exit[1]}",
            "".join(maze.solution),
        )
    )
    return "\n".join(rows) + "\n"


def write_maze(output_file: str | Path, maze: MazeGenerator) -> None:
    """Write a generated maze using UTF-8 and Unix line endings."""
    path = Path(output_file)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(serialize_maze(maze))
