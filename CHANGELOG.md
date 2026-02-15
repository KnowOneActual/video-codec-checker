# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Phase 2.5: Media Players & VJ Software (NEW!)
- **VLCChecker** - Universal media player support
  - Universal codec support via FFmpeg libraries (H.264, HEVC, VP9, AV1, ProRes, DNxHD, and hundreds more)
  - Hardware acceleration recommendations for modern codecs (H.264, HEVC, VP9, AV1)
  - Extreme bitrate performance warnings (>300 Mbps)
  - 8K resolution performance considerations
  - Cross-platform support (Windows, macOS, Linux)
  - 5 comprehensive tests covering codec universality, hardware acceleration, and performance

- **ResolumeChecker** - VJ software for concerts and festivals
  - DXV codec family optimal detection (DXV, DXV2, DXV3 - Resolume proprietary GPU codec)
  - HAP codec family full support (HAP, HAP Alpha, HAP Q, HAP Q Alpha)
  - CPU vs GPU codec performance analysis (H.264/HEVC/ProRes CPU-based warnings)
  - Platform-specific guidance (Mac vs Windows for ProRes)
  - 4K layer count considerations and warnings
  - High bitrate impact on layer count (>200 Mbps warnings)
  - MOV container requirement for DXV/HAP
  - Conversion recommendations for optimal performance
  - 5 comprehensive tests covering DXV, HAP, H.264, ProRes, and platform-specific scenarios

- **MittiChecker** - Mac-only professional playback for theatre and corporate events
  - ProRes optimal on Apple Silicon detection (M1/M2/M3 hardware acceleration)
  - HAP optimal for multi-output setups
  - Built-in transcoding workflow recommendations
  - H.264/HEVC transcoding suggestions
  - 4K codec selection guidance (HAP for GPU, ProRes for SDI)
  - High bitrate performance warnings (>250 Mbps)
  - NDI and ATEM integration notes
  - MOV container preference detection
  - 5 comprehensive tests covering ProRes, HAP, H.264, transcoding, and Apple Silicon optimization

- **MilluminChecker** - Mac-only video mapping and projection software
  - QuickTime and AVFoundation codec support
  - HAP optimal for multi-projector setups
  - ProRes excellent with Apple Silicon hardware acceleration
  - H.264/HEVC compatibility with performance notes
  - 4K projection performance considerations
  - Multi-projector GPU path optimization
  - Interactive installation workflow support
  - MOV container preference
  - 5 comprehensive tests covering HAP, ProRes, H.264, QuickTime, and projection mapping scenarios

- **Comprehensive Documentation**
  - New `docs/MEDIA_PLAYERS_VJ.md` - 16KB comprehensive guide covering all 4 new systems
  - Detailed codec recommendations for each system
  - Real-world use cases (VJ work, theatre, projection mapping, installations)
  - Performance tiers and optimization strategies
  - Hardware requirements and platform notes
  - Integration notes (NDI, ATEM, Syphon, DMX, Art-Net)
  - Codec decision tree and quick reference guide
  - Comparison table across all 4 systems
  - Converting to DXV/HAP workflow examples
  - When to use each system guidance

- **Updated Documentation**
  - Updated README.md to reflect 22 total systems (from 9)
  - Added "Media Players & VJ Software" category to supported systems table
  - Updated Phase 2 completion status (160+ tests, 94% coverage)
  - Added link to new MEDIA_PLAYERS_VJ.md guide in Documentation section
  - Updated roadmap to reflect Phase 2.5 completion

#### Phase 2.4: Enhanced Explanation System
- **Enhanced Explanation System** - Educational codec knowledge for beginners and experts
  - New `--explain` flag provides extended explanations for compatibility issues
  - Codec-specific knowledge base covering H.264 profiles, VP9, ProRes variants, HAP, VFR, and bitrate considerations
  - Severity level guide explaining Compatible, Warning, and Incompatible statuses
  - Context-aware explanations that adapt to the system being checked
  - Educational content about H.264 profiles (Baseline, Main, High)
  - VP9 compatibility explanations for browsers and live production
  - ProRes variant details (Proxy/LT for performance, 4444 for alpha channels)
  - HAP codec GPU acceleration information
  - Bitrate performance impact explanations
  - Variable Frame Rate (VFR) vs Constant Frame Rate (CFR) guidance
  - Instagram-specific encoding recommendations
  - 12 comprehensive tests for explanation functionality in test_cli_explain.py
  - Complete ExplanationFormatter class with extensible knowledge system

#### Phase 2.3: Batch Processing
- **Plain Text Output Mode** - CI/CD and logging-friendly output
  - New `--no-color` flag disables ANSI color codes for plain text output
  - Compatible with CI/CD pipelines, log files, and text processing tools
  - Works with both `check` and `batch` commands
  - Works with `--explain` flag for educational output without colors
  - Automatically detected and tested in test suite
- Enhanced formatter infrastructure
  - ExplanationFormatter class with color support and explain mode
  - Severity information system with icons, colors, and descriptions
  - System-specific summary formatting
  - Codec knowledge database for context-aware explanations
  - get_severity_info() helper function for accessing severity metadata
- **Batch Processing Feature** - Check multiple files and directories at once
  - New `batch` command for processing multiple files or directories
  - Recursive directory scanning with `--recursive` flag
  - File extension filtering with `--extensions` option (default: .mp4,.mov,.avi,.mkv,.m4v,.webm,.flv,.wmv,.mpg,.mpeg,.m2v,.mxf)
  - Batch summary statistics showing total files, compatible, warnings, and incompatible counts
  - JSON output format for batch results with file-by-file details
  - `find_video_files()` helper function for video file discovery
  - Support for checking multiple specific files: `videowise batch file1.mp4 file2.mov`
  - Support for directory scanning: `videowise batch /path/to/videos/`
  - Support for recursive scanning: `videowise batch /media/ --recursive`
  - Exit code reflects worst-case across all processed files
  - Continue-on-error support (default behavior) for robust batch processing
  - Verbose mode (`-v`) for detailed processing information
  - Compatible with both `--system` and `--all` flags
  - Now supports `--explain` and `--no-color` flags for batch operations
  - 27 comprehensive tests for batch functionality
  - Complete batch processing documentation in CLI_USAGE.md
  - Examples for pre-show checklists, media library validation, CI/CD integration

#### Phase 2.2: Multi-System Checking
- **CLI Enhancement: `--all` flag** for checking video compatibility against all supported systems at once
  - Batch compatibility checking across all 22 systems
  - Summary view categorizing systems as Compatible, Warnings, or Incompatible
  - JSON output support with multi-system results structure
  - Verbose mode compatibility for detailed multi-system analysis
  - Exit code based on worst-case scenario across all systems
  - Individual system results with clear separation and headers
  - Now supports `--explain` flag for educational multi-system analysis
  - Now supports `--no-color` flag for plain text multi-system output
  - 12 comprehensive tests covering all `--all` flag functionality
  - Complete documentation in CLI_USAGE.md with examples
  - Validation to prevent simultaneous `--system` and `--all` usage

#### Testing & Quality
- Comprehensive test suite with 94% code coverage
  - **160+ total tests** across 9 test files covering all major functionality
  - Tests for all **22 platform compatibility checkers**
  - Batch processing tests (27 tests in test_batch.py)
  - Explanation system tests (12 tests in test_cli_explain.py)
  - Formatter tests (18 tests in test_formatter.py)
  - Error handling and edge case tests
  - CLI command and output format tests
  - Video metadata parsing and analyzer tests
- Comprehensive development tooling and automation
  - Pre-commit hooks for code quality (Black, isort, flake8, mypy)
  - Makefile with common development commands
  - GitHub Actions CI/CD pipeline
  - Automated testing on Python 3.8-3.12
  - DEVELOPMENT.md contributor guide
  - TESTING.md comprehensive testing guide
- Type annotations throughout codebase

### Changed
- **System Count Milestone: 9 → 22 systems** (144% increase)
  - Live Production: CasparCG, PlayoutBee, vMix, OBS Studio, QLab, ProPresenter (6)
  - Church/Theatre: Wirecast, Playback Pro, EasyWorship (3)
  - Media Players & VJ Software: VLC, Resolume, Mitti, Millumin (4)
  - Browsers: Safari, Chrome, Firefox (3)
  - Social Media: Instagram, Twitter/X, YouTube, TikTok, Vimeo, Facebook (6)
- Improved test infrastructure with proper fixtures and mocking
- Enhanced test fixtures with directory creation helpers for batch tests
- Simplified pre-commit hooks to focus on code quality (removed whitespace/newline fixers that conflicted with editors)
- Enhanced README with batch processing examples and use cases
- Updated README with `--explain` and `--no-color` flag examples
- Updated CLI_USAGE.md with comprehensive explanation flag documentation
- Updated contributor guidelines with modern workflow
- Improved code quality standards
- Updated project status from 'ACTIVE DEVELOPMENT' to 'UNDER DEVELOPMENT' for accuracy
- Improved frame rate parsing in analyzer.py for better accuracy
- Enhanced CLI help text formatting for better readability
- Updated CLI help text to mention both `--all` flag and `batch` command options
- Updated CLI help text for `--explain` and `--no-color` flags
- Updated ROADMAP.md to mark Phase 2.3 Batch Operations as COMPLETE
- Updated ROADMAP.md to mark Phase 2.4 Enhanced Explanations as COMPLETE
- Updated ROADMAP.md to mark Phase 2.5 Media Players & VJ Software as COMPLETE
- Updated TESTING.md with batch processing and explanation test documentation
- Enhanced formatter output with better structure and clarity

### Fixed
- Fixed mypy type checking errors with `no-any-return` annotations
- Fixed mypy type checking errors with explicit type annotations in CLI loops
- Fixed Python 3.8 compatibility by downgrading pre-commit to 2.x
- Fixed CI workflow to accept warning exit codes (exit code 1) as success
- Fixed CI smoke test test video filename from `test_video.mp4` to `testvideo.mp4` for consistency
- Fixed CI smoke test JSON output step to properly handle warning exit codes
- Fixed Black formatter issues in test files (trailing whitespace, line formatting)
- Fixed flake8 line length violations in formatter.py
- Fixed unused import in test_formatter.py
- All CI jobs now passing: lint, test (Python 3.8-3.12), and cli-smoke-test
- All tests now passing across Python 3.8-3.12
- Removed unused imports from test files
- Corrected formatting inconsistencies
- Fixed frame rate parsing to correctly handle fractional frame rates
- Fixed test assertions to match updated analyzer behavior

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
