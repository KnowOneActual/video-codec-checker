# VideoWise

> ⚠️ **UNDER DEVELOPMENT**: Core compatibility engine works, but many planned features are still in progress. Expect breaking changes between releases.
>
> ✅ **What Works**: Full CLI, **22 system checkers**, Python API, `--all` flag, batch processing, enhanced explanations  
> 🚧 **In Progress**: Additional platforms, advanced features

[![CI](https://github.com/KnowOneActual/video-codec-checker/workflows/CI/badge.svg)](https://github.com/KnowOneActual/video-codec-checker/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A video codec compatibility checker that explains *why* your video won't work and how to fix it, for content creators, live production operators, and developers.

## The Problem Being Solved

### For Content Creators & Editors
You've spent hours creating the perfect video, but:
- It won't upload to Instagram
- Safari refuses to play it
- Your client says, "The video doesn't work."
- The error message is useless: "Invalid format" or worse, nothing at all
- **You want to understand WHY it doesn't work, not just that it doesn't**

### For Live Production Operators
You're setting up for a show and:
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

# Check a single video
videowise check video.mp4 --system casparcg

# Check against ALL 22 systems
videowise check video.mp4 --all

# Get extended explanations (great for learning!)
videowise check video.mp4 --system resolume --explain

# Process multiple files or directories
videowise batch videos/ --recursive --all
```

**📚 [Complete CLI Guide](docs/CLI_USAGE.md)** | **💡 [Usage Examples](docs/EXAMPLES.md)** | **🐍 [Python API](docs/API_REFERENCE.md)**

## What VideoWise Does

VideoWise analyzes video files and provides:

- **Human-readable explanations**: "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC."
- **Actionable suggestions**: "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline."
- **Live production warnings**: "This file will cause dropped frames in vMix - bitrate is 180Mbps, but your system can only handle 100Mbps smoothly."
- **VJ/Performance advice**: "Convert to DXV or HAP for Resolume - H.264 is CPU-based and limits your layer count."
- **Educational mode**: Use `--explain` flag to learn about H.264 profiles, ProRes variants, HAP codec performance, and VFR issues
- **Batch processing**: Check entire directories at once to find which videos need re-encoding before the show
- **Multi-system validation**: Use `--all` flag to check against all 22 systems simultaneously

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

## Supported Systems (22 Total)

| Category | Systems | Status |
|----------|---------|--------|
| **Live Production** | CasparCG, PlayoutBee, vMix, OBS Studio, QLab, ProPresenter | ✅ Complete |
| **Church/Theatre Presentation** | Wirecast, Playback Pro, EasyWorship | ✅ Complete |
| **Media Players & VJ Software** | VLC, Resolume, Mitti, Millumin | ✅ Complete |
| **Browsers** | Safari, Chrome, Firefox | ✅ Complete |
| **Social Media** | Instagram, Twitter/X, YouTube, TikTok, Vimeo, Facebook | ✅ Complete |

**[View detailed compatibility matrix →](docs/COMPATIBILITY_MATRIX.md)**

## Documentation

- **[CLI Usage Guide](docs/CLI_USAGE.md)** - Complete command reference and options
- **[Usage Examples](docs/EXAMPLES.md)** - Real-world workflows and use cases
- **[Python API Reference](docs/API_REFERENCE.md)** - Using VideoWise in your Python code
- **[Compatibility Matrix](docs/COMPATIBILITY_MATRIX.md)** - Detailed system compatibility features
- **[Media Players & VJ Software](docs/MEDIA_PLAYERS_VJ.md)** - In-depth guide for VLC, Resolume, Mitti, Millumin

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

### Current Status (Phase 2 Complete! 🎉)
- ✅ **22 system compatibility checkers** with 160+ passing tests (94% coverage)
- ✅ CLI with colored output, `--all` flag, batch processing
- ✅ Educational mode with `--explain` flag
- ✅ JSON output for automation
- ✅ CI/CD with automated testing
- ✅ Full browser support (Safari, Chrome, Firefox)
- ✅ Complete social media coverage (Instagram, Twitter/X, YouTube, TikTok, Vimeo, Facebook)
- ✅ VJ/media player support (VLC, Resolume, Mitti, Millumin)
- ✅ Church/theatre presentation (Wirecast, Playback Pro, EasyWorship)

### Coming Next (Phase 3)
- [ ] Streaming platforms (Twitch, Restream, Zoom)
- [ ] Additional live production (Blackmagic ATEM, Roland V-Series)
- [ ] Video editing software (DaVinci Resolve, Adobe Premiere)
- [ ] Media servers (Catalyst, Disguise, Watchout)

### Future (Phase 4)
- [ ] Auto-generate ffmpeg fix commands
- [ ] Watch folder mode
- [ ] Web interface
- [ ] PyPI package

**[View detailed roadmap →](ROADMAP.md)**

## Contributing

Contributions are welcome! We're especially looking for:
- **Bug reports** - Something broken? Let us know
- **Feature ideas** - What would make this useful for you?
- **Compatibility data** - Know the quirks of a platform or playback system?
- **Real-world war stories** - "This codec broke my show" tales help us build better checks
- **Documentation improvements** - Clearer explanations always welcome

**Special call for live production operators and VJs:** Your domain knowledge is invaluable.

**[Read the full contributing guide →](CONTRIBUTING.md)**

## Get Involved

- **Have questions?** [Start a discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- **Found a bug?** [Open an issue](https://github.com/KnowOneActual/video-codec-checker/issues)
- **Want to help?** Check out [good first issues](https://github.com/KnowOneActual/video-codec-checker/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
