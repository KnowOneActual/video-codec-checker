# VideoWise Usage Examples

Real-world workflows and use cases for content creators, live production operators, and developers.

## Table of Contents

- [Content Creator Workflows](#content-creator-workflows)
- [Live Production Workflows](#live-production-workflows)
- [Team Training & Education](#team-training--education)
- [CI/CD Integration](#cicd-integration)
- [Automation & Scripting](#automation--scripting)
- [Advanced Workflows](#advanced-workflows)

---

## Content Creator Workflows

### Pre-Upload Social Media Check

Before uploading your edited video to social media platforms:

```bash
# Check if your video is optimized for Instagram and Twitter
videowise check final_edit.mp4 --system instagram -v
videowise check final_edit.mp4 --system twitter -v

# Or check both at once
videowise check final_edit.mp4 --all
```

**Output example:**
```
============================================================
📱 INSTAGRAM
============================================================
⚠️  Instagram may re-encode this video
   Reason: H.264 High Profile detected (Instagram prefers Baseline)
   Suggestion: Consider converting to H.264 Baseline profile to avoid quality loss

============================================================
🐦 TWITTER
============================================================
✅ Video is compatible with Twitter
```

### Browser Compatibility Check

Ensure your video plays in all major browsers before embedding on your website:

```bash
# Check Safari and Chrome compatibility
videowise check promo_video.mp4 --system safari
videowise check promo_video.mp4 --system chrome

# Or check all browsers at once
videowise check promo_video.mp4 --all | grep -A5 "SAFARI\|CHROME"
```

### Batch Export Validation

After exporting multiple videos from your video editor:

```bash
# Check all exports for social media compatibility
videowise batch exports/ --all --json > validation_report.json

# Generate a human-readable report
videowise batch exports/ --all --no-color > exports_report.txt
```

### Learn About Codec Issues

Use educational mode to understand why something doesn't work:

```bash
# Get detailed explanations about compatibility issues
videowise check video.mp4 --system safari --explain
```

This is perfect for:
- Understanding H.264 profiles (Baseline vs Main vs High)
- Learning why certain codecs don't work in browsers
- Training yourself on video codec fundamentals

---

## Live Production Workflows

### Pre-Show Compatibility Check

Check all show content before going live:

```bash
#!/bin/bash
# pre_show_check.sh

echo "🎬 Pre-Show Compatibility Check"
echo "================================"

if videowise batch show-content/ --recursive --all --no-color > pre_show_report.txt; then
    echo "✅ All videos passed!"
    exit 0
else
    echo "⚠️  ATTENTION: Compatibility issues found!"
    echo "Review pre_show_report.txt immediately"
    cat pre_show_report.txt
    exit 1
fi
```

### System-Specific Validation

Check videos for your specific playback system:

```bash
# CasparCG Server
videowise batch graphics/ --recursive --system casparcg

# vMix
videowise batch lower-thirds/ --system vmix

# QLab
videowise batch audio-video-cues/ --system qlab

# ProPresenter
videowise batch worship-media/ --system propresenter --explain
```

### Last-Minute Client Deliveries

Client just sent files 10 minutes before showtime:

```bash
# Quick check for CasparCG compatibility
videowise check urgent_sponsor.mov --system casparcg

# If issues found, check what systems it DOES work with
videowise check urgent_sponsor.mov --all
```

**Exit codes help with decision making:**
- Exit code `0`: Load it, you're good to go
- Exit code `1`: Will work but check the warnings
- Exit code `2`: Don't use it, will fail

### Variable Frame Rate Detection

Screen recordings often have VFR which breaks timing in live production:

```bash
# Check for VFR issues
videowise check screen_recording.mp4 --system casparcg -v

# Batch check all screen recordings
videowise batch recordings/ --system casparcg --json | \
    jq '.results[] | select(.video_info.framerate_mode == "VFR")'
```

### Performance Optimization Check

Ensure videos won't cause performance issues:

```bash
# Check bitrate for vMix (warns at 100Mbps)
videowise check high_quality_video.mov --system vmix -v

# Check for ProRes optimization in QLab
videowise check background_loop.mov --system qlab --explain
```

---

## Team Training & Education

### Generate Training Materials

Create comprehensive codec training guides for your team:

```bash
# Generate educational report with codec explanations
videowise batch training-samples/ \
    --all \
    --explain \
    --no-color > "Team_Codec_Training_$(date +%Y%m%d).txt"
```

This creates a document explaining:
- Why certain codecs work or don't work
- What H.264 profiles mean
- ProRes variants and their uses
- HAP codec advantages for live playback
- VFR vs CFR issues

### Interactive Learning Sessions

Use during training sessions to demonstrate concepts:

```bash
# Show the difference between H.264 profiles
videowise check h264_baseline.mp4 --system instagram --explain
videowise check h264_high.mp4 --system instagram --explain

# Demonstrate ProRes performance benefits
videowise check h264_video.mp4 --system qlab --explain
videowise check prores_proxy.mov --system qlab --explain
```

### Operator Onboarding

New team member? Give them hands-on learning:

```bash
# Create a "What Works, What Doesn't" reference
videowise batch sample-videos/ --system casparcg --explain --no-color > CasparCG_Guide.txt
videowise batch sample-videos/ --system vmix --explain --no-color > vMix_Guide.txt
```

---

## CI/CD Integration

### GitHub Actions Workflow

Automatically check videos on every commit:

```yaml
# .github/workflows/video-compatibility.yml
name: Video Compatibility Check

on:
  push:
    paths:
      - 'assets/videos/**'
      - 'media/**'
  pull_request:
    paths:
      - 'assets/videos/**'
      - 'media/**'

jobs:
  check-compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install FFmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install VideoWise
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Check video compatibility
        run: |
          videowise batch assets/videos/ \
            --recursive \
            --all \
            --no-color \
            --json > compatibility_report.json
      
      - name: Upload compatibility report
        uses: actions/upload-artifact@v3
        with:
          name: compatibility-report
          path: compatibility_report.json
      
      - name: Check for critical issues
        run: |
          if jq -e '.results[] | select(.exit_code == 2)' compatibility_report.json > /dev/null; then
            echo "❌ Incompatible videos found:"
            jq -r '.results[] | select(.exit_code == 2) | "  - \(.file)"' compatibility_report.json
            exit 1
          fi
          
          warning_count=$(jq '[.results[] | select(.exit_code == 1)] | length' compatibility_report.json)
          if [ "$warning_count" -gt 0 ]; then
            echo "⚠️  $warning_count video(s) with warnings (check report)"
          fi
```

### GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate

video-compatibility:
  stage: validate
  image: python:3.11
  before_script:
    - apt-get update && apt-get install -y ffmpeg
    - pip install -r requirements.txt
    - pip install -e .
  script:
    - videowise batch media/ --recursive --all --json > report.json
    - |
      if jq -e '.results[] | select(.exit_code == 2)' report.json > /dev/null; then
        echo "Incompatible videos detected!"
        exit 1
      fi
  artifacts:
    paths:
      - report.json
    expire_in: 30 days
  only:
    changes:
      - media/**
```

### Pre-Commit Hook

Check videos before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking video compatibility..."

# Get list of staged video files
video_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(mp4|mov|avi|mkv)$')

if [ -n "$video_files" ]; then
    echo "Found video files to check:"
    echo "$video_files"
    
    # Check each file
    for file in $video_files; do
        if [ -f "$file" ]; then
            echo "Checking $file..."
            if ! videowise check "$file" --all --no-color; then
                echo "❌ Video compatibility issues found in $file"
                echo "Run 'videowise check $file --all' for details"
                exit 1
            fi
        fi
    done
    
    echo "✅ All videos passed compatibility checks"
fi

exit 0
```

---

## Automation & Scripting

### Watch Folder Monitor

Automatically check videos as they arrive:

```bash
#!/bin/bash
# watch_folder.sh

WATCH_DIR="/media/incoming/"
LOG_FILE="video_checks.log"

echo "Monitoring $WATCH_DIR for new videos..."

# Using inotifywait (Linux) or fswatch (macOS)
fswatch -0 "$WATCH_DIR" | while read -d "" event; do
    if [[ "$event" =~ \.(mp4|mov|avi|mkv)$ ]]; then
        echo "[$(date)] New video detected: $event" | tee -a "$LOG_FILE"
        
        videowise check "$event" --all --json > "${event}.compatibility.json"
        
        if [ $? -eq 0 ]; then
            echo "[$(date)] ✅ $event: Compatible" | tee -a "$LOG_FILE"
        elif [ $? -eq 1 ]; then
            echo "[$(date)] ⚠️  $event: Warnings" | tee -a "$LOG_FILE"
        else
            echo "[$(date)] ❌ $event: Incompatible" | tee -a "$LOG_FILE"
        fi
    fi
done
```

### Automated Re-Encoding Workflow

Check compatibility and trigger re-encoding if needed:

```bash
#!/bin/bash
# auto_convert.sh

INPUT_FILE="$1"
SYSTEM="${2:-casparcg}"

echo "Checking $INPUT_FILE for $SYSTEM compatibility..."

if videowise check "$INPUT_FILE" --system "$SYSTEM" --json > check.json; then
    echo "✅ Already compatible!"
    exit 0
else
    echo "⚠️  Compatibility issues found. Re-encoding..."
    
    # Extract recommended settings (you would parse the JSON output)
    # For CasparCG, convert to H.264 MP4
    OUTPUT_FILE="${INPUT_FILE%.*}_converted.mp4"
    
    ffmpeg -i "$INPUT_FILE" \
        -c:v libx264 \
        -profile:v high \
        -level 4.2 \
        -pix_fmt yuv420p \
        -r 30 \
        -c:a aac \
        -b:a 192k \
        "$OUTPUT_FILE"
    
    # Verify the converted file
    if videowise check "$OUTPUT_FILE" --system "$SYSTEM"; then
        echo "✅ Conversion successful!"
    else
        echo "❌ Conversion failed compatibility check"
        exit 1
    fi
fi
```

### Batch Report Generation

Generate daily/weekly reports:

```bash
#!/bin/bash
# generate_report.sh

REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="compatibility_report_${REPORT_DATE}.html"

echo "Generating compatibility report for $REPORT_DATE..."

# Check all videos
videowise batch /media/library/ \
    --recursive \
    --all \
    --json > report_data.json

# Generate HTML report (using jq and basic HTML)
cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Video Compatibility Report - $REPORT_DATE</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .compatible { color: green; }
        .warning { color: orange; }
        .incompatible { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Video Compatibility Report</h1>
    <h2>Generated: $REPORT_DATE</h2>
    
    <h3>Summary</h3>
    <ul>
        <li>Total Files: $(jq '.total_files' report_data.json)</li>
        <li class="compatible">Compatible: $(jq '[.results[] | select(.exit_code == 0)] | length' report_data.json)</li>
        <li class="warning">Warnings: $(jq '[.results[] | select(.exit_code == 1)] | length' report_data.json)</li>
        <li class="incompatible">Incompatible: $(jq '[.results[] | select(.exit_code == 2)] | length' report_data.json)</li>
    </ul>
    
    <h3>Detailed Results</h3>
    <table>
        <tr>
            <th>File</th>
            <th>Status</th>
            <th>Issues</th>
        </tr>
EOF

# Add table rows (simplified)
jq -r '.results[] | "<tr><td>\(.file)</td><td>\(.exit_code)</td><td>Issues here</td></tr>"' report_data.json >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF
    </table>
</body>
</html>
EOF

echo "Report generated: $REPORT_FILE"
```

### Python Integration

Use VideoWise in your Python scripts:

```python
#!/usr/bin/env python3
# check_media.py

import sys
import json
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

def check_video_for_system(video_path, system):
    """Check a video file for compatibility with a system."""
    try:
        analyzer = VideoAnalyzer(video_path)
        video_info = get_video_info(analyzer)
        issues = check_compatibility(video_info, system)
        
        return {
            'file': str(video_path),
            'system': system,
            'issues': [str(issue) for issue in issues],
            'compatible': all(issue.level == 'compatible' for issue in issues)
        }
    except Exception as e:
        return {
            'file': str(video_path),
            'system': system,
            'error': str(e)
        }

def main():
    media_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    system = sys.argv[2] if len(sys.argv) > 2 else 'casparcg'
    
    results = []
    for video_file in media_dir.glob('*.mp4'):
        result = check_video_for_system(video_file, system)
        results.append(result)
        
        if result.get('compatible'):
            print(f"✅ {video_file.name}")
        else:
            print(f"❌ {video_file.name}")
    
    # Save results
    with open('batch_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
```

---

## Advanced Workflows

### Multi-System Validation Matrix

Check specific videos against specific systems:

```bash
#!/bin/bash
# validation_matrix.sh

# Define systems to check
SYSTEMS=("casparcg" "vmix" "obs")

# Define critical videos
VIDEOS=(
    "opening_animation.mov"
    "sponsor_lower_third.mp4"
    "closing_credits.mov"
)

echo "Validation Matrix"
echo "================="

for video in "${VIDEOS[@]}"; do
    echo "
Video: $video"
    for system in "${SYSTEMS[@]}"; do
        if videowise check "$video" --system "$system" --no-color > /dev/null 2>&1; then
            echo "  ✅ $system"
        else
            echo "  ❌ $system"
        fi
    done
done
```

### Performance Benchmarking

Compare different codec options:

```bash
#!/bin/bash
# benchmark_codecs.sh

echo "Codec Performance Comparison"
echo "============================"

for codec_file in codecs/*.mov; do
    echo "
File: $(basename "$codec_file")"
    
    # Get file size
    size=$(du -h "$codec_file" | cut -f1)
    echo "  Size: $size"
    
    # Check QLab performance (ProRes is best)
    videowise check "$codec_file" --system qlab -v | grep -E "codec|bitrate|ProRes"
    
    # Check vMix bitrate warnings
    videowise check "$codec_file" --system vmix -v | grep -i "bitrate"
done
```

### Conditional Workflow Based on Compatibility

```bash
#!/bin/bash
# conditional_workflow.sh

VIDEO="$1"

echo "Analyzing $VIDEO..."

# Check compatibility and get JSON output
videowise check "$VIDEO" --all --json > results.json

# Count compatible systems
compatible_count=$(jq '[.results[] | select(.issues[0].level == "compatible")] | length' results.json)

echo "Compatible with $compatible_count out of 9 systems"

if [ "$compatible_count" -eq 9 ]; then
    echo "✅ Universal compatibility - upload to asset library"
    cp "$VIDEO" /media/library/universal/
elif [ "$compatible_count" -ge 5 ]; then
    echo "⚠️  Partial compatibility - mark as limited use"
    cp "$VIDEO" /media/library/limited/
else
    echo "❌ Poor compatibility - needs re-encoding"
    mv "$VIDEO" /media/library/needs-conversion/
fi
```

### Integration with Asset Management

```python
#!/usr/bin/env python3
# asset_management_integration.py

import json
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

class AssetManager:
    def __init__(self, asset_db_path):
        self.db_path = Path(asset_db_path)
        self.assets = self.load_db()
    
    def load_db(self):
        if self.db_path.exists():
            with open(self.db_path) as f:
                return json.load(f)
        return {}
    
    def save_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.assets, f, indent=2)
    
    def add_asset(self, video_path, systems_to_check):
        """Add a video to the asset database with compatibility info."""
        analyzer = VideoAnalyzer(video_path)
        video_info = get_video_info(analyzer)
        
        compatibility = {}
        for system in systems_to_check:
            issues = check_compatibility(video_info, system)
            compatibility[system] = {
                'compatible': all(i.level == 'compatible' for i in issues),
                'warnings': [str(i) for i in issues if i.level == 'warning'],
                'errors': [str(i) for i in issues if i.level == 'incompatible']
            }
        
        self.assets[str(video_path)] = {
            'codec': video_info['codec'],
            'container': video_info['container'],
            'resolution': f"{video_info['width']}x{video_info['height']}",
            'compatibility': compatibility,
            'tags': self.generate_tags(compatibility)
        }
        
        self.save_db()
    
    def generate_tags(self, compatibility):
        """Auto-generate tags based on compatibility."""
        tags = []
        
        if all(c['compatible'] for c in compatibility.values()):
            tags.append('universal')
        
        for system, compat in compatibility.items():
            if compat['compatible']:
                tags.append(f'{system}-ready')
        
        return tags
    
    def find_compatible_assets(self, system):
        """Find all assets compatible with a system."""
        return [
            path for path, info in self.assets.items()
            if info['compatibility'].get(system, {}).get('compatible', False)
        ]

if __name__ == '__main__':
    manager = AssetManager('asset_database.json')
    
    # Add new assets
    for video in Path('media/').glob('*.mp4'):
        manager.add_asset(video, ['casparcg', 'vmix', 'obs'])
    
    # Find CasparCG-compatible videos
    compatible = manager.find_compatible_assets('casparcg')
    print(f"Found {len(compatible)} CasparCG-compatible videos")
```

---

## Tips & Best Practices

### Use JSON for Automation

Always use `--json` flag when scripting:

```bash
videowise check video.mp4 --all --json > result.json
```

This provides structured output that's easy to parse with `jq` or in scripts.

### Combine Flags Effectively

```bash
# Educational report without colors (perfect for documentation)
videowise check video.mp4 --all --explain --no-color > report.txt

# Batch processing with explanations for training
videowise batch videos/ --recursive --all --explain --no-color > training.txt
```

### Use Exit Codes in Scripts

```bash
if videowise check video.mp4 --system casparcg; then
    echo "Load into CasparCG"
else
    echo "Don't use this file"
fi
```

### Regular Validation

Schedule regular checks with cron:

```bash
# Check media library every night at 2 AM
0 2 * * * /usr/local/bin/videowise batch /media/library/ --recursive --all --json > /var/log/videowise/daily_$(date +\%Y\%m\%d).json
```

### Document Your Workflows

Generate documentation from actual checks:

```bash
# Create a "What Works" guide
videowise batch sample-codecs/ --all --explain --no-color > docs/CODEC_COMPATIBILITY.md
```

---

Need more examples? [Open an issue](https://github.com/KnowOneActual/video-codec-checker/issues) with your use case!
