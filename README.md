# VideoWise

> ⚠️ **This project is in very early stages of development.** We're building something useful, but it will take time to get to a fully workable solution. Expect changes, experiments, and iterations.

A video codec compatibility checker that explains *why* your video won't work and how to fix it.

## The Problem We're Solving

You've spent hours creating the perfect video, but:
- It won't upload to Instagram
- Safari refuses to play it
- Your client says "the video doesn't work"
- The error message is useless: "Invalid format" or worse, nothing at all

Most tools either show you raw technical data (codec, bitrate, profile) or just fail silently. **VideoWise bridges that gap** by explaining compatibility issues in plain English and suggesting actual fixes.

## What We're Building

VideoWise will analyze video files and provide human-readable explanations:
- "This won't play in Safari because it uses VP9 codec - Safari only supports H.264 and HEVC"
- "Instagram will re-encode this (losing quality) because it's H.264 High Profile instead of Baseline"
- "This file is 850MB but Twitter's limit is 512MB - you'll need to compress it"
- "This MP4 container uses AV1 codec which isn't widely supported yet - consider H.264 for maximum compatibility"

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

**What compatibility issues frustrate you the most?**
- Which platforms do you upload to? (YouTube, Instagram, Twitter, Vimeo, web browsers?)
- What error messages have you encountered that made no sense?
- What tools do you currently use to check video compatibility?
- What would make this tool actually useful for your workflow?

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
- [ ] Test with various real video files

### Phase 2: Compatibility Rules
- [ ] Browser compatibility database (Chrome, Safari, Firefox, Edge)
- [ ] Social media platform rules (Instagram, Twitter, TikTok, YouTube)
- [ ] Streaming platform requirements (Twitch, Vimeo)
- [ ] Video editor compatibility (Premiere, DaVinci Resolve, etc.)

### Phase 3: Explanations & Fixes
- [ ] Human-readable explanation generator
- [ ] Suggest specific fixes ("transcode to H.264 baseline profile")
- [ ] Provide ffmpeg commands to fix issues
- [ ] Warning severity levels (critical/warning/info)

### Phase 4: User Interface
- [ ] CLI tool for terminal use
- [ ] Drag-and-drop web interface
- [ ] Batch processing support
- [ ] Export reports

## Contributing

We welcome contributions! Whether it's:
- **Bug reports** - something broken? Let us know
- **Feature ideas** - what would make this useful?
- **Compatibility data** - know the quirks of a platform?
- **Code contributions** - see [CONTRIBUTING.md](CONTRIBUTING.md)

This is an open learning project. Questions and "newbie" contributions are encouraged.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Why "VideoWise"?

Because understanding *why* your video won't work makes you wiser about video codecs, and wise decisions save you hours of frustration.
