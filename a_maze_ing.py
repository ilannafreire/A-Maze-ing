"""Command-line interface for the A-Maze-ing project."""

from dataclasses import dataclass, replace
from pathlib import Path
import sys
from typing import Sequence

from display.ascii_view import animate_solution, render_maze
from mazegen.generator import MazeGenerationError, MazeGenerator
from mazegen.maze_writer import write_maze

_REQUIRED_KEYS = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
}
_OPTIONAL_KEYS = {"SEED", "ALGORITHM"}
_WALL_COLORS = (
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "gray",
)


@dataclass(frozen=True)
class MazeConfig:
    """Validated options loaded from a maze configuration file."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "backtracker"


def _parse_coordinate(value: str, key: str) -> tuple[int, int]:
    """Parse a coordinate written as ``x,y``."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key} must use the format x,y.")
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError as error:
        message = f"{key} must contain two integer coordinates."
        raise ValueError(message) from error


def parse_config(config_file: str | Path) -> MazeConfig:
    """Read and validate the required key-value configuration file."""
    values: dict[str, str] = {}
    path = Path(config_file)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        message = f"Cannot read configuration file '{path}': {error}"
        raise ValueError(message) from error

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.count("=") != 1:
            message = f"Invalid configuration syntax on line {line_number}."
            raise ValueError(message)
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.upper()
        if key not in _REQUIRED_KEYS | _OPTIONAL_KEYS:
            raise ValueError(f"Unknown configuration key '{key}'.")
        if key in values:
            raise ValueError(f"Configuration key '{key}' is repeated.")
        if not value:
            raise ValueError(
                f"Configuration value for '{key}' cannot be empty."
            )
        values[key] = value

    missing = sorted(_REQUIRED_KEYS - values.keys())
    if missing:
        missing_keys = ", ".join(missing)
        raise ValueError(f"Missing configuration keys: {missing_keys}.")

    try:
        width = int(values["WIDTH"])
        height = int(values["HEIGHT"])
        seed = int(values["SEED"]) if "SEED" in values else None
    except ValueError as error:
        message = "WIDTH, HEIGHT, and SEED must be integers."
        raise ValueError(message) from error

    perfect_value = values["PERFECT"].lower()
    if perfect_value not in {"true", "false"}:
        raise ValueError("PERFECT must be True or False.")
    algorithm = values.get("ALGORITHM", "backtracker").lower()
    if algorithm not in {"bfs", "backtracker"}:
        raise ValueError("ALGORITHM must be bfs or backtracker.")

    return MazeConfig(
        width=width,
        height=height,
        entry=_parse_coordinate(values["ENTRY"], "ENTRY"),
        exit=_parse_coordinate(values["EXIT"], "EXIT"),
        output_file=values["OUTPUT_FILE"],
        perfect=perfect_value == "true",
        seed=seed,
        algorithm=algorithm,
    )


def _generate(config: MazeConfig) -> MazeGenerator:
    """Create and persist a maze for the given configuration."""
    maze = MazeGenerator(
        config.width,
        config.height,
        config.entry,
        config.exit,
        perfect=config.perfect,
        seed=config.seed,
        algorithm=config.algorithm,
    )
    write_maze(config.output_file, maze)
    return maze


def _draw_maze(maze: MazeGenerator, show_path: bool, color: str) -> None:
    """Clear the old drawing before showing the current maze state."""
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    print(render_maze(maze, show_path=show_path, color=color))


def _print_menu() -> None:
    """Display the four terminal menu options."""
    print(
        "\n--- A-Maze-ing Menu ---\n"
        "1. Re-generate a new maze\n"
        "2. Show/Hide shortest path\n"
        "3. Change wall colors\n"
        "4. Quit"
    )


def _interact(config: MazeConfig, maze: MazeGenerator) -> None:
    """Display the maze and handle the required terminal interactions."""
    show_path = True
    color = "magenta"
    current_config = config
    if not maze.has_42:
        print("The maze is too small for the 42 pattern.")
    if not animate_solution(maze, color):
        _draw_maze(maze, show_path, color)
    _print_menu()

    while True:
        try:
            command = input("Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command == "4":
            return
        if command == "2":
            show_path = not show_path
            if show_path:
                if not animate_solution(maze, color):
                    _draw_maze(maze, show_path, color)
            else:
                _draw_maze(maze, show_path, color)
            _print_menu()
        elif command == "3":
            print("Available wall colors:")
            for index, wall_color in enumerate(_WALL_COLORS, start=1):
                print(f"{index}. {wall_color.replace('_', ' ').title()}")
            try:
                color_choice = input(
                    f"Color (1-{len(_WALL_COLORS)}, 0 to cancel): "
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if color_choice == "0":
                continue
            if (
                color_choice.isdigit()
                and 1 <= int(color_choice) <= len(_WALL_COLORS)
            ):
                color = _WALL_COLORS[int(color_choice) - 1]
                _draw_maze(maze, show_path, color)
                _print_menu()
            else:
                print("Choose a listed color number.")
        elif command == "1":
            next_seed = (current_config.seed or 0) + 1
            current_config = replace(current_config, seed=next_seed)
            maze = _generate(current_config)
            if not maze.has_42:
                print("The maze is too small for the 42 pattern.")
            show_path = True
            if not animate_solution(maze, color):
                _draw_maze(maze, show_path, color)
            _print_menu()
        elif command:
            print("Choose an option from 1 to 4.")
            _print_menu()


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the command-line application and report expected errors cleanly."""
    args = list(sys.argv[1:] if arguments is None else arguments)
    if len(args) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 2
    try:
        config = parse_config(args[0])
        maze = _generate(config)
        print(f"Maze written to {config.output_file}.")
        _interact(config, maze)
    except (MazeGenerationError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
