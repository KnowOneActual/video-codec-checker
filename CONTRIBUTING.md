# Contributing to VideoWise

Thank you for your interest in contributing to VideoWise! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Adding New Systems](#adding-new-systems)
- [Documentation](#documentation)

---

## Code of Conduct

This is an open learning project. Questions and "newbie" contributions are encouraged. Be respectful, helpful, and constructive.

**Expected Behavior:**
- Be welcoming to newcomers
- Be patient with questions
- Provide constructive feedback
- Focus on what's best for the project

---

## How Can I Contribute?

### For Everyone

**Report Bugs:**
- Found something broken? [Open an issue](https://github.com/KnowOneActual/video-codec-checker/issues)
- Include: What you expected vs what happened
- Provide: Video file details (codec, container) if relevant

**Request Features:**
- Have an idea? [Start a discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- Explain: What problem does this solve?
- Describe: How would you use it?

**Improve Documentation:**
- Fix typos, clarify confusing sections
- Add examples from your real-world usage
- Translate documentation (future)

### For Content Creators & Operators

**Share Your Pain Points:**
- Which platforms do you upload to?
- What error messages confused you?
- What codec combinations always cause problems?
- What "worked in testing but failed live" stories do you have?

**Test Compatibility:**
- Try VideoWise with your actual workflow
- Report any incorrect compatibility warnings
- Suggest better error messages

### For Developers

**Add New Systems:**
- Know the codec requirements for a platform?
- See [Adding New Systems](#adding-new-systems) below

**Fix Bugs:**
- Check [good first issues](https://github.com/KnowOneActual/video-codec-checker/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- All PRs need tests

**Improve Code:**
- Performance optimizations
- Better error handling
- Code refactoring

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed and in PATH
- Git

### Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/video-codec-checker.git
cd video-codec-checker

# Add upstream remote
git remote add upstream https://github.com/KnowOneActual/video-codec-checker.git
```

### Install Development Dependencies

```bash
# Install the project in editable mode with dev dependencies
make install-dev

# OR manually:
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
make setup-hooks

# OR manually:
pre-commit install
```

### Verify Setup

```bash
# Run tests
make test

# Should see: 140+ tests passing

# Run code quality checks
make check

# Should see: All checks passing
```

---

## Development Workflow

### Create a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/issue-description
```

### Make Changes

1. **Write code** following [Coding Standards](#coding-standards)
2. **Add tests** for your changes (see [Testing Guidelines](#testing-guidelines))
3. **Update documentation** if needed
4. **Run quality checks** frequently:

```bash
# Auto-format code
make format

# Run tests
make test

# Run all quality checks
make check
```

### Commit Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: Add Firefox compatibility checker"

# Pre-commit hooks will run automatically
# If they fail, fix issues and commit again
```

**Commit Message Format:**

```
type: Short description (50 chars or less)

Longer explanation if needed (wrap at 72 chars).
Explain what and why, not how.

Closes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Open a Pull Request on GitHub
# Fill out the PR template
```

---

## Coding Standards

### Code Style

We use automated tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

**Run all formatters:**
```bash
make format
```

**Check code quality:**
```bash
make check
```

### Python Style Guidelines

**Use type hints:**
```python
# Good
def check_compatibility(video_info: Dict[str, Any], system: str) -> List[Issue]:
    pass

# Bad
def check_compatibility(video_info, system):
    pass
```

**Write docstrings:**
```python
def check_compatibility(video_info: Dict[str, Any], system: str) -> List[Issue]:
    """Check video compatibility with a specific system.
    
    Args:
        video_info: Dictionary containing video metadata
        system: System name to check against
    
    Returns:
        List of compatibility issues (empty if fully compatible)
    
    Raises:
        ValueError: If system is not supported
    """
    pass
```

**Keep functions focused:**
```python
# Good - single responsibility
def extract_codec(metadata: dict) -> str:
    return metadata.get('codec_name', 'unknown')

def extract_bitrate(metadata: dict) -> int:
    return int(metadata.get('bit_rate', 0))

# Bad - doing too much
def extract_everything(metadata: dict) -> dict:
    # 50 lines of extraction logic
    pass
```

### File Organization

```
videowise/
├── analyzer.py          # Video analysis logic
├── compatibility.py     # Compatibility checking engine
├── formatter.py         # Output formatting
├── utils.py            # Utility functions
└── cli.py              # Command-line interface

tests/
├── conftest.py         # Test fixtures
├── test_analyzer.py    # Analyzer tests
├── test_compatibility.py  # Compatibility tests
└── ...
```

---

## Testing Guidelines

### Test Requirements

**Every change must include tests:**
- New features → new tests
- Bug fixes → regression tests
- Code changes → update existing tests

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
pytest tests/test_compatibility.py

# Run specific test
pytest tests/test_compatibility.py::test_casparcg_h264_compatible

# Run with verbose output
pytest -v
```

### Writing Tests

**Use pytest fixtures:**
```python
# conftest.py provides video file fixtures
def test_h264_compatibility(h264_video_file):
    analyzer = VideoAnalyzer(h264_video_file)
    info = get_video_info(analyzer)
    issues = check_compatibility(info, 'casparcg')
    assert not issues  # Should be compatible
```

**Test both success and failure cases:**
```python
def test_casparcg_h264_compatible(h264_video_file):
    """H.264 should be compatible with CasparCG."""
    analyzer = VideoAnalyzer(h264_video_file)
    info = get_video_info(analyzer)
    issues = check_compatibility(info, 'casparcg')
    assert not issues

def test_casparcg_vp9_incompatible(vp9_video_file):
    """VP9 should not be compatible with CasparCG."""
    analyzer = VideoAnalyzer(vp9_video_file)
    info = get_video_info(analyzer)
    issues = check_compatibility(info, 'casparcg')
    assert any(i.level == 'incompatible' for i in issues)
```

**Use descriptive test names:**
```python
# Good
def test_instagram_h264_high_profile_triggers_reencoding_warning():
    pass

# Bad
def test_instagram():
    pass
```

### Test Coverage

We aim for 90%+ code coverage:

```bash
# Generate coverage report
make test-cov

# Open HTML report
open htmlcov/index.html
```

**See [TESTING.md](TESTING.md) for comprehensive testing documentation.**

---

## Submitting Changes

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines (`make check` passes)
- [ ] All tests pass (`make test` succeeds)
- [ ] New code has tests
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains what and why

### PR Description Template

```markdown
## Description
Brief description of changes.

## Motivation
Why is this change needed? What problem does it solve?

## Changes Made
- Added Firefox compatibility checker
- Updated documentation
- Added tests for Firefox detection

## Testing
How was this tested?
- [ ] Added unit tests
- [ ] Tested manually with Firefox browser
- [ ] All existing tests pass

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated Checks:** CI runs tests and code quality checks
2. **Code Review:** Maintainer reviews your code
3. **Feedback:** Address any requested changes
4. **Merge:** Once approved, PR is merged

**Be patient and respectful during review!**

---

## Adding New Systems

Want to add support for a new platform or playback system? Here's how:

### 1. Research Requirements

Gather information:
- What codecs are supported?
- What container formats work?
- Are there profile requirements (H.264 Baseline vs High)?
- Any resolution or bitrate limitations?
- Special considerations (VFR, alpha channel, etc.)?

**Sources:**
- Official documentation
- Developer forums
- Your own testing

### 2. Add Compatibility Rules

Edit `videowise/compatibility.py`:

```python
def check_firefox_compatibility(video_info: Dict[str, Any]) -> List[Issue]:
    """Check Firefox browser compatibility.
    
    Firefox supports:
    - H.264 (all profiles)
    - VP8, VP9
    - AV1 (on supported systems)
    - Theora
    
    Container formats: MP4, WebM, OGG
    """
    issues = []
    codec = video_info.get('codec', '').lower()
    container = video_info.get('container', '').lower()
    
    # Check codec support
    supported_codecs = ['h264', 'vp8', 'vp9', 'av1', 'theora']
    if codec not in supported_codecs:
        issues.append(Issue(
            level='incompatible',
            message=f"{codec.upper()} codec not supported in Firefox",
            reason="Firefox supports H.264, VP8, VP9, AV1, and Theora",
            suggestion="Convert to H.264 for maximum compatibility"
        ))
    
    # Check container format
    supported_containers = ['mp4', 'webm', 'ogg']
    if container not in supported_containers:
        issues.append(Issue(
            level='warning',
            message=f"{container.upper()} container may not work in Firefox",
            reason="Firefox prefers MP4, WebM, or OGG containers",
            suggestion="Use MP4 or WebM container for best compatibility"
        ))
    
    # Add warning for older Firefox versions
    if codec == 'av1':
        issues.append(Issue(
            level='warning',
            message="AV1 requires Firefox 67+",
            reason="Older Firefox versions don't support AV1",
            suggestion="Use H.264 or VP9 for broader compatibility"
        ))
    
    return issues

# Add to SYSTEM_CHECKERS dictionary
SYSTEM_CHECKERS = {
    'casparcg': check_casparcg_compatibility,
    'vmix': check_vmix_compatibility,
    # ... existing systems ...
    'firefox': check_firefox_compatibility,  # Add your system
}
```

### 3. Add Tests

Create tests in `tests/test_compatibility.py`:

```python
class TestFirefoxCompatibility:
    """Test Firefox browser compatibility checks."""
    
    def test_h264_compatible(self, h264_video_file):
        """H.264 should be compatible with Firefox."""
        analyzer = VideoAnalyzer(h264_video_file)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, 'firefox')
        assert not any(i.level == 'incompatible' for i in issues)
    
    def test_vp9_compatible(self, vp9_video_file):
        """VP9 should be compatible with Firefox."""
        analyzer = VideoAnalyzer(vp9_video_file)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, 'firefox')
        assert not any(i.level == 'incompatible' for i in issues)
    
    def test_hevc_incompatible(self, hevc_video_file):
        """HEVC should not be compatible with Firefox."""
        analyzer = VideoAnalyzer(hevc_video_file)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, 'firefox')
        assert any(i.level == 'incompatible' for i in issues)
    
    def test_av1_warning_for_old_versions(self, av1_video_file):
        """AV1 should warn about older Firefox versions."""
        analyzer = VideoAnalyzer(av1_video_file)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, 'firefox')
        assert any('Firefox 67+' in i.message for i in issues)
```

### 4. Update Documentation

Add to `docs/COMPATIBILITY_MATRIX.md`:

```markdown
### Firefox

**Supported Codecs:**
- ✅ H.264 (all profiles)
- ✅ VP8, VP9
- ✅ AV1 (Firefox 67+)
- ✅ Theora
- ❌ HEVC (not supported on most systems)

**Container Formats:**
- ✅ MP4
- ✅ WebM
- ✅ OGG

**Compatibility Checks:**
- ✅ Multi-codec support
- ✅ Version-specific warnings (AV1)
- ✅ Container format recommendations

**What VideoWise Checks:**
```
✅ Video is compatible with Firefox
   Note: H.264 and VP9 have broad support

⚠️  AV1 requires Firefox 67+
   Note: Older Firefox versions don't support AV1
```

**Optimal Settings:**
- VP9 or H.264 for maximum compatibility
- WebM or MP4 container
- AAC or Opus audio
```

### 5. Test Your Changes

```bash
# Run all tests
make test

# Test specifically your new system
pytest tests/test_compatibility.py::TestFirefoxCompatibility -v

# Test the CLI
videowise check test_video.mp4 --system firefox
videowise check test_video.mp4 --all
```

### 6. Submit PR

Create a PR with:
- Compatibility rules implementation
- Comprehensive tests
- Documentation updates
- Example usage in PR description

---

## Documentation

### Types of Documentation

**Code Documentation:**
- Docstrings for all public functions and classes
- Inline comments for complex logic only

**User Documentation:**
- README.md - Project overview
- docs/CLI_USAGE.md - Command-line usage
- docs/EXAMPLES.md - Real-world examples
- docs/API_REFERENCE.md - Python API
- docs/COMPATIBILITY_MATRIX.md - System details

**Developer Documentation:**
- CONTRIBUTING.md (this file)
- TESTING.md - Testing guide
- DEVELOPMENT.md - Development setup
- ROADMAP.md - Future plans

### Documentation Updates

**When to update docs:**
- Adding new features
- Changing CLI behavior
- Adding new systems
- Fixing significant bugs

**Where to update:**
- README.md → Quick Start section
- CLI_USAGE.md → Command examples
- EXAMPLES.md → New workflows
- COMPATIBILITY_MATRIX.md → New systems

---

## Questions?

- **Not sure where to start?** Check [good first issues](https://github.com/KnowOneActual/video-codec-checker/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- **Have a question?** [Start a discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- **Found a bug?** [Open an issue](https://github.com/KnowOneActual/video-codec-checker/issues)

Thank you for contributing to VideoWise! 🎉
