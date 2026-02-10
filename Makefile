.PHONY: help install run test lint format ci clean

help:
	@echo "Available targets:"
	@echo "  install  - Install dependencies"
	@echo "  run      - Run the application"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linting and type checking"
	@echo "  format   - Format code"
	@echo "  ci       - Run full CI suite (lint + test)"
	@echo "  clean    - Remove cache files"

install:
	uv sync

run:
	uv run python -m football_club

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff check --fix .
	uv run ruff format .

ci: lint test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
