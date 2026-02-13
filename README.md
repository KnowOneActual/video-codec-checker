# VideoWise

> ⚠️ **UNDER DEVELOPMENT**: This project is under development and is not yet feature-complete. The core compatibility engine works, but many planned features are still in progress. Expect breaking changes between releases.
>
> ✅ **What Works Now**: Basic CLI, 9 system compatibility checkers, Python API
> 🚧 **In Progress**: Batch processing, enhanced output formatting, additional platforms

[![CI](https://github.com/KnowOneActual/video-codec-checker/workflows/CI/badge.svg)](https://github.com/KnowOneActual/video-codec-checker/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A video codec compatibility checker that explains *why* your video won't work and how to fix it, for content creators, live production operators, and developers.

## Quick Start

```bash
# Install
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker
pip install -e .

# Check a video file
videowise check video.mp4 --system casparcg

# Get detailed output
videowise check video.mp4 --system instagram -v

# JSON output for scripting
videowise check video.mp4 --system safari --json
```

**See [CLI Usage Guide](docs/CLI_USAGE.md) for complete documentation.**

## The Problem Being Solved

### For Content Creators & Editors
You've spent hours creating the perfect video, but:
- It won't upload to Instagram
- Safari refuses to play it
- Your client says, "The video doesn't work."
- The error message is useless: "Invalid format" or worse, nothing at all

### For Live Production Operators
You're setting up for a show and:
- Your playback software (CasparCG, vMix, Linux Show Player) refuses to load the video
- The file plays fine on your computer, but stutters during live playback
- Graphics overlays work with some files but not others
- You're 10 minutes from showtime and need to know if you should re-encode NOW
- Client delivers last-minute content, and you need to know instantly if it's compatible

Most tools either show you raw technical data (codec, bitrate, profile) or just fail silently. **VideoWise bridges that gap** by explaining compatibility issues in plain English and suggesting actual fixes.

## What VideoWise Does

VideoWise analyzes video files and provides human-readable explanations:

**For Upload/Playback:**
- "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC."
- "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline."
- "This file is 850MB, but Twitter's limit is 512MB - you'll need to compress it."
- "This MP4 container uses AV1 codec, which isn't widely supported yet - consider H.264 for maximum compatibility."

**For Live Production:**
- "CasparCG 2.3 can't play this - it requires ProRes, DNxHD, or H.264 in MP4 container."
- "This file will cause dropped frames in vMix - bitrate is 180Mbps, but your system can only handle 100Mbps smoothly."
- "QLab performance will suffer with H.264 - convert to ProRes 422 Proxy for smooth scrubbing."
- "ProPresenter works best with HAP codec for GPU-accelerated playback."
- "Warning: Variable frame rate video will cause timing issues in live production - convert to constant frame rate."

## Current Status

✅ **Phase 1 Complete - Phase 2 In Progress**:
- [x] Project structure and test framework
- [x] File validation and error handling
- [x] FFprobe integration for metadata extraction
- [x] Comprehensive codec/container/profile parsing
- [x] Complete compatibility rules engine (9 systems)
- [x] 74 passing tests with 97% code coverage
- [x] ✨ **Basic CLI with colored output**
- [x] JSON output for automation
- [x] CI/CD with GitHub Actions
- [x] Code quality tools (Black, isort, flake8, mypy)
- [x] Pre-commit hooks for automated quality checks
- [ ] Batch processing (check multiple files)
- [ ] `--all` flag (check all systems at once)
- [ ] Enhanced explanation formatter

**Supported Systems:**

| Category | Systems | Status |
|----------|---------|--------|
| **Live Production** | CasparCG, vMix, OBS Studio, QLab, ProPresenter | ✅ Complete |
| **Browsers** | Safari, Chrome | ✅ Complete |
| **Social Media** | Instagram, Twitter/X | ✅ Complete |

## Installation

### Prerequisites

You need FFmpeg installed:

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Install VideoWise

```bash
# Clone the repo
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker

# Install dependencies and package
pip install -r requirements.txt
pip install -e .

# Verify installation
videowise --version

# Run tests (all should pass)
pytest -v
```

## CLI Usage

### Basic Examples

**Check CasparCG compatibility:**
```bash
videowise check sponsor_video.mov --system casparcg
```

Output:
```
Analyzing sponsor_video.mov...

Compatibility Check: CASPARCG
──────────────────────────────────────────────────
✓ Video is compatible with CasparCG 2.3
```

**Check Instagram with verbose output:**
```bash
videowise check promo.mp4 --system instagram -v
```

**JSON output for scripting:**
```bash
videowise check video.mp4 --system safari --json > results.json
```

### Available Systems

- `casparcg` - CasparCG Server
- `vmix` - vMix
- `obs` - OBS Studio
- `qlab` - QLab
- `propresenter` - ProPresenter
- `safari` - Safari browser
- `chrome` - Chrome browser
- `instagram` - Instagram
- `twitter` - Twitter/X

### Exit Codes

- `0`: Compatible (all checks passed)
- `1`: Warnings (may have issues)
- `2`: Incompatible (will not work)

**For complete CLI documentation, see [CLI Usage Guide](docs/CLI_USAGE.md)**

## Python API Usage

You can also use VideoWise as a Python library:

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

# Analyze video file
analyzer = VideoAnalyzer('video.mp4')
video_info = get_video_info(analyzer)

# Check compatibility
issues = check_compatibility(video_info, 'casparcg')

# Process results
for issue in issues:
    print(f"{issue.level.value}: {issue.message}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

## Development

### For Contributors

We use modern Python tooling for code quality and automated testing:

```bash
# One-time setup
make install-dev      # Install dev dependencies
make setup-hooks      # Install pre-commit hooks

# Daily workflow
make format          # Auto-format code (Black + isort)
make test            # Run tests
make check           # Run all quality checks (what CI runs)
```

**All code is automatically checked** on every commit with:
- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

**All code is automatically tested** on every push via GitHub Actions:
- Tests run on Python 3.8, 3.9, 3.10, 3.11, 3.12
- All quality checks must pass
- CLI smoke tests verify basic functionality

**See [TESTING.md](TESTING.md) for a comprehensive testing guide.**
**See [DEVELOPMENT.md](DEVELOPMENT.md) for the complete contributor guide.**

### Quick Development Commands

```bash
make help          # Show all available commands
make test          # Run tests
make test-cov      # Run tests with coverage report
make format        # Auto-format code (Black + isort)
make check         # Check code quality (no modifications)
make lint          # Run linters (flake8, mypy)
make clean         # Remove build artifacts
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_compatibility.py

# Run with coverage report
pytest --cov=videowise --cov-report=html
```

Building this test-first. Every feature has comprehensive tests. **Currently: 74 passing tests with 97% code coverage**

**Note:** Tests generate temporary video files using ffmpeg. If ffmpeg is not available, those tests will be skipped.

**For detailed testing information, see [TESTING.md](TESTING.md)**

### Continuous Integration

Every push triggers automated testing via GitHub Actions:

- **Linting**: Black, isort, flake8, mypy
- **Testing**: Python 3.8-3.12 on Ubuntu
- **CLI Tests**: Verify basic functionality

View status: [Actions tab](https://github.com/KnowOneActual/video-codec-checker/actions)

### Project Structure

```
video-codec-checker/
├── videowise/          # Core package
│   ├── __init__.py
│   ├── analyzer.py     # Video file analysis and metadata extraction
│   ├── compatibility.py # Rules engine (9 systems)
│   ├── utils.py        # Helper functions
│   └── cli.py          # Command-line interface
├── tests/              # Comprehensive test suite
│   ├── conftest.py    # Test fixtures (video generation)
│   ├── test_analyzer.py  # File validation tests
│   ├── test_codec_parsing.py  # Metadata extraction tests
│   ├── test_compatibility.py  # Core system tests
│   ├── test_compatibility_extended.py  # Extended tests
│   └── test_cli.py     # CLI tests
├── examples/           # Example scripts
├── docs/               # Documentation
│   └── CLI_USAGE.md   # Complete CLI guide
├── .github/workflows/  # CI/CD
│   └── ci.yml         # GitHub Actions
├── .pre-commit-config.yaml  # Pre-commit hooks
├── Makefile           # Development commands
├── TESTING.md         # Testing guide
├── DEVELOPMENT.md     # Contributor guide
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Compatibility Features

### Live Production Systems

**CasparCG Server**
- ✅ Codec validation (H.264, ProRes, DNxHD, DNxHR, MPEG-2, MJPEG)
- ✅ Container format recommendations
- ✅ Variable frame rate detection (live timing issues)

**vMix**
- ✅ Bitrate performance warnings (100Mbps, 200Mbps thresholds)
- ✅ 4K resolution hardware requirements
- ✅ ProRes/DNx optimization detection

**OBS Studio**
- ✅ H.264/HEVC/AV1 hardware acceleration detection
- ✅ MKV default format recognition
- ✅ Multi-codec support validation

**QLab**
- ✅ ProRes Proxy/LT optimal performance detection
- ✅ H.264 scrubbing performance warnings
- ✅ ProRes 4444 alpha channel support

**ProPresenter**
- ✅ HAP codec GPU acceleration (best performance)
- ✅ ProRes 4444 transparency support
- ✅ H.264/HEVC compatibility validation

### Browser Compatibility

**Safari**
- ✅ H.264 and HEVC support only
- ✅ VP9 rejection detection
- ✅ MP4 container recommendations

**Chrome**
- ✅ H.264, VP8, VP9, AV1 support
- ✅ Multi-format compatibility

### Social Media Platforms

**Instagram**
- ✅ H.264 Baseline Profile optimization
- ✅ Resolution downscaling warnings (1080p max)
- ✅ Re-encoding quality loss detection
- ✅ Profile-specific recommendations

**Twitter/X**
- ✅ H.264 High Profile recommendations
- ✅ File size limits (512MB standard, 8GB premium)
- ✅ Account tier detection
- ✅ Container format validation

## Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project setup and structure
- [x] Basic file validation
- [x] FFprobe integration
- [x] Parse codec, container, and profile information
- [x] Compatibility rules engine
- [x] Live production systems (CasparCG, vMix, OBS, QLab, ProPresenter)
- [x] Browser compatibility (Safari, Chrome)
- [x] Social media platforms (Instagram, Twitter)
- [x] Comprehensive test coverage (74 tests, 97% coverage)

### Phase 2: User Interface 🚧 IN PROGRESS
- [x] Basic CLI tool for terminal use
- [x] Colored terminal output
- [x] JSON output format
- [x] CI/CD pipeline
- [x] Code quality automation
- [x] Pre-commit hooks
- [ ] `--all` flag (check all systems)
- [ ] Batch processing support (check multiple files)
- [ ] Enhanced explanation formatter
- [ ] Summary reports

### Phase 3: Additional Systems
- [ ] Linux Show Player compatibility
- [ ] Wirecast compatibility
- [ ] Playback Pro compatibility
- [ ] Firefox browser rules
- [ ] TikTok, YouTube platform rules
- [ ] Streaming platforms (Twitch, Vimeo, Restream)
- [ ] Video editor compatibility (Premiere, DaVinci Resolve, Final Cut Pro)

### Phase 4: Advanced Features
- [ ] Provide ffmpeg commands to fix issues
- [ ] Pre-show compatibility checker mode
- [ ] Watch folder mode (auto-check files as they arrive)
- [ ] Export reports (for production documentation)
- [ ] Web interface
- [ ] Package for PyPI (pip install videowise)

**See [ROADMAP.md](ROADMAP.md) for detailed plans.**

## Wanted: Your Input!

**For Content Creators:**
- Which platforms do you upload to? (YouTube, Instagram, Twitter, Vimeo, web browsers?)
- What error messages have you encountered that made no sense?
- What tools do you currently use to check video compatibility?

**For Live Production Operators:**
- What playback systems do you use? (CasparCG, vMix, OBS, Linux Show Player, Wirecast, PlayoutBee?)
- What "this file worked in testing but failed live" stories do you have?
- What codec combinations always cause problems?
- What do you wish you could check BEFORE loading a file into your system?

**For Everyone:**
- What would make this tool actually useful for your workflow?
- Would you use a CLI tool, web interface, or both?

**Open an [issue](https://github.com/KnowOneActual/video-codec-checker/issues)** or **start a [discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)** - your real-world pain points will shape what gets built.

## Contributing

Contributions are welcome! Whether it's:
- **Bug reports** - something broken? Let me know
- **Feature ideas** - what would make this useful?
- **Compatibility data** - know the quirks of a platform or playback system?
- **Real-world war stories** - "this codec broke my show" tales help us build better checks
- **Code contributions** - see [DEVELOPMENT.md](DEVELOPMENT.md)
- **Documentation improvements** - clearer explanations always welcome
- **Test cases** - additional edge cases to cover

This is an open learning project. Questions and "newbie" contributions are encouraged.

**Special call for live production operators:** Your domain knowledge is invaluable. Would like to know what actually breaks in the field.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Why "VideoWise"?

Because understanding *why* your video won't work makes you wiser about video codecs, and wise decisions save you hours of frustration - whether you're uploading to social media or running a live show.
