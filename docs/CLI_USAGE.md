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

Process **multiple files or directories**:

```bash
videowise batch videos/ --recursive --all
```

## Commands

### `check`

Check a single video file's compatibility with one or all systems.

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

### `batch`

Check multiple video files or entire directories for compatibility.

**Basic Usage:**
```bash
# Check multiple files
videowise batch <file1> <file2> ... --system <system>

# Check directory (non-recursive)
videowise batch <directory> --system <system>

# Check directory recursively
videowise batch <directory> --recursive --all
```

**Options:**
- `--system, -s`: Target system to check (mutually exclusive with `--all`)
- `--all`: Check against all available systems (mutually exclusive with `--system`)
- `--recursive, -r`: Recursively scan directories for video files
- `--extensions, -e`: Comma-separated list of file extensions to include (e.g., `.mp4,.mov`)
  - Default: `.mp4,.mov,.avi,.mkv,.m4v,.webm,.flv,.wmv,.mpg,.mpeg,.m2v,.mxf`
- `--json`: Output batch results as JSON
- `--verbose, -v`: Show detailed processing information
- `--continue-on-error`: Continue processing files even if some fail (default: True)

**Note:** You must specify either `--system` or `--all`, but not both.

## Examples

### Single File Check

**Check CasparCG compatibility:**
```bash
videowise check sponsor_video.mov --system casparcg
```

**Check all systems:**
```bash
videowise check promo_video.mp4 --all
```

**Check with verbose output:**
```bash
videowise check video.mp4 --system vmix -v
```

### Batch Processing

**Check multiple specific files:**
```bash
videowise batch video1.mp4 video2.mov video3.mp4 --system casparcg
```

Output:
```
📂 Found 3 video file(s) to check

======================================================================
📊 BATCH SUMMARY
======================================================================

Total files processed: 3
Systems checked: casparcg

✅ Fully compatible: 2
⚠️  Warnings: 1
```

**Check all videos in a directory:**
```bash
videowise batch /path/to/videos/ --system casparcg
```

**Recursively scan directory and all subdirectories:**
```bash
videowise batch /media/show-content/ --recursive --all
```

Output with `--all` flag:
```
📂 Found 15 video file(s) to check

======================================================================
📊 BATCH SUMMARY
======================================================================

Total files processed: 15
Systems checked: casparcg, vmix, obs, qlab, propresenter, safari, chrome, instagram, twitter

✅ Fully compatible: 10
⚠️  Warnings: 3
❌ Incompatible: 2
```

**Filter by file extension:**
```bash
# Only check .mp4 and .mov files
videowise batch /videos/ --recursive --extensions .mp4,.mov --all
```

**Verbose batch processing:**
```bash
videowise batch videos/ --all -v
```

With verbose mode, you'll see each file being processed:
```
📂 Found 5 video file(s) to check

Processing: /videos/clip1.mp4
Processing: /videos/clip2.mp4
Processing: /videos/clip3.mov
...
```

**Batch processing with JSON output:**
```bash
videowise batch videos/*.mp4 --all --json > batch_report.json
```

JSON structure:
```json
{
  "total_files": 3,
  "processed_files": 3,
  "systems_checked": ["casparcg", "vmix", "obs", "qlab", "propresenter", "safari", "chrome", "instagram", "twitter"],
  "results": [
    {
      "file": "/videos/video1.mp4",
      "video_info": {
        "codec": "h264",
        "profile": "High",
        "container": "mp4",
        "width": 1920,
        "height": 1080,
        "framerate": 29.97,
        "bitrate": 12500000
      },
      "systems_checked": ["casparcg", "vmix", ...],
      "results": [
        {
          "system": "casparcg",
          "issues": [{"level": "compatible", "message": "..."}]
        }
      ],
      "exit_code": 0
    },
    {
      "file": "/videos/video2.mp4",
      "video_info": {...},
      "systems_checked": [...],
      "results": [...],
      "exit_code": 1
    }
  ],
  "errors": 0
}
```

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

## Exit Codes

The CLI uses standard exit codes for scripting:

- `0`: Compatible (all checks passed, no warnings)
- `1`: Warnings (yellow warnings present, but may work)
- `2`: Incompatible (red errors, will not work)

**For `--all` flag:** The exit code reflects the **worst case** across all systems:
- If any system is incompatible → exit code `2`
- Else if any system has warnings → exit code `1`  
- Else all compatible → exit code `0`

**For `batch` command:** The exit code reflects the **worst case** across all processed files:
- If any file is incompatible → exit code `2`
- Else if any file has warnings → exit code `1`
- Else all files compatible → exit code `0`

## Output Colors

Terminal output uses colors for quick visual scanning:

- ✅ **Green**: Compatible - file will work
- ⚠️ **Yellow**: Warning - may have issues, check carefully
- ❌ **Red**: Incompatible - will not work, must fix
- ℹ️ **Cyan**: Information

## Common Workflows

### Pre-Show Checklist (Single File)

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

### Pre-Show Checklist (Batch Mode)

```bash
#!/bin/bash
# Check entire video library at once using batch mode

echo "🎬 Pre-Show Compatibility Check (Batch Mode)"
echo "============================================="

if videowise batch playlist/ --recursive --all --json > full_report.json; then
    echo "\n✅ All videos passed compatibility checks!"
    exit 0
else
    exit_code=$?
    echo "\n⚠️  Some videos have compatibility issues."
    echo "See full_report.json for details"
    exit $exit_code
fi
```

### Validate Entire Media Library

```bash
#!/bin/bash
# Scan entire media library and generate compatibility report

echo "📚 Scanning media library..."

videowise batch /media/library/ \
    --recursive \
    --all \
    --json > library_report.json

echo "\n📊 Generating summary..."

# Extract summary using jq
jq '{
  total: .total_files,
  compatible: [.results[] | select(.exit_code == 0)] | length,
  warnings: [.results[] | select(.exit_code == 1)] | length,
  incompatible: [.results[] | select(.exit_code == 2)] | length,
  errors: .errors
}' library_report.json
```

### Find Videos Compatible with Specific System (Batch)

```bash
#!/bin/bash
# Find all CasparCG-compatible videos in a directory

echo "🔍 Finding CasparCG-compatible videos..."

videowise batch videos/ --recursive --system casparcg --json > results.json

# Extract compatible videos
jq -r '.results[] | select(.exit_code == 0) | .file' results.json > compatible_videos.txt

echo "\n✅ Found $(wc -l < compatible_videos.txt) compatible videos"
echo "List saved to: compatible_videos.txt"
```

### Social Media Batch Validation

```bash
#!/bin/bash
# Check all export videos for social media compatibility

echo "📱 Checking social media compatibility..."

videowise batch exports/ --all --json | \
    jq '.results[] | {
        file: .file | split("/")[-1],
        instagram: (.results[] | select(.system == "instagram") | .issues[0].level),
        twitter: (.results[] | select(.system == "twitter") | .issues[0].level)
    }'
```

### CI/CD Integration (Batch)

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
      - name: Check all videos using batch mode
        run: |
          videowise batch assets/videos/ --recursive --all --json > compatibility_report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: compatibility-report
          path: compatibility_report.json
      - name: Fail if incompatibilities found
        run: |
          if jq -e '.results[] | select(.exit_code == 2)' compatibility_report.json > /dev/null; then
            echo "❌ Incompatible videos found!"
            jq '.results[] | select(.exit_code == 2) | .file' compatibility_report.json
            exit 1
          fi
```

### Filter by Extension and Quality Check

```bash
#!/bin/bash
# Check only high-quality formats (ProRes, DNxHD)

echo "🎥 Checking professional formats..."

videowise batch media/ \
    --recursive \
    --extensions .mov,.mxf \
    --system casparcg \
    --json > prores_check.json

echo "Results saved to prores_check.json"
```

### Error Handling in Batch Processing

```bash
#!/bin/bash
# Process with detailed error reporting

videowise batch videos/ --recursive --all --json > report.json

if [ $? -ne 0 ]; then
    echo "\n⚠️  Batch processing completed with issues"
    
    # Check for processing errors
    error_count=$(jq '.errors' report.json)
    if [ "$error_count" -gt 0 ]; then
        echo "\n❌ $error_count file(s) could not be processed:"
        jq -r '.results[] | select(.error) | "  - \(.file): \(.error)"' report.json
    fi
    
    # Check for incompatibilities
    incompatible=$(jq '[.results[] | select(.exit_code == 2)] | length' report.json)
    if [ "$incompatible" -gt 0 ]; then
        echo "\n❌ $incompatible file(s) incompatible with at least one system"
    fi
fi
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
videowise batch videos/

# Correct
videowise check video.mp4 --system casparcg
videowise batch videos/ --all
```

### "Cannot use both --system and --all flags"

**Problem:** You provided both flags at the same time.

**Solution:**
```bash
# Wrong
videowise batch videos/ --system safari --all

# Correct - choose one
videowise batch videos/ --system safari
# OR
videowise batch videos/ --all
```

### "No video files found"

**Problem:** The batch command couldn't find any video files in the specified path(s).

**Solutions:**
1. **Check the path exists:**
   ```bash
   ls -la /path/to/videos/
   ```

2. **Use recursive flag for subdirectories:**
   ```bash
   videowise batch /path/ --recursive --all
   ```

3. **Check file extensions:**
   ```bash
   # If your files have uncommon extensions
   videowise batch /path/ --extensions .mp4,.avi --system casparcg
   ```

4. **Verify files are actually videos:**
   ```bash
   ffprobe video_file.mp4
   ```

### Batch processing is slow

**Problem:** Processing many files with `--all` flag takes significant time.

**Solutions:**
1. **Target specific systems** if you don't need all:
   ```bash
   videowise batch videos/ --system casparcg
   ```

2. **Filter files before processing:**
   ```bash
   # Only check MP4 files
   videowise batch videos/ --extensions .mp4 --all
   ```

3. **Process in parallel** (advanced):
   ```bash
   find videos/ -name "*.mp4" | \
       parallel -j 4 "videowise check {} --all --json > {}.json"
   ```

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
videowise batch --help

# Version info
videowise --version
```

## What's Next?

- See [ROADMAP.md](../ROADMAP.md) for upcoming features
- Report issues on [GitHub](https://github.com/KnowOneActual/video-codec-checker/issues)
- Contribute improvements via pull requests
