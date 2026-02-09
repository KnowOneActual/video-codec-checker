# VideoWise

A video codec compatibility checker that explains *why* your video won't work and how to fix it.

## What It Does

VideoWise analyzes video files and explains compatibility issues in plain English:
- "This won't play in Safari because it uses VP9 codec"
- "Instagram will re-encode this because it's not H.264 baseline profile"
- "This file is too large for Twitter's 512MB limit"

## Status

🚧 **Early Development** - Building the foundation

## Installation

### Prerequisites

You need FFmpeg installed on your system:

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
```

## Development

### Running Tests

```bash
pytest
```

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

- [x] Project setup
- [x] Basic file validation
- [x] FFprobe integration
- [ ] Extract codec information
- [ ] Browser compatibility rules
- [ ] Social media platform rules
- [ ] Human-readable explanations
- [ ] CLI interface
- [ ] Suggest fixes/transcoding options

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Distributed under the MIT License. See LICENSE for more information.
