# VideoWise CLI Usage Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

VideoWise now has **simple preset commands** for the fastest workflow:

```bash
# Use system names directly!
videowise casparcg video.mp4        # Check for CasparCG
videowise instagram video.mp4       # Check for Instagram
videowise resolume video.mp4        # Check for Resolume

# Check against ALL systems (default)
videowise check video.mp4

# Educational mode - understand WHY
videowise learn video.mp4

# See all available systems
videowise systems
```

## Commands Overview

VideoWise offers three ways to check videos:

### 1. Preset Commands (Simplest! ⭐)
Direct system-specific commands:
```bash
videowise casparcg video.mp4
videowise instagram video.mp4
videowise obs video.mp4
```

### 2. Check Command (Flexible)
```bash
videowise check video.mp4                    # All systems (default)
videowise check video.mp4 --system casparcg  # Single system
```

### 3. Learn Command (Educational)
```bash
videowise learn video.mp4  # Explains WHY issues occur
```

## Preset Commands (⭐ Recommended)

**The fastest way to check compatibility!**

All 22 systems have preset commands:

```bash
# Live Production
videowise casparcg video.mp4
videowise vmix video.mp4
videowise obs video.mp4
videowise qlab video.mp4
videowise propresenter video.mp4
videowise wirecast video.mp4
videowise playbackpro video.mp4
videowise easyworship video.mp4
videowise playoutbee video.mp4

# VJ / Media Players
videowise resolume video.mp4
videowise vlc video.mp4
videowise mitti video.mp4
videowise millumin video.mp4

# Browsers
videowise safari video.mp4
videowise chrome video.mp4
videowise firefox video.mp4

# Social Media
videowise instagram video.mp4
videowise twitter video.mp4
videowise youtube video.mp4
videowise tiktok video.mp4
videowise vimeo video.mp4
videowise facebook video.mp4
```

**All preset commands support:**
- `--recursive, -r`: Scan directories recursively
- `--extensions, -e`: Filter file types (e.g., `.mp4,.mov`)
- `--json`: Output as JSON
- `--verbose, -v`: Show detailed video info
- `--no-color`: Plain text output

**Examples:**
```bash
# Check single file
videowise casparcg sponsor_video.mov

# Check directory recursively
videowise instagram exports/ -r

# Multiple files with JSON output
videowise resolume video1.mp4 video2.mp4 --json

# Verbose with specific extensions
videowise vmix videos/ -r -e .mp4,.mov --verbose
```

## Check Command

Check videos against one or all systems.

### Default Behavior (All Systems)
```bash
# Checks against ALL 22 systems
videowise check video.mp4
```

### Single System
```bash
# Check specific system
videowise check video.mp4 --system casparcg
```

### Options
- `--system, -s <name>`: Check specific system
- `--all`: Explicitly check all systems (default behavior)
- `--explain`: Add educational explanations
- `--verbose, -v`: Show detailed video information
- `--json`: Output as JSON
- `--no-color`: Disable colors
- `--recursive, -r`: Scan directories recursively
- `--extensions, -e <list>`: File extensions to check

**Examples:**
```bash
# All systems (default)
videowise check video.mp4

# Single system
videowise check video.mp4 --system safari

# With explanations
videowise check video.mp4 --system instagram --explain

# Batch check directory
videowise check videos/ -r
```

## Learn Command (Educational Mode)

Get extended explanations to **understand why** videos fail:

```bash
videowise learn video.mp4
```

This checks against all systems with educational context about:
- What each codec is and how it works
- Why certain systems don't support specific formats
- Best practices for video encoding
- How to fix compatibility issues

**Examples:**
```bash
# Learn about a problematic video
videowise learn problem_video.mp4

# Learn mode on entire directory
videowise learn exports/ -r

# Save to text file for training
videowise learn video.mp4 --no-color > training_guide.txt
```

**Output includes:**
```
📹 Video: problem_video.mp4

🔍 Checking against all 22 systems

============================================================
🎬 SAFARI
============================================================
❌ VP9 codec not supported
   Reason: Safari only supports H.264 and HEVC
   Suggestion: Convert to H.264 for Safari compatibility

   📖 About Incompatible:
      This video will NOT work.
      The video will fail to play, upload, or process. Conversion is required.

   💡 Additional Context:
      VP9 is a modern, efficient codec by Google, but not universally 
      supported. H.264 or HEVC are safer choices for broad compatibility.
```

## Systems Command

List all available systems:

```bash
videowise systems
```

**Output:**
```
📋 Available Systems:

Live Production:
  • casparcg           → videowise casparcg video.mp4
  • vmix               → videowise vmix video.mp4
  • obs                → videowise obs video.mp4
  ...

VJ / Media Players:
  • resolume           → videowise resolume video.mp4
  ...

Browsers:
  • safari             → videowise safari video.mp4
  ...

Social Media:
  • instagram          → videowise instagram video.mp4
  ...

💡 TIP:
  Use system names directly as commands for simpler usage!
```

## Batch Command (Legacy)

**Note:** The `check` command now handles both single files and batches. The `batch` command is kept for backward compatibility.

**Use `check` or preset commands instead:**
```bash
# Old way
videowise batch videos/ --recursive --system casparcg

# New way (simpler!)
videowise casparcg videos/ -r
# OR
videowise check videos/ -r --system casparcg
```

## Common Workflows

### Pre-Show Check
```bash
# Check all show videos for CasparCG
videowise casparcg show-videos/ -r

# Check with verbose output
videowise casparcg show-videos/ -r -v
```

### Social Media Export Validation
```bash
# Check Instagram compatibility
videowise instagram exports/*.mp4

# Check all social platforms
videowise check exports/*.mp4
```

### Learn About Codec Issues
```bash
# Understand why a video fails
videowise learn problematic_video.mp4

# Generate training document
videowise learn samples/ -r --no-color > codec_training.txt
```

### CI/CD Integration
```bash
# JSON output for automation
videowise check assets/video.mp4 --json

# Plain text for logs
videowise casparcg video.mp4 --no-color
```

### Find Compatible Videos
```bash
# Get JSON report
videowise casparcg videos/ -r --json > report.json

# Extract compatible files using jq
jq -r '.results[] | select(.exit_code == 0) | .file' report.json
```

## Exit Codes

- `0`: Compatible (all checks passed)
- `1`: Warnings (may work with issues)
- `2`: Incompatible (will not work)

**For multi-system checks:** Exit code reflects the **worst case** across all systems.

## Output Modes

### Colored Output (Default)
Terminal output uses colors for quick visual scanning:
- ✅ **Green**: Compatible
- ⚠️ **Yellow**: Warning  
- ❌ **Red**: Incompatible
- ℹ️ **Cyan**: Information

### Plain Text (`--no-color`)
Disables colors for CI/CD, logs, and text processing:
```bash
videowise casparcg video.mp4 --no-color
```

### JSON Output (`--json`)
Machine-readable output for automation:
```bash
videowise check video.mp4 --json
```

## Examples

### Quick Checks
```bash
# Live production
videowise casparcg sponsor.mov
videowise vmix lower_third.mp4
videowise resolume vj_loop.mov

# Social media
videowise instagram story.mp4
videowise youtube upload.mp4
videowise tiktok video.mp4

# Browsers
videowise safari web_video.mp4
videowise chrome presentation.webm
```

### Batch Processing
```bash
# Check entire show library
videowise casparcg /media/show-content/ -r

# Check exports for Instagram
videowise instagram exports/ -r --json > report.json

# Find compatible videos
videowise resolume loops/ -r -v
```

### Educational & Training
```bash
# Understand codec issues
videowise learn problem_video.mp4

# Generate team training guide
videowise learn training-samples/ -r --no-color > guide.txt

# Learn about specific system
videowise learn video.mp4  # Checks all systems with explanations
```

### Advanced Usage
```bash
# Check only MP4 files
videowise casparcg videos/ -r -e .mp4

# Verbose with no colors (for logging)
videowise vmix video.mp4 -v --no-color

# Multiple videos with JSON
videowise instagram *.mp4 --json > batch_report.json
```

## Troubleshooting

### "Unable to extract video metadata"
**Solution:** Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### "No video files found"
**Solutions:**
1. Use `--recursive` flag for subdirectories
2. Check file extensions with `--extensions .mp4,.mov`
3. Verify files are actually videos with `ffprobe video.mp4`

### Command not found
**Solution:** Reinstall VideoWise:
```bash
pip install -e .
```

## Getting Help

```bash
# General help
videowise --help

# Command-specific help
videowise check --help
videowise learn --help
videowise casparcg --help

# Version
videowise --version

# List all systems
videowise systems
```

## Migration from Old CLI

If you're used to the old CLI, here's how to update:

**Old:**
```bash
videowise check video.mp4 --system casparcg
videowise batch videos/ --recursive --system instagram
videowise check video.mp4 --system safari --explain
```

**New (simpler!):**
```bash
videowise casparcg video.mp4
videowise instagram videos/ -r
videowise learn video.mp4  # For educational mode
```

**The old syntax still works** for backward compatibility!

## What's Next?

- See [ROADMAP.md](../ROADMAP.md) for upcoming features
- Report issues on [GitHub](https://github.com/KnowOneActual/video-codec-checker/issues)
- Contribute improvements via pull requests
