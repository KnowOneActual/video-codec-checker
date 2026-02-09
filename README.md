# VideoWise

> ⚠️ **This project is in very early stages of development.** We're building something useful, but it will take time to get to a fully workable solution. Expect changes, experiments, and iterations.

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

VideoWise will analyze video files and provide human-readable explanations:

**For Upload/Playback:**
- "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC"
- "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline"
- "This file is 850MB but Twitter's limit is 512MB - you'll need to compress it"
- "This MP4 container uses AV1 codec which isn't widely supported yet - consider H.264 for maximum compatibility"

**For Live Production:**
- "CasparCG 2.3 can't play this - it requires ProRes, DNxHD, or H.264 in MP4 container"
- "This file will cause dropped frames in vMix - bitrate is 180Mbps but your system can only handle 100Mbps smoothly"
- "Linux Show Player may have audio sync issues - this uses VBR audio instead of CBR"
- "This codec requires GPU decoding but your system only has CPU decode - expect playback issues"
- "Warning: Variable frame rate video will cause timing issues in live production - convert to constant frame rate"

## Current Status

🚧 **Early Development Phase** - We're currently:
- [x] Setting up project structure
- [x] Implementing basic file validation
- [x] Integrating ffprobe for metadata extraction
- [ ] Building codec information parser
- [ ] Creating compatibility rules engine
- [ ] Writing human-readable explanation system

This is a **learning project** being built incrementally with testing at each step. Progress may be slow, but it will be solid.

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

# Run tests to verify setup
pytest
```

## Development

### Running Tests

```bash
pytest
```

We're building this test-first, so every feature should have tests before implementation.

### Project Structure

```
video-codec-checker/
├── videowise/          # Core package
│   ├── analyzer.py     # Video analysis
│   ├── compatibility.py # Rules engine (coming soon)
│   └── explainer.py    # Human-readable output (coming soon)
└── tests/              # Test suite
```

## Roadmap

### Phase 1: Foundation (Current)
- [x] Project setup and structure
- [x] Basic file validation
- [x] FFprobe integration
- [ ] Parse codec, container, and profile information
- [ ] Test with various real video files (ProRes, H.264, DNxHD, etc.)

### Phase 2: Compatibility Rules
- [ ] Browser compatibility database (Chrome, Safari, Firefox, Edge)
- [ ] Social media platform rules (Instagram, Twitter, TikTok, YouTube)
- [ ] Live production systems (CasparCG, vMix, OBS, Linux Show Player, Wirecast)
- [ ] Streaming platform requirements (Twitch, Vimeo, Restream)
- [ ] Video editor compatibility (Premiere, DaVinci Resolve, Final Cut Pro)

### Phase 3: Explanations & Fixes
- [ ] Human-readable explanation generator
- [ ] Suggest specific fixes ("transcode to H.264 baseline profile")
- [ ] Provide ffmpeg commands to fix issues
- [ ] Warning severity levels (critical/warning/info)
- [ ] Pre-show compatibility checker mode for live production

### Phase 4: User Interface
- [ ] CLI tool for terminal use
- [ ] Drag-and-drop web interface
- [ ] Batch processing support (check entire playlists)
- [ ] Export reports (for production documentation)
- [ ] Watch folder mode (auto-check files as they arrive)

## Use Cases

### Pre-Show Verification
```bash
videowise check-playlist /path/to/show/media/ --system casparcg-2.3
# Returns: 5 files OK, 2 files need attention:
#   - intro.mov: Wrong codec, will not play. Convert to ProRes.
#   - sponsor.mp4: VFR detected, may cause timing issues. Convert to CFR.
```

### Upload Preparation
```bash
videowise check video.mp4 --target instagram
# Returns: File will be re-encoded by Instagram (quality loss)
#          Reason: H.264 High Profile detected, Instagram prefers Baseline
#          Fix: ffmpeg -i video.mp4 -profile:v baseline -level 3.0 output.mp4
```

### Quick Compatibility Check
```bash
videowise info video.mov
# Returns: ProRes 422 HQ, 1920x1080, 23.976fps
#          ✓ Compatible with: CasparCG, vMix, Premiere, DaVinci
#          ✗ Not compatible with: Web browsers (use H.264 instead)
```

## Contributing

We welcome contributions! Whether it's:
- **Bug reports** - something broken? Let us know
- **Feature ideas** - what would make this useful?
- **Compatibility data** - know the quirks of a platform or playback system?
- **Real-world war stories** - "this codec broke my show" tales help us build better checks
- **Code contributions** - see [CONTRIBUTING.md](CONTRIBUTING.md)

This is an open learning project. Questions and "newbie" contributions are encouraged.

**Special call for live production operators:** Your domain knowledge is invaluable. We need to know what actually breaks in the field.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Why "VideoWise"?

Because understanding *why* your video won't work makes you wiser about video codecs, and wise decisions save you hours of frustration - whether you're uploading to social media or running a live show.
