# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive development tooling and automation
  - Pre-commit hooks for code quality (Black, isort, flake8, mypy)
  - Makefile with common development commands
  - GitHub Actions CI/CD pipeline
  - Automated testing on Python 3.8-3.12
  - DEVELOPMENT.md contributor guide
- Type annotations throughout codebase
- Improved test coverage and organization

### Changed
- Enhanced README with development tools section
- Updated contributor guidelines with modern workflow
- Improved code quality standards

### Fixed
- Removed unused imports from test files
- Fixed mypy type checking errors
- Corrected formatting inconsistencies

### Planned
- `--all` flag (check all systems at once)
- Batch processing support
- Enhanced explanation formatter
- Additional platform support (Firefox, YouTube, TikTok, etc.)

## [0.1.0] - 2026-02-09

### Added - Phase 1: Core Engine Complete

#### Project Foundation
- Initial project structure with Python package layout
- Comprehensive test framework using pytest
- Test fixtures for generating sample videos with ffmpeg
- 45 passing tests with 100% coverage of core features
- Development workflow scripts (start-work.sh)

#### Video Analysis
- `VideoAnalyzer` class for file validation and metadata extraction
- FFprobe integration for reading video properties
- Codec name and profile detection (H.264, ProRes, VP9, AV1, etc.)
- Container format identification (MP4, MOV, MKV, WebM)
- Resolution and frame rate parsing
- Bitrate and file size analysis
- Metadata caching for performance

#### Compatibility Rules Engine
- Extensible `CompatibilityChecker` base class
- Three-level issue system: COMPATIBLE, WARNING, INCOMPATIBLE
- Structured issue reporting with reasons and suggestions

#### Live Production Systems (5 checkers)
- **CasparCG Server**
  - Codec validation (H.264, ProRes, DNxHD, DNxHR, MPEG-2, MJPEG)
  - Container format recommendations by codec
  - Variable frame rate detection for live timing issues
  - Version-specific rules (default 2.3)

- **vMix**
  - Bitrate performance warnings (100Mbps, 200Mbps thresholds)
  - 4K resolution hardware requirement warnings
  - ProRes/DNxHD optimization detection
  - Hardware acceleration notes for H.264

- **OBS Studio**
  - Multi-codec support (H.264, HEVC, AV1, VP8, VP9, ProRes, DNxHD)
  - Hardware acceleration detection for recommended codecs
  - MKV/Matroska default format recognition
  - MP4/MOV compatibility validation

- **QLab**
  - ProRes Proxy/LT optimal performance detection
  - H.264 scrubbing performance warnings
  - ProRes 4444 alpha channel (transparency) support
  - MOV/MP4 container recommendations

- **ProPresenter**
  - HAP codec GPU acceleration (best performance)
  - ProRes 4444 alpha channel support
  - H.264/HEVC/ProRes compatibility validation
  - MOV/MP4 container optimization

#### Browser Compatibility (2 checkers)
- **Safari**
  - H.264 and HEVC-only validation
  - VP9 rejection detection
  - MP4 container recommendations

- **Chrome**
  - Multi-codec support (H.264, VP8, VP9, AV1)
  - Format compatibility validation

#### Social Media Platforms (2 checkers)
- **Instagram**
  - H.264 Baseline Profile optimization
  - Resolution limit warnings (1080p max)
  - Re-encoding quality loss detection
  - Profile-specific recommendations

- **Twitter/X**
  - H.264 High Profile recommendations
  - Tiered file size limits (512MB standard, 8GB premium)
  - Account type detection
  - Container format validation (MP4/MOV)

#### Testing
- `test_analyzer.py` - File validation and metadata extraction (3 tests)
- `test_codec_parsing.py` - Codec/container/profile parsing (10 tests)
- `test_compatibility.py` - Core compatibility checkers (11 tests)
- `test_compatibility_extended.py` - Extended system validation (21 tests)
- Test fixtures for generating H.264, VP9, and other sample videos
- Metadata caching validation

#### Documentation
- Comprehensive README with use cases and examples
- CONTRIBUTING.md with contribution guidelines
- MIT LICENSE
- pytest.ini configuration
- requirements.txt with dependencies

### Changed
- Updated README to reflect Phase 1 completion
- Reorganized project status showing current capabilities

### Fixed
- OBS checker now properly detects Matroska/MKV containers (ffprobe returns 'matroska' not 'mkv')
- ProPresenter checker recognizes all ProRes variants including prores4444
- All .UPPER() typos corrected to .upper() throughout codebase

## [0.0.1] - 2026-02-03

### Added
- Initial repository setup
- Basic project structure
- Placeholder README

[Unreleased]: https://github.com/KnowOneActual/video-codec-checker/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.1.0
[0.0.1]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.0.1
