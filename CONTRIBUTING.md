# Contributing to VideoWise

Thank you for your interest in contributing! This guide will help you set up your development environment and follow our code quality standards.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (IMPORTANT!)

**This is the #1 way to prevent code quality issues:**

```bash
pre-commit install
```

Now, every time you commit, the following checks run automatically:
- ✅ **black** - Code formatting
- ✅ **isort** - Import sorting
- ✅ **flake8** - Linting (including line length checks)
- ✅ **mypy** - Type checking

If any check fails, the commit is blocked until you fix it.

### 3. Verify Setup

```bash
# Run all quality checks manually
make check

# Run tests
pytest -v

# Run tests with coverage
make test
```

## 🛠️ Development Workflow

### Before You Start Coding

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Pull latest changes**
   ```bash
   git pull origin main
   ```

### While Coding

1. **Run checks frequently**
   ```bash
   make check      # Quick quality checks
   make test       # Run full test suite
   ```

2. **Auto-format your code**
   ```bash
   make format     # Runs black and isort
   ```

3. **Write tests for new features**
   - Add tests in `tests/` directory
   - Follow existing test patterns
   - Aim for >90% code coverage

### Before Committing

1. **Ensure all tests pass**
   ```bash
   pytest -v
   ```

2. **Run quality checks**
   ```bash
   make check
   ```

3. **If using pre-commit hooks, just commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks run automatically!
   ```

## 📋 Code Quality Standards

### Line Length
- **Maximum: 100 characters**
- Break long lines using:
  - Parentheses (implicit line continuation)
  - Backslash `\` (explicit continuation)
  - String concatenation with `+`

**Example:**
```python
# Bad (110 characters)
click.echo("This is a very long string that exceeds one hundred characters and will fail flake8 checks")

# Good (split with parentheses)
click.echo(
    "This is a very long string that exceeds one hundred characters "
    "but is now split properly"
)
```

### Import Ordering
- Automatically handled by **isort**
- Standard library imports first
- Third-party imports second
- Local imports last

### Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types
- **mypy** enforces type correctness

### Docstrings
- All public functions must have docstrings
- Use Google-style docstring format
- Include Args, Returns, and Raises sections

**Example:**
```python
def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility with a specific system.
    
    Args:
        video_info: Dictionary containing video metadata
        system: Name of the target system to check
        
    Returns:
        List of compatibility issues found
        
    Raises:
        ValueError: If system name is not recognized
    """
```

## 🧪 Testing Requirements

### Writing Tests

1. **One test file per source file**
   - `videowise/analyzer.py` → `tests/test_analyzer.py`

2. **Test naming convention**
   ```python
   def test_function_name_scenario():
       """Test description of what is being tested."""
   ```

3. **Use fixtures for common setup**
   ```python
   @pytest.fixture
   def sample_video(tmp_path):
       # Setup code
       return video_path
   ```

4. **Aim for comprehensive coverage**
   - Happy path (normal usage)
   - Edge cases (boundary conditions)
   - Error cases (invalid input)

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_check_h264_casparcg_compatible

# Run with coverage report
make test
# or
pytest --cov=videowise --cov-report=html
```

## 🔧 Editor Integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=100",
    "--extend-ignore=E203,W503"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    },
    "editor.rulers": [100]
  },
  "python.linting.mypyEnabled": true,
  "isort.args": ["--profile", "black"]
}
```

### PyCharm

1. **Enable Black formatter:**
   - Settings → Tools → Black
   - Check "On code reformat"
   - Line length: 100

2. **Enable Flake8:**
   - Settings → Tools → External Tools
   - Add flake8 with arguments: `--max-line-length=100 --extend-ignore=E203,W503`

3. **Show line limit:**
   - Settings → Editor → Code Style → Hard wrap at: 100
   - Check "Wrap on typing"

### Vim/Neovim

```vim
" Add to .vimrc
autocmd FileType python set colorcolumn=100
autocmd FileType python set textwidth=100

" Use ALE for linting
let g:ale_linters = {'python': ['flake8', 'mypy']}
let g:ale_python_flake8_options = '--max-line-length=100 --extend-ignore=E203,W503'

" Use black for formatting
autocmd BufWritePre *.py execute ':Black'
```

## 🤖 GitHub Actions CI

Every pull request automatically runs:

1. **Quality checks** (black, isort, flake8, mypy)
2. **Test suite** on multiple Python versions
3. **Coverage report**

Pull requests must pass all checks before merging.

## 📝 Commit Message Guidelines

Use conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

### Types
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `style:` - Code style changes (formatting)

### Examples

```bash
feat: add support for AV1 codec

fix: correct line length violation in cli.py

docs: update installation instructions

test: add edge cases for video analyzer
```

## 🐛 Common Issues & Solutions

### Issue: Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Or run manually
pre-commit run --all-files
```

### Issue: Line too long error

```bash
# Check which lines are too long
flake8 videowise/cli.py --select=E501

# Fix by breaking lines
# Before (bad):
some_function(very_long_argument_one, very_long_argument_two, very_long_argument_three)

# After (good):
some_function(
    very_long_argument_one,
    very_long_argument_two,
    very_long_argument_three,
)
```

### Issue: Import order wrong

```bash
# Auto-fix with isort
isort videowise/ tests/

# Or
make format
```

### Issue: Tests fail after changes

```bash
# Run tests with verbose output to see details
pytest -vv

# Run only failed tests
pytest --lf

# Debug specific test
pytest tests/test_cli.py::test_name -vv -s
```

## 📚 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 🎯 Quick Reference

```bash
# Setup
pre-commit install                  # Install hooks (do this once!)

# Development
make format                         # Auto-format code
make check                          # Run quality checks
make test                           # Run tests with coverage
pytest -v                           # Run tests verbose

# Before committing
make check && pytest -v             # Ensure everything passes
git add . && git commit -m "..."    # Commit (hooks run automatically)

# Manual checks
pre-commit run --all-files          # Run all hooks manually
flake8 videowise/ tests/            # Check linting
black --check videowise/ tests/     # Check formatting
```

## 💡 Pro Tips

1. **Run `make format` before `make check`** - Automatically fixes most formatting issues
2. **Use `pytest -k keyword`** - Run tests matching a keyword
3. **Use `pytest --pdb`** - Drop into debugger on test failure
4. **Run `pre-commit autoupdate`** periodically - Keep hooks up to date
5. **Add `# noqa: E501` to unavoidable long lines** - Rare but sometimes necessary

## ❓ Questions?

Feel free to open an issue for questions about contributing!
