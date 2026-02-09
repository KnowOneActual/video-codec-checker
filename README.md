# VideoWise

> ⚠️ **This project is in early stages of development.** Core compatibility engine complete - now building user interface.

A video codec compatibility checker that explains *why* your video won't work and how to fix it - for content creators, live production operators, and developers.

## The Problem We're Solving

### For Content Creators & Editors
You've spent hours creating the perfect video, but:
- It won't upload to Instagram
- Safari refuses to play it
- Your client says "the video doesn't work"
- The error message is useless: "Invalid format" or worse, nothing at all

### For Live Production Operators
You're setting up for a show and:
- Your playback software (CasparCG, vMix, Linux Show Player) refuses to load the video
- The file plays fine on your computer but stutters during live playback
- Graphics overlays work with some files but not others
- You're 10 minutes from showtime and need to know if you should re-encode NOW
- Client delivers last-minute content and you need to know instantly if it's compatible

Most tools either show you raw technical data (codec, bitrate, profile) or just fail silently. **VideoWise bridges that gap** by explaining compatibility issues in plain English and suggesting actual fixes.

## What We're Building

VideoWise analyzes video files and provides human-readable explanations:

**For Upload/Playback:**
- "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC"
- "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline"
- "This file is 850MB but Twitter's limit is 512MB - you'll need to compress it"
- "This MP4 container uses AV1 codec which isn't widely supported yet - consider H.264 for maximum compatibility"

**For Live Production:**
- "CasparCG 2.3 can't play this - it requires ProRes, DNxHD, or H.264 in MP4 container"
- "This file will cause dropped frames in vMix - bitrate is 180Mbps but your system can only handle 100Mbps smoothly"
- "QLab performance will suffer with H.264 - convert to ProRes 422 Proxy for smooth scrubbing"
- "ProPresenter works best with HAP codec for GPU-accelerated playback"
- "Warning: Variable frame rate video will cause timing issues in live production - convert to constant frame rate"

## Current Status

✅ **Core Engine Complete** - We have:
- [x] Project structure and test framework
- [x] File validation and error handling
- [x] FFprobe integration for metadata extraction
- [x] Comprehensive codec/container/profile parsing
- [x] Complete compatibility rules engine (9 systems)
- [x] 45 passing tests covering all features
- [ ] CLI interface (next up!)
- [ ] Human-readable explanation formatter

**Supported Systems (All Functional):**

| Category | Systems | Coverage |
|----------|---------|----------|
| **Live Production** | CasparCG, vMix, OBS Studio, QLab, ProPresenter | ✅ Complete |
| **Browsers** | Safari, Chrome | ✅ Complete |
| **Social Media** | Instagram, Twitter/X | ✅ Complete |

**What Works Right Now:**
```python
from videowise.compatibility import check_compatibility
from videowise.analyzer import VideoAnalyzer

analyzer = VideoAnalyzer('video.mp4')
video_info = analyzer.get_video_info()
issues = check_compatibility(video_info, 'casparcg')

for issue in issues:
    print(f"{issue.level.value}: {issue.message}")
```

## We Want Your Input!

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

**Open an [issue](https://github.com/KnowOneActual/video-codec-checker/issues)** or **start a [discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)** - your real-world pain points will shape what we build.

## Installation (For Developers)

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

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup (all 45 should pass)
pytest -v
```

## Development

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

We're building this test-first - every feature has comprehensive tests. **Currently: 45 passing tests**

**Note:** Tests generate temporary video files using ffmpeg. If ffmpeg is not available, those tests will be skipped.

### Project Structure

```
video-codec-checker/
├── videowise/          # Core package
│   ├── __init__.py
│   ├── analyzer.py     # Video file analysis and metadata extraction
│   ├── compatibility.py # Rules engine (9 systems, 45 tests)
│   └── explainer.py    # Human-readable output (coming soon)
├── tests/              # Comprehensive test suite
│   ├── conftest.py    # Test fixtures (video generation)
│   ├── test_analyzer.py  # File validation tests
│   ├── test_codec_parsing.py  # Metadata extraction tests
│   ├── test_compatibility.py  # Core system tests
│   └── test_compatibility_extended.py  # Extended system tests
├── requirements.txt
├── pytest.ini
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
- ✅ VP9 rejection (your exact use case!)
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
- [x] Comprehensive test coverage (45 tests)

### Phase 2: User Interface (Current Focus)
- [ ] CLI tool for terminal use
- [ ] Human-readable explanation formatter
- [ ] Batch processing support (check entire playlists)
- [ ] Colored output for better readability
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

## Use Cases (Coming Soon with CLI)

### Pre-Show Verification
```bash
videowise check video.mov --system casparcg
# Returns: ✓ Compatible with CasparCG 2.3
#          ProRes codec in MOV container

videowise check sponsor.mp4 --system qlab
# Returns: ⚠ Warning: H.264 performs poorly when scrubbing
#          Suggestion: Convert to ProRes 422 Proxy for better performance
```

### Upload Preparation
```bash
videowise check video.mp4 --system instagram
# Returns: ⚠ File will be re-encoded by Instagram (quality loss)
#          Reason: H.264 High Profile detected, Instagram prefers Baseline
#          Fix: ffmpeg -i video.mp4 -profile:v baseline -level 3.0 output.mp4
```

### Browser Compatibility Check
```bash
videowise check video.webm --system safari
# Returns: ✗ Incompatible: Safari does not support VP9 codec
#          Suggestion: Convert to H.264 for maximum browser compatibility
```

### Multi-System Check
```bash
videowise check video.mp4 --all
# Checks against all 9 systems and provides summary report
```

## Contributing

We welcome contributions! Whether it's:
- **Bug reports** - something broken? Let us know
- **Feature ideas** - what would make this useful?
- **Compatibility data** - know the quirks of a platform or playback system?
- **Real-world war stories** - "this codec broke my show" tales help us build better checks
- **Code contributions** - see [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation improvements** - clearer explanations always welcome
- **Test cases** - additional edge cases to cover

This is an open learning project. Questions and "newbie" contributions are encouraged.

**Special call for live production operators:** Your domain knowledge is invaluable. We need to know what actually breaks in the field.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Why "VideoWise"?

Because understanding *why* your video won't work makes you wiser about video codecs, and wise decisions save you hours of frustration - whether you're uploading to social media or running a live show.
