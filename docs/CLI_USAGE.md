# VideoWise CLI Usage Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

Check a video file's compatibility with a specific system:

```bash
videowise check video.mp4 --system casparcg
```

## Commands

### `check`

Check video file compatibility with a specific system.

**Basic Usage:**
```bash
videowise check <file> --system <system>
```

**Options:**
- `--system, -s`: Target system to check (required)
  - Available systems: `casparcg`, `vmix`, `obs`, `qlab`, `propresenter`, `safari`, `chrome`, `instagram`, `twitter`
- `--verbose, -v`: Show detailed information
- `--json`: Output results as JSON

## Examples

### Live Production

**Check CasparCG compatibility:**
```bash
videowise check sponsor_video.mov --system casparcg
```

**Check vMix with verbose output:**
```bash
videowise check high_bitrate_clip.mp4 --system vmix -v
```

**Pre-show verification for QLab:**
```bash
videowise check background_loop.mov --system qlab
```

### Browser Compatibility

**Check Safari compatibility:**
```bash
videowise check website_video.webm --system safari
```

**Check Chrome compatibility:**
```bash
videowise check hero_video.mp4 --system chrome
```

### Social Media

**Instagram upload check:**
```bash
videowise check promo_video.mp4 --system instagram -v
```

**Twitter/X upload check:**
```bash
videowise check announcement.mov --system twitter
```

### JSON Output (for scripting)

```bash
videowise check video.mp4 --system casparcg --json > results.json
```

JSON output structure:
```json
{
  "file": "video.mp4",
  "system": "casparcg",
  "issues": [
    {
      "level": "compatible",
      "message": "Video is compatible with CasparCG 2.3",
      "reason": null,
      "suggestion": null
    }
  ]
}
```

## Exit Codes

The CLI uses standard exit codes for scripting:

- `0`: Compatible (all green)
- `1`: Warnings (yellow warnings present)
- `2`: Incompatible (red errors or tool errors)

**Example usage in scripts:**
```bash
#!/bin/bash
if videowise check video.mp4 --system casparcg; then
    echo "Video is ready for playback!"
else
    echo "Video needs fixing"
    exit 1
fi
```

## Output Colors

Terminal output uses colors for quick visual scanning:

- ✓ **Green**: Compatible - file will work
- ⚠ **Yellow**: Warning - may have issues, check carefully
- ✗ **Red**: Incompatible - will not work, must fix
- ? **Cyan**: Unknown - unable to determine

## Common Workflows

### Pre-Show Checklist

```bash
#!/bin/bash
# Check all videos in a playlist

echo "Checking show playlist..."
for video in playlist/*.mp4; do
    echo "Checking $video..."
    if ! videowise check "$video" --system casparcg; then
        echo "⚠️  Warning: $video has compatibility issues!"
    fi
done
```

### Batch Upload Preparation

```bash
# Check multiple videos for Instagram
for video in export/*.mp4; do
    videowise check "$video" --system instagram --json >> instagram_report.json
done
```

### CI/CD Integration

```yaml
# .github/workflows/video-check.yml
name: Check Video Compatibility

on:
  push:
    paths:
      - 'assets/videos/**'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install ffmpeg
        run: sudo apt-get install -y ffmpeg
      - name: Install VideoWise
        run: pip install -e .
      - name: Check videos
        run: |
          for video in assets/videos/*.mp4; do
            videowise check "$video" --system safari
          done
```

## Troubleshooting

### "Unable to extract video metadata"

**Problem:** ffmpeg/ffprobe is not installed or not in PATH.

**Solution:**
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Command not found

**Problem:** VideoWise is not installed correctly.

**Solution:**
```bash
pip install -e .
```

## Getting Help

```bash
# General help
videowise --help

# Command-specific help
videowise check --help

# Version info
videowise --version
```

## What's Next?

- See [ROADMAP.md](../ROADMAP.md) for upcoming features
- Report issues on [GitHub](https://github.com/KnowOneActual/video-codec-checker/issues)
- Contribute improvements via pull requests
