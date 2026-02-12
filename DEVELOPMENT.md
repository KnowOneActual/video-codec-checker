# Development Guide

Guide for contributing to VideoWise development.

## Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for tests and CLI functionality)
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install-dev

# Install pre-commit hooks
make setup-hooks
```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run tests with verbose output
make test-v

# Run tests with coverage report
make test-cov
```

### Code Quality

**Auto-format code:**
```bash
make format
```

This runs:
- `black` - Code formatter
- `isort` - Import sorter

**Check code (without modifying):**
```bash
make check
```

This runs:
- `black --check` - Format verification
- `isort --check` - Import order verification
- `flake8` - Linting

**Run individual tools:**
```bash
make black    # Format with Black
make isort    # Sort imports
make flake8   # Lint with flake8
make mypy     # Type check with mypy
```

### Pre-commit Hooks

Pre-commit hooks automatically run on `git commit`:

```bash
# Install hooks (one-time setup)
make setup-hooks

# Run hooks manually on all files
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

Hooks that run:
- Black (formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Edit code, add tests, update documentation.

### 3. Format and Test

```bash
# Format code
make format

# Run tests
make test

# Check everything
make check
```

### 4. Commit

```bash
git add .
git commit -m "Brief description of changes"
```

Pre-commit hooks will run automatically.

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Project Structure

```
video-codec-checker/
├── videowise/              # Main package
│   ├── __init__.py
│   ├── analyzer.py         # Video analysis
│   ├── compatibility.py    # Compatibility rules
│   ├── utils.py            # Helper functions
│   └── cli.py              # CLI interface
├── tests/                  # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_analyzer.py
│   ├── test_compatibility.py
│   └── test_cli.py
├── examples/               # Example scripts
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD
├── .pre-commit-config.yaml # Pre-commit hooks
├── pyproject.toml          # Project config
├── Makefile                # Development commands
└── README.md
```

## Adding a New System

1. **Create checker class** in `videowise/compatibility.py`:
   ```python
   class NewSystemChecker(CompatibilityChecker):
       def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
           # Your logic here
           pass
   ```

2. **Register in `check_compatibility()` function**:
   ```python
   checkers = {
       # ... existing systems
       'newsystem': NewSystemChecker,
   }
   ```

3. **Add to CLI choices** in `videowise/cli.py`:
   ```python
   type=click.Choice([
       'casparcg', 'vmix', ..., 'newsystem'
   ])
   ```

4. **Write tests** in `tests/test_compatibility_extended.py`:
   ```python
   def test_newsystem_compatible():
       video_info = {...}
       issues = check_compatibility(video_info, 'newsystem')
       assert len(issues) == 1
       assert issues[0].level == CompatibilityLevel.COMPATIBLE
   ```

5. **Update documentation** in README.md

## Testing Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names: `test_<system>_<scenario>_<expected>`
- Tests should be fast (use minimal test videos)
- Mock external dependencies when possible

## Code Style

- Line length: 100 characters (Black default)
- Use type hints where helpful
- Docstrings for all public functions/classes
- Follow PEP 8 (enforced by flake8)
- Import order: stdlib → third-party → local (enforced by isort)

## Continuous Integration

GitHub Actions runs on all PRs:

1. **Lint Job** - Checks formatting, imports, linting
2. **Test Job** - Runs tests on Python 3.8-3.12
3. **CLI Smoke Test** - Verifies CLI works end-to-end

All must pass before merging.

## Helpful Commands

```bash
# See all available commands
make help

# Clean build artifacts
make clean

# Run specific test file
pytest tests/test_cli.py -v

# Run specific test function
pytest tests/test_cli.py::test_cli_version -v

# Run tests matching pattern
pytest -k "casparcg" -v

# Update pre-commit hooks
pre-commit autoupdate
```

## Getting Help

- Check existing [Issues](https://github.com/KnowOneActual/video-codec-checker/issues)
- Start a [Discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- Read the [README](README.md) and [CLI Usage Guide](docs/CLI_USAGE.md)

## Resources

- [Black documentation](https://black.readthedocs.io/)
- [isort documentation](https://pycqa.github.io/isort/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [pytest documentation](https://docs.pytest.org/)
- [Click documentation](https://click.palletsprojects.com/)
