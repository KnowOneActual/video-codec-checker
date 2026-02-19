# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- TBD - Phase 4 planning in progress

## [0.5.0] - 2026-02-19

### Added

#### Phase 3.4: Professional Editing Platforms ✅ COMPLETE

**All 364 tests passing (100%)** ✅

**5 New Professional Editing Platform Checkers:**

- **DaVinciResolveChecker** - Professional editing and color grading software
  - BRAW (Blackmagic RAW) native format detection and workflow guidance
  - DNxHD/DNxHR optimal codec detection with quality level recommendations
  - ProRes support with platform-specific hardware acceleration detection:
    - Apple Silicon (M1/M2/M3/M4) hardware encode/decode
    - Intel Mac native support without hardware acceleration
    - Windows software decode with performance notes
  - 10-bit color depth detection for ProRes 422 HQ and 4444 variants
  - H.264/H.265 decode support with GPU acceleration (Studio only)
  - Re-encoding warnings for heavy editing and color grading workflows
  - Free vs Studio version feature detection
  - Container compatibility (MOV, MXF, MP4)
  - AV1 support in Studio 18.5+
  - Performance optimization suggestions for 4K+ timelines

- **AdobePremiereProChecker** - Industry-standard editing software
  - Native codec support (ProRes, DNxHD/DNxHR)
  - RED RAW (R3D) native workflow support with Lumetri color controls
  - XAVC (Sony camera format) native support
  - Mercury Playback Engine GPU acceleration detection and recommendations
  - VFR (Variable Frame Rate) detection with sync issue warnings
  - High bitrate 4K warnings (>100 Mbps performance impact)
  - H.264 Level 5.1 validation for UHD/4K delivery
  - Proxy workflow recommendations for 8K footage
  - Dynamic Link compatibility notes with After Effects
  - Multi-cam editing codec recommendations
  - Platform-specific ProRes guidance (Mac vs Windows licensing)

- **FinalCutProChecker** - Mac-only professional editing software
  - ProRes native codec with Apple Silicon hardware acceleration
  - ProRes RAW native workflow support
  - Optimized Media workflow detection for H.264/HEVC
  - Background rendering recommendations for 4K/high-bitrate footage
  - Hardware decode detection for H.264/HEVC on Apple Silicon
  - MOV (QuickTime) native container preference
  - Magnetic Timeline codec optimization (ProRes 422)
  - Proxy media workflow for 4K+ editing on laptops
  - iPhone/iPad footage optimization (HEVC in MOV)
  - DNxHD/DNxHR support with ProRes conversion recommendations

- **AvidMediaComposerChecker** - Broadcast industry standard NLE
  - DNxHD/DNxHR native codec optimal performance detection
  - MXF container requirement for broadcast workflows
  - OP1a MXF structure detection for MediaCentral collaboration
  - ProRes collaboration workflow (AMA linking with Final Cut Pro)
  - H.264 AMA linking with transcoding recommendations
  - Avid codec pack requirements for third-party formats (XAVC)
  - PCM audio broadcast compliance detection
  - MOV container warnings with MXF rewrap suggestions
  - Frame rate conformity validation for project lock
  - DNxHD resolution limit detection (HD only, suggest DNxHR for 4K+)

- **AfterEffectsChecker** - Motion graphics and compositing software
  - ProRes 4444 with alpha channel detection (optimal for motion graphics)
  - Animation Codec (QuickTime Animation/qtrle) lossless alpha support
  - PNG/TIFF sequence recommendations for motion graphics workflows
  - H.264/HEVC warnings (avoid for intermediate renders)
  - Alpha channel preservation validation (warn if codec doesn't support alpha)
  - RAM preview codec optimization guidance
  - Dynamic Link compatibility notes with Premiere Pro
  - GPU acceleration recommendations for 4K+ compositions
  - Multi-Frame Rendering suggestions for performance
  - Workflow-specific guidance (motion_graphics vs vfx)

#### Phase 3.3: Streaming Platforms ✅ COMPLETE

**6 New Streaming Platform Checkers:**

- **TwitchChecker** - Live streaming platform
  - Resolution and bitrate recommendations (720p30-1080p60)
  - Bitrate limits (6Mbps for 1080p60, 4.5Mbps for 1080p30)
  - H.264 codec requirement with High Profile support
  - Keyframe interval recommendations (2 seconds)
  - Audio codec requirements (AAC-LC, 128-160kbps)
  - Partner/Affiliate transcoding availability notes

- **YouTubeLiveChecker** - Live streaming on YouTube
  - Resolution-based bitrate recommendations (1.5-9Mbps for 720p-1080p60)
  - H.264 High Profile optimal, Main Profile acceptable
  - Variable bitrate (VBR) with 1.5x multiplier for max bitrate
  - Keyframe interval (2-4 seconds)
  - AAC audio codec recommendations (128-256kbps)
  - Latency mode optimization (Normal, Low, Ultra Low)

- **KickChecker** - Emerging streaming platform
  - H.264 High Profile codec requirement
  - Similar bitrate recommendations to Twitch (4.5-6Mbps)
  - Keyframe interval validation (2 seconds)
  - AAC audio codec support
  - Growing platform with Twitch-like requirements

- **RestreamChecker** - Multi-streaming service
  - Conservative bitrate recommendations for multi-platform streaming
  - H.264 High Profile codec requirement
  - Platform-agnostic optimization (works with all streaming services)
  - Automatic transcoding and distribution features
  - Keyframe interval recommendations

- **ZoomChecker** - Video conferencing platform
  - Conservative bitrate recommendations for conferencing (1-3Mbps)
  - H.264 codec with Baseline/Main Profile support
  - Screen sharing resolution recommendations (720p-1080p)
  - Webcam streaming guidance (360p-720p)
  - Cloud recording format validation

- **DiscordChecker** - Community voice/video platform
  - Nitro vs non-Nitro quality tier detection
  - Resolution limits (720p30 standard, 1080p60 with Nitro)
  - Bitrate limits (2.5Mbps standard, 8Mbps with Nitro)
  - H.264 codec requirement
  - Screen sharing and Go Live streaming guidance
  - Audio codec recommendations (Opus preferred)

#### Testing & Quality
- **364 total tests, all passing (100%)** ✅
  - Professional editing platforms: 50 tests
  - Streaming platforms: 30 tests
  - Advanced playout systems: 40 tests
  - All other test suites: 244 tests
- 100% pass rate across all Python versions (3.8-3.12)
- Full linting compliance (black, isort, flake8)
- Comprehensive test coverage for all 31 systems

#### Documentation
- New `docs/EDITING_PLATFORMS.md` - Comprehensive 25KB guide for all 5 editing platforms
- New `docs/STREAMING_PLATFORMS.md` - Complete guide for all 6 streaming platforms
- Updated README.md with 31 systems and v0.5.0 status
- Updated ROADMAP.md marking Phase 3 complete
- Updated CLI_USAGE.md with new system examples

#### Module Structure
- New `videowise/editing_platforms.py` module (35KB)
- New `videowise/streaming_checkers.py` module (20KB)
- Enhanced `videowise/advanced_playout.py` module
- Complete integration into compatibility registry
- Platform-specific parameter support throughout

### Changed

**System Count Milestones:**
- **Phase 3.3:** 23 → 29 systems (26% increase) - Added 6 streaming platforms
- **Phase 3.4:** 29 → 31 systems (6.9% increase) - Added 5 editing platforms  
  _(Note: System counts overlap as both phases were developed in parallel)_
- **Overall Phase 3:** 23 → 31 systems (35% increase)
- **Project Total:** 9 (Phase 1) → 31 systems (244% increase)

**Test Suite Evolution:**
- Phase 1: 45 tests
- Phase 2: 274 tests
- Phase 3 (v0.5.0): 364 tests (90 new tests)
- All tests passing with 100% pass rate

**Enhanced Compatibility Registry:**
- Dynamic imports for editing and streaming platforms
- Graceful degradation for optional modules
- Improved error handling throughout
- Platform-specific initialization parameters

### Fixed
- All linting issues resolved (E501 line lengths, unused imports)
- Python string method typo: `.UPPER()` → `.upper()` throughout codebase
- Test assertions updated for new checker behaviors
- Black formatter compliance across all modules
- All 364 tests passing on Python 3.8-3.12

## [0.3.0] - 2026-02-15

### Added - Phase 2 Complete (13 New Systems)

#### Browsers
- Firefox - H.264, VP8, VP9, AV1 support

#### Social Media  
- YouTube - H.264 High Profile optimal, upload optimization
- TikTok - H.264 in MP4/MOV, vertical video support
- Vimeo - H.264 in MP4/MOV, high-quality uploads
- Facebook - H.264 in MP4/MOV, 4GB file size limit

#### Live Production
- PlayoutBee - HAP optimal, Raspberry Pi guidance

#### Church/Theatre Presentation
- Wirecast - H.264/ProRes, streaming optimization
- Playback Pro - ProRes 422 optimal, MOV required
- EasyWorship - Native EW7+ support, H.264 in MP4/MOV

#### Media Players & VJ Software
- VLC - Universal codec support via FFmpeg
- Resolume - DXV/HAP GPU codecs optimal
- Mitti - ProRes/HAP optimal, Apple Silicon
- Millumin - HAP for multi-projector, projection mapping

#### Documentation
- New `docs/MEDIA_PLAYERS_VJ.md` (16KB guide)

#### Testing
- 160+ tests (up from 45)
- 94% code coverage

## [0.2.0] - 2026-02-12

### Added - Core CLI & System Expansion

#### CLI Commands
- `batch` command for directory processing
- `learn` command for educational mode
- `systems` command for listing platforms
- Preset commands (casparcg, instagram, etc.)
- `--all` flag for multi-system checking
- `--explain` flag for detailed explanations
- `--no-color` flag for plain text output
- JSON output support

#### New System Checkers
- Enhanced CasparCG, vMix, OBS Studio
- QLab, ProPresenter
- Safari, Chrome
- Instagram, Twitter/X

## [0.1.0] - 2026-02-09

### Added - Phase 1: Core Engine

#### Project Foundation
- Initial project structure
- Comprehensive test framework
- 45 passing tests with 100% coverage

#### Video Analysis
- VideoAnalyzer class
- FFprobe integration
- Codec/container detection
- Metadata extraction and caching

#### Compatibility Rules Engine
- CompatibilityChecker base class
- Three-level issue system (COMPATIBLE, WARNING, INCOMPATIBLE)
- Structured issue reporting

#### Initial System Checkers (9)
- Live Production: CasparCG, vMix, OBS Studio, QLab, ProPresenter
- Browsers: Safari, Chrome
- Social Media: Instagram, Twitter/X

[Unreleased]: https://github.com/KnowOneActual/video-codec-checker/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.5.0
[0.3.0]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.3.0
[0.2.0]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.2.0
[0.1.0]: https://github.com/KnowOneActual/video-codec-checker/releases/tag/v0.1.0
