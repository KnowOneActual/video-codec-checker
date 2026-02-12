# VideoWise Quick Start Guide

## For Users (Phase 2 - Coming Soon)

Once the CLI is ready, you'll be able to:

```bash
pip install videowise
videowise check video.mp4 --system casparcg
```

For now, see the Developer Quick Start below.

---

## For Developers (Current)

### Prerequisites

1. **Python 3.8+** - Check your version:
   ```bash
   python3 --version
   ```

2. **FFmpeg** - Must be installed and in your PATH:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Git** - For cloning the repository

### Installation

```bash
# Clone the repository
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation - run tests
pytest -v
```

You should see **45 tests pass**.

### Basic Usage (Python API)

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility

# Analyze a video file
analyzer = VideoAnalyzer('path/to/video.mp4')
video_info = analyzer.get_video_info()

# Check compatibility with a specific system
issues = check_compatibility(video_info, 'casparcg')

# Print results
for issue in issues:
    print(f"[{issue.level.value.upper()}] {issue.message}")
    if issue.reason:
        print(f"  Reason: {issue.reason}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

### Example Output

```
[COMPATIBLE] Video is compatible with CasparCG 2.3
```

```
[INCOMPATIBLE] CasparCG 2.3 does not support VP9 codec
  Reason: CasparCG only supports: dnxhd, dnxhr, h264, mjpeg, mpeg2video, prores
  Suggestion: Convert to ProRes, DNxHD, or H.264 in MP4 container
```

```
[WARNING] H.264 works but performs poorly when scrubbing or changing speed
  Reason: H.264 is not optimized for variable-speed playback
  Suggestion: Convert to ProRes 422 Proxy or LT for better performance
```

### Supported Systems

```python
# Check against different systems
check_compatibility(video_info, 'casparcg')     # CasparCG Server
check_compatibility(video_info, 'vmix')         # vMix
check_compatibility(video_info, 'obs')          # OBS Studio
check_compatibility(video_info, 'qlab')         # QLab
check_compatibility(video_info, 'propresenter') # ProPresenter
check_compatibility(video_info, 'safari')       # Safari browser
check_compatibility(video_info, 'chrome')       # Chrome browser
check_compatibility(video_info, 'instagram')    # Instagram
check_compatibility(video_info, 'twitter')      # Twitter/X
```

### Common Workflows

#### Check Multiple Systems

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility

systems = ['casparcg', 'vmix', 'obs', 'qlab', 'propresenter']
analyzer = VideoAnalyzer('video.mp4')
video_info = analyzer.get_video_info()

for system in systems:
    print(f"\n=== {system.upper()} ===")
    issues = check_compatibility(video_info, system)
    for issue in issues:
        print(f"[{issue.level.value}] {issue.message}")
```

#### Filter by Severity

```python
from videowise.compatibility import CompatibilityLevel

issues = check_compatibility(video_info, 'instagram')

# Show only problems
problems = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
for issue in problems:
    print(issue.message)

# Show warnings
warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
for issue in warnings:
    print(issue.message)
```

#### Get Video Metadata

```python
from videowise.analyzer import VideoAnalyzer

analyzer = VideoAnalyzer('video.mp4')
video_info = analyzer.get_video_info()

print(f"Codec: {video_info['codec']}")
print(f"Container: {video_info['container']}")
print(f"Resolution: {video_info['resolution']}")
print(f"Frame Rate: {video_info['frame_rate']}")
print(f"Bitrate: {video_info.get('bitrate', 'N/A')}")
print(f"Profile: {video_info.get('profile', 'N/A')}")
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
open htmlcov/index.html  # View coverage report
```

### Development Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** and add tests

3. **Run tests:**
   ```bash
   pytest
   ```

4. **Format code** (optional, recommended):
   ```bash
   black videowise/
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-new-feature
   ```

6. **Create Pull Request** on GitHub

### Project Structure

```
video-codec-checker/
├── videowise/              # Main package
│   ├── __init__.py
│   ├── analyzer.py        # Video analysis
│   └── compatibility.py   # Compatibility checkers
├── tests/                 # Test suite (45 tests)
├── docs/                  # Documentation
├── README.md              # Project overview
├── ROADMAP.md             # Development roadmap
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # Contribution guidelines
├── setup.py               # Package setup
├── pyproject.toml         # Modern Python config
└── requirements.txt       # Dependencies
```

### Troubleshooting

#### "FFmpeg not found"

Make sure FFmpeg is installed and in your PATH:
```bash
ffmpeg -version
ffprobe -version
```

If not found:
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt-get install ffmpeg`
- **Windows:** Add FFmpeg to your PATH after installing

#### Tests are skipped

Some tests require ffmpeg to generate test videos. If ffmpeg is not available, they'll be skipped automatically. This is expected behavior.

#### Import errors

Make sure you're in the project root directory and your virtual environment is activated:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how the code works
- Check [ROADMAP.md](../ROADMAP.md) to see what's coming next
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
- Open an [issue](https://github.com/KnowOneActual/video-codec-checker/issues) with questions

### Getting Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/KnowOneActual/video-codec-checker/issues)
- **Discussions:** [Ask questions or share ideas](https://github.com/KnowOneActual/video-codec-checker/discussions)
- **Documentation:** Check the `/docs` folder for detailed guides

---

**Ready to build the CLI?** See [ROADMAP.md](../ROADMAP.md) Phase 2 for what's coming next!
