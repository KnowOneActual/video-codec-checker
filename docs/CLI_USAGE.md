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

Or check against **all systems at once**:

```bash
videowise check video.mp4 --all
```

## Commands

### `check`

Check video file compatibility with one or all systems.

**Basic Usage:**
```bash
# Check a single system
videowise check <file> --system <system>

# Check all systems
videowise check <file> --all
```

**Options:**
- `--system, -s`: Target system to check (mutually exclusive with `--all`)
  - Available systems: `casparcg`, `vmix`, `obs`, `qlab`, `propresenter`, `safari`, `chrome`, `instagram`, `twitter`
- `--all`: Check against all available systems (mutually exclusive with `--system`)
- `--verbose, -v`: Show detailed information (codec, bitrate, resolution, etc.)
- `--json`: Output results as JSON for scripting/automation

**Note:** You must specify either `--system` or `--all`, but not both.

## Examples

### Check All Systems

**Basic all-systems check:**
```bash
videowise check promo_video.mp4 --all
```

Output:
```
📹 Video: promo_video.mp4

🔍 Checking against all 9 systems

============================================================
🎬 CASPARCG
============================================================
✅ Video is compatible with CasparCG 2.3

============================================================
🎬 SAFARI
============================================================
⚠️  Safari may have performance issues with High Profile H.264
   Reason: Safari prefers Main or Baseline profile
   Suggestion: Consider Main profile for better compatibility

============================================================
📊 SUMMARY
============================================================

✅ Compatible (7):
   • casparcg
   • vmix
   • obs
   • chrome
   • instagram
   • twitter
   • propresenter

⚠️  Warnings (2):
   • safari
   • qlab
```

**Check all systems with verbose output:**
```bash
videowise check video.mp4 --all -v
```

This shows detailed codec information before compatibility checks:
```
📹 Video: video.mp4

Codec: h264 (High)
Container: mp4
Resolution: 1920x1080
Framerate: 29.97 fps
Bitrate: 12.50 Mbps

🔍 Checking against all 9 systems
...
```

**Check all systems with JSON output:**
```bash
videowise check video.mp4 --all --json > full_report.json
```

JSON output structure for `--all`:
```json
{
  "file": "video.mp4",
  "video_info": {
    "codec": "h264",
    "profile": "High",
    "container": "mp4",
    "width": 1920,
    "height": 1080,
    "framerate": 29.97,
    "bitrate": 12500000,
    "file_size": 52428800
  },
  "systems_checked": [
    "casparcg",
    "vmix",
    "obs",
    "qlab",
    "propresenter",
    "safari",
    "chrome",
    "instagram",
    "twitter"
  ],
  "results": [
    {
      "system": "casparcg",
      "issues": [
        {
          "level": "compatible",
          "message": "Video is compatible with CasparCG 2.3",
          "reason": null,
          "suggestion": null
        }
      ]
    },
    {
      "system": "safari",
      "issues": [
        {
          "level": "warning",
          "message": "Safari may have performance issues",
          "reason": "High Profile H.264 is supported but not optimal",
          "suggestion": "Use Main or Baseline profile for best compatibility"
        }
      ]
    }
  ]
}
```

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

**Verify video works everywhere before show:**
```bash
videowise check opening_video.mp4 --all
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

**Check all browsers at once:**
```bash
videowise check landing_page_video.mp4 --all | grep -A 5 "safari\|chrome"
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

**Check all social platforms:**
```bash
videowise check social_media_post.mp4 --all
```

### JSON Output (for scripting)

**Single system:**
```bash
videowise check video.mp4 --system casparcg --json > results.json
```

JSON output structure (single system):
```json
{
  "file": "video.mp4",
  "system": "casparcg",
  "video_info": {
    "codec": "h264",
    "profile": "High",
    "container": "mp4"
  },
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

- `0`: Compatible (all checks passed, no warnings)
- `1`: Warnings (yellow warnings present, but may work)
- `2`: Incompatible (red errors, will not work)

**For `--all` flag:** The exit code reflects the **worst case** across all systems:
- If any system is incompatible → exit code `2`
- Else if any system has warnings → exit code `1`
- Else all compatible → exit code `0`

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

**Check all systems and fail if any incompatibility:**
```bash
#!/bin/bash
if videowise check video.mp4 --all --json > report.json; then
    echo "✅ Video compatible with all systems"
else
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        echo "❌ Video incompatible with at least one system"
    elif [ $exit_code -eq 1 ]; then
        echo "⚠️  Video has warnings on some systems"
    fi
    exit $exit_code
fi
```

## Output Colors

Terminal output uses colors for quick visual scanning:

- ✅ **Green**: Compatible - file will work
- ⚠️ **Yellow**: Warning - may have issues, check carefully
- ❌ **Red**: Incompatible - will not work, must fix
- ℹ️ **Cyan**: Information

## Common Workflows

### Pre-Show Checklist

```bash
#!/bin/bash
# Check all videos in a playlist against all systems

echo "🎬 Pre-Show Compatibility Check"
echo "================================"

failed_videos=()

for video in playlist/*.mp4; do
    echo "\nChecking $(basename "$video")..."
    if ! videowise check "$video" --all --json > "reports/$(basename "$video" .mp4).json"; then
        failed_videos+=("$video")
    fi
done

if [ ${#failed_videos[@]} -eq 0 ]; then
    echo "\n✅ All videos passed compatibility checks!"
else
    echo "\n⚠️  The following videos have issues:"
    printf '   - %s\n' "${failed_videos[@]}"
    echo "\nCheck individual reports in reports/ directory"
    exit 1
fi
```

### Universal Compatibility Check

```bash
#!/bin/bash
# Check if a video works everywhere

video="$1"

echo "🔍 Checking $video for universal compatibility..."

if videowise check "$video" --all; then
    echo "\n✅ This video will work on all systems!"
    exit 0
else
    echo "\n⚠️  This video has compatibility issues."
    echo "Run with -v flag for details: videowise check \"$video\" --all -v"
    exit 1
fi
```

### Batch Upload Preparation

```bash
# Check multiple videos for social media
for video in export/*.mp4; do
    echo "Checking $(basename "$video")..."
    videowise check "$video" --all --json | \
        jq '{file: .file, instagram: .results[] | select(.system=="instagram"), twitter: .results[] | select(.system=="twitter")}'
done
```

### Find Videos Compatible with Specific System

```bash
#!/bin/bash
# Find all videos in a directory compatible with CasparCG

for video in videos/*.{mp4,mov}; do
    if videowise check "$video" --system casparcg --json 2>/dev/null | \
       jq -e '.issues[] | select(.level == "incompatible")' > /dev/null; then
        : # Has incompatibilities, skip
    else
        echo "✅ $video"
    fi
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
      - name: Check all videos against all systems
        run: |
          mkdir -p reports
          for video in assets/videos/*.mp4; do
            echo "Checking $video..."
            videowise check "$video" --all --json > "reports/$(basename "$video" .mp4).json" || true
          done
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: compatibility-reports
          path: reports/
```

## Troubleshooting

### "Unable to extract video metadata"

**Problem:** ffmpeg/ffprobe is not installed or not in PATH.

**Solution:**
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### "Must specify either --system or --all flag"

**Problem:** You didn't provide either `--system` or `--all`.

**Solution:**
```bash
# Wrong
videowise check video.mp4

# Correct
videowise check video.mp4 --system casparcg
# OR
videowise check video.mp4 --all
```

### "Cannot use both --system and --all flags"

**Problem:** You provided both flags at the same time.

**Solution:**
```bash
# Wrong
videowise check video.mp4 --system safari --all

# Correct - choose one
videowise check video.mp4 --system safari
# OR
videowise check video.mp4 --all
```

### Command not found

**Problem:** VideoWise is not installed correctly.

**Solution:**
```bash
pip install -e .
```

### `--all` check is too slow

**Problem:** Checking all systems takes time because each system runs compatibility rules.

**Solution:** For repeated checks, use `--system` to target specific systems. Use `--all` when you need comprehensive verification (e.g., pre-show checks, final deliverable validation).

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
