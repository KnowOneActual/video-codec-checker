.PHONY: help install install-dev test test-v lint format check clean

help:
	@echo "VideoWise Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install package in editable mode"
	@echo "  make install-dev   - Install package with dev dependencies"
	@echo "  make setup-hooks   - Install pre-commit hooks"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests"
	@echo "  make test-v        - Run tests with verbose output"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run all linters (black, isort, flake8, mypy)"
	@echo "  make format        - Auto-format code with black and isort"
	@echo "  make check         - Check code without modifying (CI-style)"
	@echo "  make black         - Run black formatter"
	@echo "  make isort         - Run isort import sorter"
	@echo "  make flake8        - Run flake8 linter"
	@echo "  make mypy          - Run mypy type checker"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove build artifacts and cache files"

install:
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e .

setup-hooks:
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

test:
	export PYTHONPATH=$${PYTHONPATH}:$(shell pwd)/src && pytest

test-v:
	export PYTHONPATH=$${PYTHONPATH}:$(shell pwd)/src && pytest -v

test-cov:
	export PYTHONPATH=$${PYTHONPATH}:$(shell pwd)/src && pytest --cov=videowise --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

black:
	black src tests examples

isort:
	isort src tests examples

flake8:
	flake8 src tests \
		--max-line-length=100 \
		--extend-ignore=E203,W503 \
		--exclude=.git,__pycache__,.venv,.eggs,*.egg,build,dist

mypy:
	mypy src --ignore-missing-imports --no-strict-optional

format: black isort
	@echo "✓ Code formatted"

lint: black isort flake8
	@echo "✓ All linters passed"

check:
	@echo "Running black check..."
	black --check --diff src tests examples
	@echo "Running isort check..."
	isort --check-only --diff src tests examples
	@echo "Running flake8..."
	flake8 src tests \
		--max-line-length=100 \
		--extend-ignore=E203,W503 \
		--exclude=.git,__pycache__,.venv,.eggs,*.egg,build,dist
	@echo "✓ All checks passed"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned build artifacts"
