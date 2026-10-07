*This project has been created as part of the 42 curriculum by <dassunca>, <ifreire>.*

# A-Maze-ing

## Description

A-Maze-ing generates a connected maze from a text configuration file, finds a
shortest route between its entry and exit, writes the maze in hexadecimal wall
format, and displays it in the terminal. It supports perfect mazes and braided
boards, a visible closed-cell 42 pattern when the dimensions allow it, and two
reproducible generation algorithms.

The reusable `mazegen` package exposes `MazeGenerator` from
`mazegen.generator`. Tree carving, braiding, the 42 pattern, grid operations,
validation, and shortest-path search live in focused modules. The package has
no third-party runtime dependencies.

## Instructions

Python 3.10 or later is required. Install the project and development tools with
`make install`. Run the default configuration with `make run`, or run a chosen
configuration directly:

```text
python3 a_maze_ing.py config.txt
```

The shortest route is traced in place when the program starts and when shown
again; each valid route cell is highlighted without redrawing the maze.
The terminal menu accepts `1` to generate another maze, `2` to show or hide
the highlighted route, `3` to change wall color, and `4` to quit.
`make test`, `make lint`, and `make lint-strict` run the tests and quality
checks. Build the reusable wheel and copy it to the repository root with:

```text
make package
```

The generated `mazegen_a_maze_ing-1.0.0-py3-none-any.whl` at the repository
root can be installed with pip. The source package and its documentation remain
in `mazegen/generator.py`.

### Configuration

Each non-comment line in the configuration file is one `KEY=VALUE` pair.
Lines beginning with `#` and blank lines are ignored. The six required keys
are:

| Key | Meaning | Example |
| --- | --- | --- |
| `WIDTH` | Number of cells per row | `WIDTH=20` |
| `HEIGHT` | Number of rows | `HEIGHT=15` |
| `ENTRY` | Entry coordinate, `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit coordinate, `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Generated maze output path | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether the maze must have one unique route | `PERFECT=True` |

Optional keys are `SEED`, an integer used for reproducible generation, and
`ALGORITHM`, either `bfs` or `backtracker`. Coordinates are zero-based. The
grid dimensions must be positive, and entry and exit must be distinct usable
cells. A perfect one-column or one-row maze is valid. The non-perfect mode also
needs enough usable cells to form two independent loops. The 42 pattern needs
at least 13 columns and 9 rows; it is omitted for smaller grids with a console
notice.

### Generation and Output

Both generation algorithms create a spanning tree over all usable cells.
`bfs` uses a randomized breadth-first frontier; `backtracker` uses iterative
depth-first search with backtracking. A seed makes either result reproducible.
The default is `backtracker`: its iterative depth-first traversal tends to make
longer winding corridors and avoids recursion depth limits. `bfs` remains
available as an alternative that is easy to inspect level by level.

When `PERFECT=True`, the spanning tree is retained, so every pair of usable
cells has exactly one route. In the default non-perfect mode, braiding is a
separate post-processing step: it opens additional safe walls to create at
least two independent loops and remove dead ends. It rejects any opening that
would create a fully open 3-by-3 area. The generator reports an error if the
requested constraints cannot be met. The 42 pattern is made of fully closed
cells and is excluded from the traversable graph. In non-perfect mode, its
placement keeps the center cell free for the Pac-Man-style player start.

The output contains one uppercase hexadecimal wall mask per cell, one row per
line. Bits 0 through 3 represent north, east, south, and west; a set bit means
that wall is closed. After a blank line, the file contains the entry coordinate,
exit coordinate, and shortest path direction string on separate lines.

### Reusable Generator

The public generator class is in `mazegen/generator.py`. The BFS and
backtracker algorithms are in `mazegen/carving.py`; output serialization and
file writing are in `mazegen/maze_writer.py`. Install the built wheel, then
import and use the generator:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
		width=20,
		height=15,
		entry=(0, 0),
		exit=(19, 14),
		perfect=False,
		seed=42,
		algorithm="backtracker",
)

grid = maze.grid
solution = maze.solution
```

`grid[y][x]` contains each cell's wall mask. `solution` is a list of `N`, `E`,
`S`, and `W` steps. `maze.shortest_path()` can calculate the solution again
after the grid is changed.

## Resources

- Python documentation: https://docs.python.org/3/
- Breadth-first search: https://en.wikipedia.org/wiki/Breadth-first_search
- Depth-first search: https://en.wikipedia.org/wiki/Depth-first_search
- Python packaging: https://packaging.python.org/
- The project subject: `amazeing.pdf`

AI assistance was used to diagnose flake8 and mypy findings, review tests, and draft project
documentation. The project authors are responsible for understanding, testing,
and reviewing all submitted work.

## Team and Project Management

- Team members: Ilanna Freire (login: ifreire) and Daniel Assunção (login: dassunca).
- Roles and responsibilities were divided between the generation engine and
	the application and delivery work:
	- Ilanna Freire: grid operations and validation, BFS/backtracker carving,
		braiding, the 42 pattern, the reusable generator API, shortest-path
		solving, and tests for generation rules.
	- Daniel Assunção: configuration parsing and CLI, terminal rendering and
		interactions, output serialization, maze analysis, packaging, and
		integration tests.
- Planning and changes: the work was organized around two connected tracks:
	building a reusable generation engine and integrating it into the terminal
	application. The initial scope covered configuration, maze generation,
	shortest-path output, and display. The delivered scope also includes two
	generation algorithms, reproducible seeds, the 42 pattern, braided boards,
	interactive path/color controls, an installable wheel, and automated checks.
- Retrospective: separating generation from the CLI made the generator
	importable and testable on its own. Fixed seeds, automated tests, and the
	analyzer made maze behavior repeatable to check. Further improvements include
	tests for interactive CLI flows and analyzer input errors, plus stricter type
	checking of the test suite.
- Tools used: Python 3, Make, pytest, flake8, mypy, setuptools/build, pip, Git,
	the supplied `maze_analyzer.py`, and AI assistance for diagnosing checks, reviewing tests, and drafting docs.