# Install the project and development tools in the active Python environment.
install:
	python3 -m pip install -e ".[dev]"

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

test:
	python3 -m pytest

package:
	python3 -m build --wheel
	cp dist/mazegen_a_maze_ing-*.whl .

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info
	rm -f mazegen_*.whl

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug test package clean lint lint-strict
