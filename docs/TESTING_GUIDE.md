# Testing Guide - Video Codec Checker Feature Branch

## Quick Start

### Run All Tests
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=videowise --cov-report=term-missing

# Run specific test file
pytest tests/test_playout_systems.py -v
pytest tests/test_social_media.py -v
```

### Expected Results
- **Total Tests**: 89 (all should pass)
  - `test_playout_systems.py`: 27 tests
  - `test_social_media.py`: 62 tests
- **Systems Covered**: 16 integrated systems
- **Expected Duration**: < 5 seconds

---

## Test Organization

### test_playout_systems.py (27 tests)

#### CasparCGChecker (12 tests)
- HAP codec support (standard, alpha, Q)
- NotchLC codec support
- ProRes 4444 alpha channel detection
- Legacy codec support (H.264, ProRes, DNxHD)
- 4K bandwidth warnings
- Unsupported codec handling

#### PlayoutBeeChecker (15 tests)
- HAP variants (standard, alpha, Q)
- Platform-specific (Desktop vs Raspberry Pi)
- H.264 bitrate warnings on Pi
- ProRes support and Pi warnings
- Resolution limits on Pi
- Container format support

### test_social_media.py (62 tests)

#### FirefoxChecker (10 tests)
- Codec support (H.264, VP8, VP9, AV1)
- HEVC partial support
- WebM container optimization
- MP4 container support

#### YouTubeChecker (15 tests)
- H.264 profile detection
- MP4 container preference
- File size limits
- Container format warnings

#### TikTokChecker (15 tests)
- H.264 optimization
- HEVC iOS warnings
- Mobile vs Desktop limits
- Bitrate thresholds
- Resolution optimization

#### VimeoChecker (10 tests)
- H.264 recommendations
- ProRes handling
- Resolution-based bitrate validation
- 4K, 1080p, 720p specific tests

#### FacebookChecker (12 tests)
- H.264 for Feed/Stories/Ads
- Modern codecs for Reels (HEVC, VP9, AV1)
- File size limits
- Container support

---

## Running Specific Test Categories

### Live Production Systems Only
```bash
pytest tests/test_playout_systems.py -v
```

### Social Media & Browsers Only
```bash
pytest tests/test_social_media.py -v
```

### Run Single Test Class
```bash
# CasparCG tests only
pytest tests/test_playout_systems.py::TestCasparCGChecker -v

# PlayoutBee tests only
pytest tests/test_playout_systems.py::TestPlayoutBeeChecker -v

# YouTube tests only
pytest tests/test_social_media.py::TestYouTubeChecker -v
```

### Run Single Test
```bash
pytest tests/test_playout_systems.py::TestCasparCGChecker::test_hap_codec_supported -v
```

---

## Manual Testing Examples

### Test CasparCG with HAP Codec
```python
from videowise.compatibility import CasparCGChecker

checker = CasparCGChecker(version="2.3")
video_info = {
    "codec": "hap",
    "container": "mov",
    "resolution": (1920, 1080),
}

issues = checker.check(video_info)
for issue in issues:
    print(f"{issue.level.value.upper()}: {issue.message}")
    if issue.reason:
        print(f"  Reason: {issue.reason}")
```

**Expected Output:**
```
COMPATIBLE: HAP codec provides GPU-accelerated playback
  Reason: Optimal for real-time playback in CasparCG
```

### Test PlayoutBee on Raspberry Pi
```python
from videowise.compatibility import PlayoutBeeChecker

pi_checker = PlayoutBeeChecker(platform="raspberrypi")
video_info = {
    "codec": "h264",
    "container": "mp4",
    "bitrate": 60_000_000,  # 60 Mbps
    "resolution": (1920, 1080),
}

issues = pi_checker.check(video_info)
for issue in issues:
    print(f"{issue.level.value.upper()}: {issue.message}")
```

**Expected Output:**
```
COMPATIBLE: H.264 is compatible with PlayoutBee
WARNING: H.264 at 60Mbps may be demanding on Raspberry Pi
COMPATIBLE: MP4 container is supported by PlayoutBee
```

### Test YouTube Upload
```python
from videowise.compatibility import YouTubeChecker

checker = YouTubeChecker()
video_info = {
    "codec": "h264",
    "profile": "high",
    "container": "mp4",
    "file_size": 100_000_000,  # 100MB
}

issues = checker.check(video_info)
for issue in issues:
    print(f"{issue.level.value.upper()}: {issue.message}")
```

**Expected Output:**
```
COMPATIBLE: H.264 High Profile is optimal for YouTube
COMPATIBLE: MP4 is YouTube's preferred container format
```

### Test TikTok Mobile Upload
```python
from videowise.compatibility import TikTokChecker

mobile_checker = TikTokChecker(upload_source="mobile")
video_info = {
    "codec": "h264",
    "container": "mp4",
    "resolution": (1080, 1920),
    "bitrate": 12_000_000,  # 12 Mbps
    "file_size": 200_000_000,  # 200MB
}

issues = mobile_checker.check(video_info)
for issue in issues:
    print(f"{issue.level.value.upper()}: {issue.message}")
```

**Expected Output:**
```
COMPATIBLE: H.264 is the optimal codec for TikTok
COMPATIBLE: MP4 container is supported by TikTok
COMPATIBLE: 1080x1920 is optimal for TikTok
```

---

## Coverage Requirements

### Minimum Coverage Targets
- **Overall**: > 90%
- **compatibility.py**: > 95%
- **New checkers**: 100%

### Check Coverage
```bash
# Generate HTML coverage report
pytest tests/ --cov=videowise --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage by Module
```bash
pytest tests/ --cov=videowise.compatibility --cov-report=term-missing
```

---

## Troubleshooting

### Tests Not Found
```bash
# Ensure you're in the project root
pwd

# Check pytest can discover tests
pytest --collect-only
```

### Import Errors
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Specific Test Failures
```bash
# Run with full output
pytest tests/test_playout_systems.py::TestCasparCGChecker::test_hap_codec_supported -vv -s

# Run with debugger on failure
pytest tests/ --pdb
```

---

## Test Data Patterns

### Valid Video Info Structures

```python
# Minimal
video_info = {
    "codec": "h264",
    "container": "mp4",
}

# With Resolution
video_info = {
    "codec": "prores",
    "container": "mov",
    "resolution": (1920, 1080),
}

# With Bitrate
video_info = {
    "codec": "h264",
    "container": "mp4",
    "bitrate": 50_000_000,  # 50 Mbps
}

# Complete
video_info = {
    "codec": "h264",
    "profile": "high",
    "container": "mp4",
    "resolution": (3840, 2160),
    "bitrate": 100_000_000,
    "frame_rate": "30",
    "file_size": 1_000_000_000,
}
```

### Codec Name Variations

The checkers handle various codec name formats:
- `h264`, `H.264`, `H264`
- `hevc`, `h265`, `H.265`
- `prores`, `prores422`, `prores4444`
- `hap`, `hap_alpha`, `hap_q`, `hap_q_alpha`
- `dnxhd`, `dnxhr`

---

## Continuous Integration

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=videowise --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Performance Benchmarks

### Expected Test Performance
- Individual test: < 5ms
- Full suite (89 tests): < 5 seconds
- With coverage: < 10 seconds

### Benchmark Specific Tests
```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run with timing
pytest tests/ --durations=10
```

---

## Next Steps After Tests Pass

1. **Verify all 89 tests pass** ✅
2. **Check coverage is > 90%** ✅
3. **Review PROGRESS.md** for integration status
4. **Merge `playout_additions.py`** into `compatibility.py`
5. **Create tests for 4 pending systems** (Wirecast, Resolume, PlaybackPro, PVP)
6. **Run full suite again** (~129 tests expected)
7. **Update README.md** with new systems
8. **Create pull request**

---

## Questions or Issues?

If tests fail unexpectedly:
1. Check Python version (3.8+)
2. Verify dependencies installed
3. Review PROGRESS.md for known limitations
4. Check compatibility.py for recent changes
5. Run with `-vv` for detailed output

**Current Status**: 89/89 tests should pass ✅
