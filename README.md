# VideoWise

> # The current state of this project isn’t working right now. I'm actively working on fixing it, but it might take a little time. Thanks so much for your patience!
> ⚠️ **UNDER DEVELOPMENT**: Core compatibility engine works, but many planned features are still in progress. Expect breaking changes between releases.
>
> ✅ **What Works**: Full CLI, **31 system checkers**, Python API, preset commands, batch processing, enhanced explanations  
> 🚧 **In Progress**: Additional features, PyPI package
>
> 🎉 ** First Phase Refactoring Complete**: Replaced 31 hardcoded checker classes with a rule-based engine! **79% less code, 90% faster to add new systems.** See [REFACTORING.md](REFACTORING.md) for details.

[![CI](https://github.com/KnowOneActual/video-codec-checker/workflows/CI/badge.svg)](https://github.com/KnowOneActual/video-codec-checker/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A video codec compatibility checker that explains *why* your video won't work and how to fix it, for content creators, live production operators, video editors, and developers.

> 💡 **v0.5.0 Released (Feb 19, 2026)**: Professional editing platforms + streaming platforms! Check compatibility with DaVinci Resolve, Premiere Pro, Final Cut Pro, Avid, After Effects, Twitch, YouTube Live, and more. **31 systems now supported!**

## The Problem Being Solved

### For Content Creators & Editors
You've spent hours creating the perfect video, but:
- It won't upload to Instagram or stream to Twitch
- Safari refuses to play it
- Your client says, "The video doesn't work."
- The error message is useless: "Invalid format" or worse, nothing at all
- **You want to understand WHY it doesn't work, not just that it doesn't**

### For Video Editors & Post-Production
You receive footage from clients or cameras and:
- Your NLE (Premiere, DaVinci, Final Cut) stutters during playback
- Multi-cam editing is dropping frames
- You're not sure if you need to transcode or can edit natively
- **You need to know which formats will edit smoothly before importing terabytes of footage**

### For Live Production Operators
You're setting up for a show or stream and:
- Your playback software (CasparCG, vMix, Resolume) refuses to load the video or stutters during live playback
- You're 10 minutes from showtime with last-minute content and need instant compatibility verification
- **You have 50 videos to check before the show starts and need to train your team on what codecs work and why**

Most tools either show you raw technical data (codec, bitrate, profile) or just fail silently. **VideoWise bridges that gap** by explaining compatibility issues in plain English and suggesting actual fixes.

## Quick Start

```bash
# Install
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker
pip install -e .

# Check for specific systems (SIMPLE!)
videowise casparcg video.mp4
videowise instagram video.mp4
videowise resolume video.mp4
videowise twitch stream.mp4

# Check editing platforms
videowise check video.mp4 --system davinciresolve
videowise check footage.mp4 --system premiere
videowise check clip.mov --system finalcut

# Check streaming platforms
videowise check stream.mp4 --system twitch
videowise check video.mp4 --system youtube-live

# Check against ALL 31 systems
videowise check video.mp4

# Learn mode - understand why videos fail
videowise learn video.mp4

# See all available systems
videowise systems

# Batch check directories
videowise casparcg videos/ -r
```

**📚 [Complete CLI Guide](docs/CLI_USAGE.md)** | **💡 [Usage Examples](docs/EXAMPLES.md)** | **🐍 [Python API](docs/API_REFERENCE.md)**

## What VideoWise Does

VideoWise analyzes video files and provides:

- **Human-readable explanations**: "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC."
- **Actionable suggestions**: "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline."
- **Live production warnings**: "This file will cause dropped frames in vMix - bitrate is 180Mbps, but your system can only handle 100Mbps smoothly."
- **Editing workflow advice**: "DNxHD is optimal for DaVinci Resolve multi-layer timelines. H.264 will work but requires re-encoding."
- **Streaming platform guidance**: "Twitch recommends 6Mbps for 1080p60 - this file's 3Mbps may result in quality loss."
- **VJ/Performance advice**: "Convert to DXV or HAP for Resolume - H.264 is CPU-based and limits your layer count."
- **Educational mode**: Use `videowise learn` to understand H.264 profiles, ProRes variants, HAP codec performance, and VFR issues
- **Batch processing**: Check entire directories at once to find which videos need re-encoding before the show or edit session
- **Multi-system validation**: Check against all 31 systems simultaneously (default behavior)

**[See detailed examples and real-world scenarios →](docs/EXAMPLES.md)**

## Installation

### Prerequisites

You need FFmpeg installed:

```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Windows: Download from ffmpeg.org
```

### Install VideoWise

```bash
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker
pip install -e .

# Verify installation
videowise --version
```

## Supported Systems (31 Total)

| Category | Systems | Status |
|----------|---------|--------|
| **Live Production** | CasparCG, PlayoutBee, vMix, OBS Studio, QLab, ProPresenter | ✅ Complete |
| **Church/Theatre Presentation** | Wirecast, Playback Pro, EasyWorship, ProVideoPlayer | ✅ Complete |
| **Media Players & VJ Software** | VLC, Resolume, Mitti, Millumin | ✅ Complete |
| **Browsers** | Safari, Chrome, Firefox | ✅ Complete |
| **Social Media** | Instagram, Twitter/X, YouTube, TikTok, Vimeo, Facebook | ✅ Complete |
| **Video Editing** | DaVinci Resolve, Adobe Premiere Pro, Final Cut Pro, Avid Media Composer, After Effects | ✅ Complete |
| **Streaming Platforms** | Twitch, YouTube Live, Kick, Restream, Zoom, Discord | ✅ Complete |

**[View detailed compatibility matrix →](docs/COMPATIBILITY_MATRIX.md)**

## Architecture & Extensibility

### Rule-Based Engine (Phase 2 Complete!)

VideoWise uses a **rule-based architecture** that makes adding new systems trivial:

- **Before**: 50-200 lines of Python per system (31 classes = 144KB of code)
- **After**: 5-15 lines of YAML per system (79% code reduction)
- **Benefit**: Non-developers can contribute! Just edit YAML, no Python required.

#### Adding a New System (Example)

```yaml
# In videowise/system_profiles.yaml
systems:
  twitch:
    name: "Twitch"
    category: streaming
    codecs:
      supported: [h264]
      optimal: [h264]
    rules:
      - condition: {codec_ne: "h264"}
        level: incompatible
        message: "Twitch only supports H.264 codec"
        suggestion: "Re-encode to H.264 before streaming"
      
      - condition: {bitrate_gt: 8000000}
        level: warning
        message: "Bitrate {bitrate_mbps}Mbps exceeds Twitch's 8Mbps limit"
        suggestion: "Lower bitrate to 6Mbps for 1080p60"
```

That's it! No Python code, no tests to write. The rule engine handles everything.

**[Learn more about the architecture →](REFACTORING.md)**

## Documentation

- **[CLI Usage Guide](docs/CLI_USAGE.md)** - Complete command reference and options
- **[Usage Examples](docs/EXAMPLES.md)** - Real-world workflows and use cases
- **[Python API Reference](docs/API_REFERENCE.md)** - Using VideoWise in your Python code
- **[Compatibility Matrix](docs/COMPATIBILITY_MATRIX.md)** - Detailed system compatibility features
- **[Media Players & VJ Software](docs/MEDIA_PLAYERS_VJ.md)** - In-depth guide for VLC, Resolume, Mitti, Millumin
- **[Editing Platforms](docs/EDITING_PLATFORMS.md)** - Comprehensive guide for DaVinci, Premiere, Final Cut, Avid, After Effects
- **[Architecture Refactoring](REFACTORING.md)** - How we reduced code by 79% and made contributions 10x easier

## Development

- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Testing Guide](TESTING.md)** - Running tests and adding test coverage
- **[Development Setup](DEVELOPMENT.md)** - Setting up your development environment

**Quick development commands:**

```bash
make install-dev    # Install dev dependencies
make test          # Run tests
make format        # Auto-format code
make check         # Run all quality checks
```

## Roadmap

### Current Status (v0.5.0 Released! 🎉)
- ✅ **31 system compatibility checkers** (all production-ready)
- ✅ **386 passing tests** with 100% pass rate
- ✅ **Rule-based architecture** (Phase 2 complete - 79% code reduction)
- ✅ **Preset commands** for instant checks (videowise casparcg, videowise instagram, etc.)
- ✅ **Learn mode** with educational explanations
- ✅ CLI with colored output, batch processing
- ✅ JSON output for automation
- ✅ CI/CD with automated testing
- ✅ Full browser support (Safari, Chrome, Firefox)
- ✅ Complete social media coverage (Instagram, Twitter/X, YouTube, TikTok, Vimeo, Facebook)
- ✅ VJ/media player support (QLab, VLC, Resolume, Mitti, Millumin)
- ✅ Live presentation (Wirecast, Playback Pro, EasyWorship, PlayOutBee, ProVideoPlayer)
- ✅ **Professional editing platforms** (DaVinci Resolve, Premiere Pro, Final Cut Pro, Avid, After Effects)
- ✅ **Streaming platforms** (Twitch, YouTube Live, Kick, Restream, Zoom, Discord)

### Coming Next (Phase 3-4)
- [ ] Migrate remaining 16 systems to rule-based engine
- [ ] CLI integration with rule engine (default to YAML definitions)
- [ ] Additional live production systems (Blackmagic ATEM, Roland V-Series)
- [ ] Media servers (Catalyst, Disguise, Watchout)
- [ ] Auto-generate ffmpeg fix commands
- [ ] Watch folder mode
- [ ] Web interface
- [ ] PyPI package

**[View detailed roadmap →](ROADMAP.md)**

## Contributing

**🎉 Now easier than ever!** With our rule-based architecture, you can contribute without writing Python:

### Add a New System (No Python Required!)

1. Edit `videowise/system_profiles.yaml`
2. Add 5-15 lines of YAML
3. Submit a pull request

That's it! Perfect for:
- **Streamers** wanting to add Twitch/Kick/Discord specs
- **Live operators** who know CasparCG/vMix/OBS quirks
- **Editors** familiar with NLE codec preferences
- **VJs** who understand Resolume/VDMX performance needs

Other ways to contribute:
- **Bug reports** - Something broken? Let us know
- **Feature ideas** - What would make this useful for you?
- **Compatibility data** - Know the quirks of a platform or playback system?
- **Real-world war stories** - "This codec broke my show" or "This footage destroyed my edit" tales help build better checks
- **Documentation improvements** - Clearer explanations always welcome

**Special call for live production operators, video editors, streamers, and VJs:** Your domain knowledge is invaluable.

**[Read the full contributing guide →](CONTRIBUTING.md)**

## Get Involved

- **Have questions?** [Start a discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- **Found a bug?** [Open an issue](https://github.com/KnowOneActual/video-codec-checker/issues)
- **Want to help?** Check out [good first issues](https://github.com/KnowOneActual/video-codec-checker/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
