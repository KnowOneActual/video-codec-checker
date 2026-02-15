# VideoWise Python API Reference

Documentation for using VideoWise as a Python library in your own projects.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Modules](#core-modules)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Advanced Usage](#advanced-usage)

---

## Installation

```bash
# Clone and install
git clone https://github.com/KnowOneActual/video-codec-checker.git
cd video-codec-checker
pip install -e .
```

## Quick Start

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

# Analyze a video file
analyzer = VideoAnalyzer('video.mp4')
video_info = get_video_info(analyzer)

# Check compatibility with a system
issues = check_compatibility(video_info, 'casparcg')

# Print results
for issue in issues:
    print(f"{issue.level.upper()}: {issue.message}")
```

---

## Core Modules

### `videowise.analyzer`

Handles video file analysis and metadata extraction using FFprobe.

### `videowise.compatibility`

Contains the compatibility checking engine and rules for all supported systems.

### `videowise.utils`

Utility functions for working with video information.

### `videowise.formatter`

Formatting utilities for displaying compatibility results.

---

## API Reference

### VideoAnalyzer

**Class:** `videowise.analyzer.VideoAnalyzer`

Analyzes video files and extracts metadata using FFprobe.

#### Constructor

```python
VideoAnalyzer(file_path: str)
```

**Parameters:**
- `file_path` (str): Path to the video file to analyze

**Raises:**
- `FileNotFoundError`: If the file doesn't exist
- `ValueError`: If the file is not a valid video file

#### Methods

##### `analyze()`

```python
analyzer.analyze() -> Dict[str, Any]
```

Runs FFprobe and extracts metadata.

**Returns:**
- Dictionary containing raw FFprobe output

**Raises:**
- `RuntimeError`: If FFprobe fails to analyze the file

#### Example

```python
from videowise.analyzer import VideoAnalyzer

try:
    analyzer = VideoAnalyzer('video.mp4')
    metadata = analyzer.analyze()
    print(f"Codec: {metadata.get('codec_name')}")
except FileNotFoundError:
    print("Video file not found")
except ValueError as e:
    print(f"Invalid video file: {e}")
```

---

### get_video_info

**Function:** `videowise.utils.get_video_info`

Extracts structured video information from a VideoAnalyzer instance.

```python
get_video_info(analyzer: VideoAnalyzer) -> Dict[str, Any]
```

**Parameters:**
- `analyzer` (VideoAnalyzer): Initialized VideoAnalyzer instance

**Returns:**
- Dictionary with standardized video information:
  - `codec` (str): Video codec (e.g., 'h264', 'prores', 'vp9')
  - `profile` (str): Codec profile (e.g., 'High', 'Main', 'Baseline')
  - `container` (str): Container format (e.g., 'mp4', 'mov', 'mkv')
  - `width` (int): Video width in pixels
  - `height` (int): Video height in pixels
  - `framerate` (float): Frame rate (fps)
  - `framerate_mode` (str): 'CFR' (constant) or 'VFR' (variable)
  - `bitrate` (int): Bitrate in bits per second
  - `file_size` (int): File size in bytes
  - `duration` (float): Duration in seconds
  - `has_audio` (bool): Whether the file contains audio

#### Example

```python
from videowise.analyzer import VideoAnalyzer
from videowise.utils import get_video_info

analyzer = VideoAnalyzer('video.mp4')
info = get_video_info(analyzer)

print(f"Codec: {info['codec']}")
print(f"Resolution: {info['width']}x{info['height']}")
print(f"Bitrate: {info['bitrate'] / 1_000_000:.2f} Mbps")
print(f"Frame Rate Mode: {info['framerate_mode']}")
```

---

### check_compatibility

**Function:** `videowise.compatibility.check_compatibility`

Checks video compatibility with a specific system.

```python
check_compatibility(
    video_info: Dict[str, Any],
    system: str
) -> List[Issue]
```

**Parameters:**
- `video_info` (dict): Video information from `get_video_info()`
- `system` (str): System to check against. Valid options:
  - Live Production: `'casparcg'`, `'vmix'`, `'obs'`, `'qlab'`, `'propresenter'`
  - Browsers: `'safari'`, `'chrome'`
  - Social Media: `'instagram'`, `'twitter'`

**Returns:**
- List of `Issue` objects. If list is empty, the video is fully compatible.

#### Issue Object

```python
class Issue:
    level: str          # 'compatible', 'warning', or 'incompatible'
    message: str        # Human-readable issue description
    reason: str         # Why this is an issue
    suggestion: str     # How to fix the issue
```

#### Example

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

analyzer = VideoAnalyzer('video.mp4')
info = get_video_info(analyzer)

# Check CasparCG compatibility
issues = check_compatibility(info, 'casparcg')

if not issues:
    print("Video is fully compatible!")
else:
    for issue in issues:
        print(f"{issue.level.upper()}: {issue.message}")
        print(f"  Reason: {issue.reason}")
        print(f"  Fix: {issue.suggestion}")
```

---

### ExplanationFormatter

**Class:** `videowise.formatter.ExplanationFormatter`

Formats compatibility issues with optional educational explanations.

#### Constructor

```python
ExplanationFormatter(
    use_color: bool = True,
    explain_mode: bool = False
)
```

**Parameters:**
- `use_color` (bool): Enable ANSI color codes in output (default: True)
- `explain_mode` (bool): Include educational explanations (default: False)

#### Methods

##### `format_issue()`

```python
formatter.format_issue(
    issue: Issue,
    system: str
) -> str
```

Formats a single issue for display.

**Parameters:**
- `issue` (Issue): Issue object to format
- `system` (str): System name for context

**Returns:**
- Formatted string with issue details

##### `format_all_issues()`

```python
formatter.format_all_issues(
    issues: List[Issue],
    system: str,
    video_file: str
) -> str
```

Formats all issues for a video/system combination.

#### Example

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info
from videowise.formatter import ExplanationFormatter

analyzer = VideoAnalyzer('video.mp4')
info = get_video_info(analyzer)
issues = check_compatibility(info, 'safari')

# Format with colors and explanations
formatter = ExplanationFormatter(use_color=True, explain_mode=True)
output = formatter.format_all_issues(issues, 'safari', 'video.mp4')
print(output)

# Format for plain text (CI/CD)
plain_formatter = ExplanationFormatter(use_color=False, explain_mode=False)
plain_output = plain_formatter.format_all_issues(issues, 'safari', 'video.mp4')
print(plain_output)
```

---

## Usage Examples

### Basic Compatibility Check

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

def check_video(file_path, system):
    """Check if a video is compatible with a system."""
    try:
        analyzer = VideoAnalyzer(file_path)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, system)
        
        if not issues:
            return True, "Compatible"
        
        # Check severity
        has_errors = any(i.level == 'incompatible' for i in issues)
        has_warnings = any(i.level == 'warning' for i in issues)
        
        if has_errors:
            return False, "Incompatible"
        elif has_warnings:
            return True, "Compatible with warnings"
        
        return True, "Compatible"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

# Usage
compatible, status = check_video('video.mp4', 'casparcg')
print(f"Status: {status}")
```

### Check Multiple Systems

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

SYSTEMS = ['casparcg', 'vmix', 'obs', 'qlab', 'propresenter',
           'safari', 'chrome', 'instagram', 'twitter']

def check_all_systems(file_path):
    """Check a video against all systems."""
    analyzer = VideoAnalyzer(file_path)
    info = get_video_info(analyzer)
    
    results = {}
    for system in SYSTEMS:
        issues = check_compatibility(info, system)
        results[system] = {
            'compatible': not any(i.level == 'incompatible' for i in issues),
            'warnings': [i for i in issues if i.level == 'warning'],
            'errors': [i for i in issues if i.level == 'incompatible']
        }
    
    return results

# Usage
results = check_all_systems('video.mp4')
for system, result in results.items():
    status = "✅" if result['compatible'] else "❌"
    print(f"{status} {system}")
```

### Batch Processing

```python
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

def batch_check(directory, system, recursive=True):
    """Check all videos in a directory."""
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']
    
    dir_path = Path(directory)
    pattern = '**/*' if recursive else '*'
    
    results = []
    for file_path in dir_path.glob(pattern):
        if file_path.suffix.lower() in video_extensions:
            try:
                analyzer = VideoAnalyzer(str(file_path))
                info = get_video_info(analyzer)
                issues = check_compatibility(info, system)
                
                results.append({
                    'file': str(file_path),
                    'compatible': not any(i.level == 'incompatible' for i in issues),
                    'issues': [str(i.message) for i in issues]
                })
            except Exception as e:
                results.append({
                    'file': str(file_path),
                    'error': str(e)
                })
    
    return results

# Usage
results = batch_check('videos/', 'casparcg', recursive=True)
compatible = sum(1 for r in results if r.get('compatible', False))
print(f"Compatible: {compatible}/{len(results)}")
```

### Custom Compatibility Rules

```python
from videowise.analyzer import VideoAnalyzer
from videowise.utils import get_video_info

def check_custom_requirements(file_path):
    """Check video against custom requirements."""
    analyzer = VideoAnalyzer(file_path)
    info = get_video_info(analyzer)
    
    issues = []
    
    # Require H.264 codec
    if info['codec'] != 'h264':
        issues.append(f"Requires H.264, got {info['codec']}")
    
    # Require 1080p or higher
    if info['height'] < 1080:
        issues.append(f"Requires 1080p minimum, got {info['height']}p")
    
    # Require constant frame rate
    if info['framerate_mode'] == 'VFR':
        issues.append("Variable frame rate not allowed")
    
    # Bitrate limit (50 Mbps)
    if info['bitrate'] > 50_000_000:
        mbps = info['bitrate'] / 1_000_000
        issues.append(f"Bitrate too high: {mbps:.2f} Mbps (max 50 Mbps)")
    
    return issues

# Usage
issues = check_custom_requirements('video.mp4')
if not issues:
    print("Meets all requirements")
else:
    print("Issues found:")
    for issue in issues:
        print(f"  - {issue}")
```

### Integration with Django

```python
# models.py
from django.db import models
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info
import json

class VideoAsset(models.Model):
    file = models.FileField(upload_to='videos/')
    codec = models.CharField(max_length=50, blank=True)
    resolution = models.CharField(max_length=20, blank=True)
    compatibility_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def analyze(self):
        """Analyze video and store compatibility data."""
        analyzer = VideoAnalyzer(self.file.path)
        info = get_video_info(analyzer)
        
        # Store basic info
        self.codec = info['codec']
        self.resolution = f"{info['width']}x{info['height']}"
        
        # Check compatibility with key systems
        systems = ['casparcg', 'safari', 'instagram']
        compat_data = {}
        
        for system in systems:
            issues = check_compatibility(info, system)
            compat_data[system] = {
                'compatible': not any(i.level == 'incompatible' for i in issues),
                'issues': [i.message for i in issues]
            }
        
        self.compatibility_data = compat_data
        self.save()
    
    def is_compatible_with(self, system):
        """Check if video is compatible with a system."""
        return self.compatibility_data.get(system, {}).get('compatible', False)

# views.py
from django.shortcuts import render
from .models import VideoAsset

def upload_video(request):
    if request.method == 'POST':
        video = VideoAsset(file=request.FILES['video'])
        video.save()
        
        try:
            video.analyze()
            return render(request, 'success.html', {'video': video})
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
    
    return render(request, 'upload.html')
```

### Integration with Flask

```python
from flask import Flask, request, jsonify
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'

@app.route('/api/check', methods=['POST'])
def check_video():
    """API endpoint to check video compatibility."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    system = request.form.get('system', 'casparcg')
    
    # Save temporarily
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        # Analyze
        analyzer = VideoAnalyzer(filepath)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, system)
        
        # Build response
        response = {
            'file': file.filename,
            'video_info': {
                'codec': info['codec'],
                'resolution': f"{info['width']}x{info['height']}",
                'bitrate_mbps': info['bitrate'] / 1_000_000
            },
            'system': system,
            'compatible': not any(i.level == 'incompatible' for i in issues),
            'issues': [
                {
                    'level': i.level,
                    'message': i.message,
                    'suggestion': i.suggestion
                }
                for i in issues
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Advanced Usage

### Custom Issue Class

Create your own issue types:

```python
from dataclasses import dataclass

@dataclass
class CustomIssue:
    level: str
    category: str
    message: str
    technical_details: dict
    fix_command: str = ""

def advanced_check(video_info, system):
    """Custom compatibility check with additional context."""
    issues = []
    
    if video_info['codec'] == 'vp9' and system == 'safari':
        issues.append(CustomIssue(
            level='incompatible',
            category='codec',
            message='VP9 not supported in Safari',
            technical_details={
                'current_codec': 'vp9',
                'required_codecs': ['h264', 'hevc'],
                'browser': 'Safari'
            },
            fix_command='ffmpeg -i input.mp4 -c:v libx264 output.mp4'
        ))
    
    return issues
```

### Async Processing

Use asyncio for parallel processing:

```python
import asyncio
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

async def check_video_async(file_path, system):
    """Async video check (I/O bound operation)."""
    loop = asyncio.get_event_loop()
    
    # Run blocking operations in executor
    analyzer = await loop.run_in_executor(None, VideoAnalyzer, file_path)
    info = await loop.run_in_executor(None, get_video_info, analyzer)
    issues = await loop.run_in_executor(None, check_compatibility, info, system)
    
    return {
        'file': file_path,
        'system': system,
        'compatible': not any(i.level == 'incompatible' for i in issues)
    }

async def batch_check_async(directory, system):
    """Check multiple videos in parallel."""
    video_files = list(Path(directory).glob('*.mp4'))
    
    tasks = [check_video_async(str(f), system) for f in video_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

# Usage
results = asyncio.run(batch_check_async('videos/', 'casparcg'))
for result in results:
    if isinstance(result, Exception):
        print(f"Error: {result}")
    else:
        print(f"{result['file']}: {result['compatible']}")
```

### Caching Results

Cache analysis results to avoid re-processing:

```python
import json
import hashlib
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.utils import get_video_info

class CachedAnalyzer:
    def __init__(self, cache_dir='.videowise_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, file_path):
        """Generate cache key from file path and modification time."""
        stat = Path(file_path).stat()
        key_data = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_info(self, file_path):
        """Get cached video info if available."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        return None
    
    def cache_info(self, file_path, info):
        """Cache video info."""
        cache_key = self.get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(info, f)
    
    def get_video_info(self, file_path):
        """Get video info with caching."""
        # Check cache first
        cached = self.get_cached_info(file_path)
        if cached:
            return cached
        
        # Analyze and cache
        analyzer = VideoAnalyzer(file_path)
        info = get_video_info(analyzer)
        self.cache_info(file_path, info)
        
        return info

# Usage
cached_analyzer = CachedAnalyzer()
info = cached_analyzer.get_video_info('video.mp4')  # Analyzes
info = cached_analyzer.get_video_info('video.mp4')  # Uses cache
```

---

## Error Handling

### Robust Error Handling

```python
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

def safe_check(file_path, system):
    """Check video with comprehensive error handling."""
    try:
        analyzer = VideoAnalyzer(file_path)
    except FileNotFoundError:
        return {'error': 'File not found', 'code': 'FILE_NOT_FOUND'}
    except ValueError as e:
        return {'error': f'Invalid file: {str(e)}', 'code': 'INVALID_FILE'}
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}', 'code': 'ANALYSIS_ERROR'}
    
    try:
        info = get_video_info(analyzer)
    except KeyError as e:
        return {'error': f'Missing metadata: {str(e)}', 'code': 'METADATA_ERROR'}
    except Exception as e:
        return {'error': f'Info extraction failed: {str(e)}', 'code': 'EXTRACTION_ERROR'}
    
    try:
        issues = check_compatibility(info, system)
        return {
            'success': True,
            'compatible': not any(i.level == 'incompatible' for i in issues),
            'issues': [{'level': i.level, 'message': i.message} for i in issues]
        }
    except Exception as e:
        return {'error': f'Compatibility check failed: {str(e)}', 'code': 'CHECK_ERROR'}

# Usage
result = safe_check('video.mp4', 'casparcg')
if 'error' in result:
    print(f"Error ({result['code']}): {result['error']}")
else:
    print(f"Compatible: {result['compatible']}")
```

---

## Performance Considerations

### Parallel Processing

For large batches, use multiprocessing:

```python
from multiprocessing import Pool
from pathlib import Path
from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility
from videowise.utils import get_video_info

def check_single(args):
    """Check a single video (must be top-level function for pickling)."""
    file_path, system = args
    try:
        analyzer = VideoAnalyzer(file_path)
        info = get_video_info(analyzer)
        issues = check_compatibility(info, system)
        return (file_path, not any(i.level == 'incompatible' for i in issues))
    except Exception as e:
        return (file_path, f"Error: {e}")

def batch_check_parallel(directory, system, workers=4):
    """Check videos in parallel using multiprocessing."""
    video_files = [str(f) for f in Path(directory).glob('*.mp4')]
    args = [(f, system) for f in video_files]
    
    with Pool(workers) as pool:
        results = pool.map(check_single, args)
    
    return results

# Usage
results = batch_check_parallel('videos/', 'casparcg', workers=4)
for file_path, compatible in results:
    print(f"{file_path}: {compatible}")
```

---

For more examples, see [EXAMPLES.md](EXAMPLES.md).
