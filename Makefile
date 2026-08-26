.PHONY: install test lint format check clean

install:
	uv sync

test:
	uv run pytest -v --cov=src/pycore

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff format .

check: lint test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache