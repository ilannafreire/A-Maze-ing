"""Tests for maze generation, output, configuration, and rendering."""

from pathlib import Path

import pytest

from a_maze_ing import parse_config
from display.ascii_view import _cell_cursor, render_maze
from mazegen.generator import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    MazeGenerationError,
    MazeGenerator,
)
from mazegen.maze_writer import serialize_maze

_WALLS = (NORTH, EAST, SOUTH, WEST)
_MOVES = {
    "N": (0, -1, NORTH),
    "E": (1, 0, EAST),
    "S": (0, 1, SOUTH),
    "W": (-1, 0, WEST),
}


def _make_maze(algorithm: str, perfect: bool = False) -> MazeGenerator:
    """Create a standard seeded maze for behavior tests."""
    return MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=perfect,
        seed=42,
        algorithm=algorithm,
    )


def _degree(maze: MazeGenerator, x: int, y: int) -> int:
    """Count the open sides of one non-blocked cell."""
    return sum(not maze.grid[y][x] & wall for wall in _WALLS)


def _assert_no_open_3x3(maze: MazeGenerator) -> None:
    """Assert that no 3-by-3 group has all internal walls removed."""
    for top in range(maze.height - 2):
        for left in range(maze.width - 2):
            cells = {
                (left + x, top + y)
                for x in range(3)
                for y in range(3)
            }
            if cells & maze.blocked_cells:
                continue
            horizontal_open = all(
                not maze.grid[y][x] & EAST
                for y in range(top, top + 3)
                for x in range(left, left + 2)
            )
            vertical_open = all(
                not maze.grid[y][x] & SOUTH
                for y in range(top, top + 2)
                for x in range(left, left + 3)
            )
            assert not (horizontal_open and vertical_open)


@pytest.mark.parametrize("algorithm", ["bfs", "backtracker"])
def test_seed_reproduces_each_generation_algorithm(algorithm: str) -> None:
    """The same algorithm and seed produce identical wall masks."""
    first = _make_maze(algorithm)
    second = _make_maze(algorithm)

    assert first.grid == second.grid
    assert first.solution == second.solution


@pytest.mark.parametrize("algorithm", ["bfs", "backtracker"])
def test_perfect_mode_is_a_connected_tree(algorithm: str) -> None:
    """Perfect mode has one open edge per usable cell after the first."""
    maze = _make_maze(algorithm, perfect=True)
    degrees = [
        _degree(maze, x, y)
        for y in range(maze.height)
        for x in range(maze.width)
        if (x, y) not in maze.blocked_cells
    ]
    edge_count = sum(degrees) // 2
    vertex_count = len(degrees)

    assert edge_count == vertex_count - 1
    assert maze.solution
    assert maze.has_42
    assert all(maze.grid[y][x] == 15 for x, y in maze.blocked_cells)


@pytest.mark.parametrize("algorithm", ["bfs", "backtracker"])
def test_braiding_bonus_and_loops(algorithm: str) -> None:
    """Default mode removes dead ends and avoids open 3-by-3 areas."""
    maze = _make_maze(algorithm)
    degrees = [
        _degree(maze, x, y)
        for y in range(maze.height)
        for x in range(maze.width)
        if (x, y) not in maze.blocked_cells
    ]
    edge_count = sum(degrees) // 2

    assert min(degrees) >= 2
    assert edge_count - len(degrees) + 1 >= 2
    assert (maze.width // 2, maze.height // 2) not in maze.blocked_cells
    _assert_no_open_3x3(maze)


def test_shared_walls_are_encoded_consistently() -> None:
    """Every pair of neighboring cells agrees on its shared wall."""
    maze = _make_maze("backtracker")
    for y, row in enumerate(maze.grid):
        for x, walls in enumerate(row):
            if x + 1 < maze.width:
                assert bool(walls & EAST) == bool(maze.grid[y][x + 1] & WEST)
            if y + 1 < maze.height:
                assert bool(walls & SOUTH) == bool(maze.grid[y + 1][x] & NORTH)


def test_solution_steps_follow_open_walls_to_exit() -> None:
    """The shortest path uses open walls and avoids closed 42 cells."""
    maze = _make_maze("bfs")
    x, y = maze.entry
    for step in maze.solution:
        dx, dy, wall = _MOVES[step]
        assert not maze.grid[y][x] & wall
        x += dx
        y += dy
        assert (x, y) not in maze.blocked_cells
    assert (x, y) == maze.exit


def test_output_format_has_hex_rows_and_three_trailer_lines() -> None:
    """Output rows and path metadata follow the required format."""
    maze = _make_maze("backtracker")
    output = serialize_maze(maze)
    rows, trailer = output.rstrip("\n").split("\n\n")
    trailer_lines = trailer.splitlines()

    assert len(rows.splitlines()) == maze.height
    assert all(len(row) == maze.width for row in rows.splitlines())
    assert all(
        character in "0123456789ABCDEF"
        for character in rows.replace("\n", "")
    )
    assert trailer_lines == [
        "0,0",
        "19,14",
        "".join(maze.solution),
    ]
    assert output.endswith("\n")


def test_config_parser_reads_required_and_optional_values(
    tmp_path: Path,
) -> None:
    """The parser accepts comments and optional reproducibility settings."""
    config_path = tmp_path / "config.txt"
    config_path.write_text(
        "# test config\n"
        "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
        "OUTPUT_FILE=maze.txt\nPERFECT=False\nSEED=42\nALGORITHM=bfs\n",
        encoding="utf-8",
    )

    config = parse_config(config_path)

    assert config.width == 20
    assert config.entry == (0, 0)
    assert config.seed == 42
    assert config.algorithm == "bfs"
    assert config.perfect is False


def test_config_parser_rejects_missing_keys(tmp_path: Path) -> None:
    """Missing mandatory settings produce a clear validation error."""
    config_path = tmp_path / "config.txt"
    config_path.write_text("WIDTH=10\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing configuration keys"):
        parse_config(config_path)


def test_generator_rejects_invalid_dimensions_and_algorithm() -> None:
    """Impossible dimensions and unsupported algorithms are rejected."""
    with pytest.raises(MazeGenerationError, match="must be positive"):
        MazeGenerator(0, 5, (0, 0), (0, 4))
    with pytest.raises(MazeGenerationError, match="Algorithm"):
        MazeGenerator(5, 5, (0, 0), (4, 4), algorithm="prim")


def test_single_column_perfect_maze_is_supported() -> None:
    """A valid one-column perfect maze is not rejected unnecessarily."""
    maze = MazeGenerator(1, 5, (0, 0), (0, 4), perfect=True, seed=7)

    assert len(maze.solution) == 4


def test_ascii_renderer_shows_route_and_42_without_player_marker() -> None:
    """The renderer shows the route and solid 42 cells, without an @ marker."""
    maze = _make_maze("backtracker")
    rendered = render_maze(maze, use_color=False)

    assert " E " in rendered
    assert " X " in rendered
    assert "███" in rendered
    assert " * " in rendered
    assert " @ " not in rendered

    without_path = render_maze(maze, show_path=False, use_color=False)
    assert " * " not in without_path


def test_animation_cursor_matches_four_character_cell_width() -> None:
    """The route cursor aligns with each four-column maze cell."""
    assert _cell_cursor((3, 2)) == "\033[6;14H"


def test_small_maze_can_omit_42() -> None:
    """A maze too small for the pattern remains usable."""
    maze = MazeGenerator(
        8, 6, (0, 0), (7, 5), perfect=True, seed=7
    )

    assert not maze.has_42
    assert maze.solution
