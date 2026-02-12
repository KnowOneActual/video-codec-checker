# Testing Guide for VideoWise

A comprehensive, easy-to-follow guide for testing VideoWise. Whether you're a contributor or just want to verify everything works, this guide has you covered.

## Table of Contents

- [Quick Start](#quick-start)
- [Understanding the Tests](#understanding-the-tests)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)

## Quick Start

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run with coverage:**
```bash
pytest --cov=videowise --cov-report=html
open htmlcov/index.html  # View coverage report
```

That's it! If all tests pass, you're good to go. ✅

## Understanding the Tests

### What Gets Tested

VideoWise has **55+ tests** covering:

1. **File Validation** (`test_analyzer.py`)
   - Does the file exist?
   - Can we read it?
   - Does it handle errors gracefully?

2. **Metadata Extraction** (`test_codec_parsing.py`)
   - Can we detect the codec (H.264, VP9, ProRes)?
   - Can we read the container format (MP4, MOV, WebM)?
   - Can we parse resolution, frame rate, bitrate?

3. **Compatibility Rules** (`test_compatibility.py`)
   - Does CasparCG reject VP9?
   - Does vMix warn about high bitrates?
   - Does Instagram prefer H.264 Baseline?

4. **Extended System Tests** (`test_compatibility_extended.py`)
   - All 9 systems (CasparCG, vMix, OBS, QLab, ProPresenter, Safari, Chrome, Instagram, Twitter)
   - Edge cases and special scenarios

5. **CLI Functionality** (`test_cli.py`)
   - Does the command-line tool work?
   - Does it produce correct output?
   - Do exit codes work properly?

### Test Fixtures

Tests use **generated test videos** instead of checking in large binary files:

```python
# From conftest.py - automatically generates test videos
@pytest.fixture
def h264_video(test_videos_dir, ffmpeg_available):
    """Generate a minimal H.264 MP4 test video."""
    # Creates a 1-second blue test video
    # Located in temporary directory
    # Cleaned up after tests
```

**Why?**
- No large binary files in git
- Tests work the same on all systems
- Can generate any codec/format we need

**Requirement:** Tests need `ffmpeg` installed. If not available, those tests are skipped automatically.

## Running Tests

### Basic Test Commands

**Run everything:**
```bash
make test
# or
pytest
```

**Run with details:**
```bash
pytest -v
```

Output:
```
tests/test_analyzer.py::test_analyzer_rejects_nonexistent_file PASSED
tests/test_analyzer.py::test_analyzer_accepts_existing_file PASSED
tests/test_compatibility.py::test_casparcg_h264_compatible PASSED
... (55 tests)
```

**Run a specific test file:**
```bash
pytest tests/test_compatibility.py
```

**Run a specific test:**
```bash
pytest tests/test_compatibility.py::test_casparcg_h264_compatible
```

**Run tests matching a pattern:**
```bash
pytest -k "casparcg"  # Only CasparCG tests
pytest -k "h264"      # Only H.264 tests
```

### Coverage Reports

**Generate HTML coverage report:**
```bash
make test-cov
# or
pytest --cov=videowise --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see:
- Which lines are tested
- Which branches are covered
- What percentage of code is tested

**Quick terminal coverage:**
```bash
pytest --cov=videowise --cov-report=term
```

Output:
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
videowise/__init__.py            2      0   100%
videowise/analyzer.py           47      2    96%
videowise/compatibility.py     312      8    97%
-------------------------------------------------
TOTAL                          361     10    97%
```

### Fast Testing During Development

**Skip slow tests (video generation):**
```bash
pytest -m "not slow"
```

**Only run failed tests:**
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first, then others
```

**Stop on first failure:**
```bash
pytest -x
```

**Run tests in parallel (faster):**
```bash
pip install pytest-xdist
pytest -n auto  # Uses all CPU cores
```

## Test Structure

### Test Organization

```
tests/
├── conftest.py                      # Test fixtures (shared setup)
│   ├── ffmpeg_available()          # Check if ffmpeg installed
│   ├── test_videos_dir()           # Temp directory for videos
│   ├── h264_video()                # Generate H.264 test video
│   ├── h264_high_profile_video()   # Generate H.264 High Profile
│   └── vp9_video()                 # Generate VP9 test video
│
├── test_analyzer.py                 # 3 tests - File validation
│   ├── test_analyzer_rejects_nonexistent_file
│   ├── test_analyzer_accepts_existing_file
│   └── test_get_metadata_returns_none_for_invalid_video
│
├── test_codec_parsing.py            # 10 tests - Metadata extraction
│   ├── test_get_codec_name_h264
│   ├── test_get_codec_profile_baseline
│   ├── test_get_container_format_mp4
│   ├── test_get_resolution
│   └── ... (more parsing tests)
│
├── test_compatibility.py            # 11 tests - Core compatibility
│   ├── test_casparcg_h264_compatible
│   ├── test_casparcg_vp9_incompatible
│   ├── test_vmix_high_bitrate_warning
│   └── ... (more system tests)
│
├── test_compatibility_extended.py   # 21 tests - Extended validation
│   ├── test_obs_h264_compatible
│   ├── test_qlab_prores_proxy_optimal
│   ├── test_instagram_h264_baseline_optimal
│   └── ... (all 9 systems)
│
└── test_cli.py                      # 10 tests - CLI functionality
    ├── test_cli_version
    ├── test_check_command_help
    ├── test_check_h264_casparcg_compatible
    └── ... (more CLI tests)
```

### Anatomy of a Test

```python
def test_casparcg_h264_compatible():
    """Test that H.264 in MP4 is compatible with CasparCG."""
    
    # 1. ARRANGE - Set up test data
    checker = CasparCGChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    
    # 2. ACT - Run the code being tested
    issues = checker.check(video_info)
    
    # 3. ASSERT - Check the results
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
```

**Every test follows this pattern:**
1. **Arrange** - Create test data
2. **Act** - Call the function
3. **Assert** - Verify the result

## Writing Tests

### Adding a New Test

**Example: Test that vMix warns about 8K video**

```python
# In tests/test_compatibility.py

def test_vmix_8k_warning():
    """Test that 8K resolution triggers hardware warning."""
    checker = VmixChecker()
    video_info = {
        "codec": "h264",
        "resolution": (7680, 4320),  # 8K
    }
    
    issues = checker.check(video_info)
    
    # Should have warning about resolution
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("8k" in issue.message.lower() for issue in issues)
```

**Run your new test:**
```bash
pytest tests/test_compatibility.py::test_vmix_8k_warning -v
```

### Using Test Fixtures

Fixtures provide reusable test data:

```python
def test_get_codec_name_h264(h264_video):
    """Test that we can extract H.264 codec name."""
    # h264_video is automatically created by the fixture
    # It's a Path object pointing to a real H.264 video file
    
    analyzer = VideoAnalyzer(str(h264_video))
    codec = analyzer.get_codec_name()
    
    assert codec == "h264"
```

**Available fixtures:**
- `h264_video` - Basic H.264 Baseline Profile
- `h264_high_profile_video` - H.264 High Profile
- `vp9_video` - VP9 in WebM
- `test_videos_dir` - Temporary directory for videos
- `ffmpeg_available` - Boolean, True if ffmpeg installed

### Testing CLI Commands

```python
from click.testing import CliRunner
from videowise.cli import cli

def test_check_h264_casparcg_compatible(runner, h264_video):
    """Test check command with compatible H.264 file for CasparCG."""
    result = runner.invoke(cli, ["check", str(h264_video), "--system", "casparcg"])
    
    # Check exit code
    assert result.exit_code in [0, 1]  # 0=compatible, 1=warning
    
    # Check output contains expected text
    assert "CasparCG" in result.output or "casparcg" in result.output.lower()
```

## Troubleshooting

### Tests Are Skipped

**Problem:**
```
tests/test_codec_parsing.py::test_get_codec_name_h264 SKIPPED
```

**Cause:** FFmpeg is not installed.

**Solution:**
```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

### Tests Fail on Video Generation

**Problem:**
```
E   FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:** Install ffmpeg (see above) or skip those tests:
```bash
pytest -m "not ffmpeg"
```

### Import Errors

**Problem:**
```
E   ModuleNotFoundError: No module named 'videowise'
```

**Solution:** Install the package in editable mode:
```bash
pip install -e .
```

### Tests Pass Locally But Fail in CI

**Check:**
1. Did you commit all changes?
   ```bash
   git status
   ```

2. Are there formatting issues?
   ```bash
   make check
   ```

3. Do tests work in a clean environment?
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate
   pip install -r requirements.txt
   pip install -e .
   pytest
   ```

### Slow Test Performance

**Problem:** Tests take a long time.

**Solutions:**

1. **Run in parallel:**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

2. **Skip video generation tests:**
   ```bash
   pytest -k "not video"
   ```

3. **Run only what you're working on:**
   ```bash
   pytest tests/test_compatibility.py::test_casparcg_h264_compatible
   ```

## Best Practices

### Before Committing

```bash
# 1. Format code
make format

# 2. Run all checks (what CI runs)
make check

# 3. Run all tests
make test
```

Or use pre-commit hooks to automate this:
```bash
make setup-hooks
```

Now every `git commit` automatically runs checks!

### Test-Driven Development (TDD)

1. **Write test first** (it will fail)
   ```python
   def test_new_feature():
       result = new_function()
       assert result == "expected"
   ```

2. **Run test** (confirms it fails)
   ```bash
   pytest tests/test_new.py::test_new_feature
   ```

3. **Write code** to make it pass
   ```python
   def new_function():
       return "expected"
   ```

4. **Run test again** (should pass now)
   ```bash
   pytest tests/test_new.py::test_new_feature
   ```

5. **Refactor** if needed

### What to Test

✅ **DO test:**
- Public API functions
- Edge cases (empty input, very large files, unusual codecs)
- Error handling
- Different input combinations

❌ **DON'T test:**
- Third-party libraries (they have their own tests)
- Simple getters/setters with no logic
- Obvious code (e.g., `return True` when function always returns True)

## Continuous Integration

### What Runs on Every Push

GitHub Actions automatically runs:

1. **Linting**
   - Black (code formatting)
   - isort (import sorting)
   - flake8 (style checking)
   - mypy (type checking)

2. **Testing**
   - All 55+ tests
   - On Python 3.8, 3.9, 3.10, 3.11, 3.12
   - On Ubuntu Linux

3. **CLI Smoke Tests**
   - Verify `videowise --version` works
   - Verify `videowise --help` works

### Viewing CI Results

1. Go to [Actions tab](https://github.com/KnowOneActual/video-codec-checker/actions)
2. Click on your commit
3. View results for each job

**Green checkmark** ✅ = All tests passed!  
**Red X** ❌ = Something failed (click for details)

## Need Help?

- **Tests confusing?** Open an [issue](https://github.com/KnowOneActual/video-codec-checker/issues)
- **Want to add tests?** See [DEVELOPMENT.md](DEVELOPMENT.md)
- **Found a bug?** Write a test that reproduces it, then fix it!

## Summary

**Quick reference:**

```bash
# Run all tests
pytest

# Run with details
pytest -v

# Run specific test
pytest tests/test_compatibility.py::test_casparcg_h264_compatible

# Run with coverage
pytest --cov=videowise --cov-report=html

# Run what CI runs
make check
make test
```

**That's it!** Testing should be straightforward. If it's not, that's a bug in the documentation—please let us know!
