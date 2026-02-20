# Phase 2 Architecture Refactoring Guide

## Overview

This document describes the Phase 2 refactoring that transforms VideoWise from a class-based checker system to a rule-based engine using declarative YAML configurations.

## Why This Refactoring?

### Problems with Original Architecture

**Before (Old System):**
- **78KB** of compatibility.py with 31 individual checker classes
- **38KB** of editing_platforms.py with 5 more checker classes  
- Each new system required 50-200 lines of repetitive Python code
- 90% code duplication across similar systems
- Hard to maintain and extend
- Contributors needed Python expertise to add systems

**After (New System):**
- **~30KB** total for rule engine + API wrapper
- **10KB** YAML file with all system definitions
- New systems require 5-10 lines of YAML
- Zero code duplication
- Easy to maintain and extend
- Contributors can add systems with just YAML knowledge

### Concrete Benefits

1. **80% Less Code**: From 116KB to ~40KB total
2. **10x Easier to Add Systems**: YAML vs Python classes
3. **100% Backward Compatible**: Existing code works unchanged
4. **Data-Driven**: Rules in YAML, not hardcoded logic
5. **Community-Friendly**: Non-coders can contribute system profiles

## Architecture Components

### 1. System Profiles (`videowise/systems/profiles.yaml`)

Declarative YAML definitions for all 31+ systems. Example:

```yaml
live_production:
  casparcg:
    name: "CasparCG Server"
    category: "live_production"
    codecs:
      optimal: ["hap", "hap_alpha", "notchlc"]
      recommended: ["prores", "dnxhd"]
      supported: ["h264"]
    containers:
      preferred: ["mov", "mp4"]
    rules:
      - codec: "hap"
        level: "compatible"
        message: "HAP codec provides GPU-accelerated playback"
      - condition: "resolution[0] >= 3840 and bitrate > 200000000"
        level: "warning"
        message: "4K at high bitrate may stress system"
        suggestion: "Consider HAP codec for GPU acceleration"
```

### 2. Rule Engine (`videowise/rule_engine.py`)

Core evaluation engine that:
- Loads YAML profiles
- Evaluates codec/container compatibility
- Executes conditional rules (e.g., `bitrate > 100000000`)
- Checks limits (file size, resolution, duration)
- Returns `CompatibilityIssue` objects

### 3. Compatibility API (`videowise/compatibility_v2.py`)

Backward-compatible wrapper that:
- Maintains existing class-based API
- Internally delegates to rule engine
- Zero breaking changes for existing code

## Key Features

### 1. Declarative Codec Tiers

```yaml
codecs:
  optimal: ["hap", "prores"]      # Best performance
  recommended: ["dnxhd", "h264"]  # Good compatibility
  supported: ["mpeg2video"]        # Works but not ideal
```

Engine automatically generates appropriate messages based on tier.

### 2. Conditional Rules

Supports Python expressions:

```yaml
rules:
  - condition: "codec == 'h264' and profile != 'baseline'"
    level: "warning"
    message: "Instagram prefers H.264 Baseline profile"
    suggestion: "Convert to Baseline profile"
  
  - condition: "resolution[0] >= 3840 or bitrate > 100000000"
    level: "warning"
    message: "4K or high bitrate may require proxies"
```

Available variables:
- `codec`: Video codec (e.g., "h264", "prores")
- `container`: Container format (e.g., "mp4", "mov")
- `bitrate`: Bitrate in bits per second
- `resolution`: Tuple `(width, height)`
- `frame_rate`: Frame rate (float or string)
- `profile`: Codec profile (e.g., "baseline", "high")
- `file_size`: File size in bytes

### 3. System Variants

Single system with multiple configurations:

```yaml
playoutbee:
  codecs:
    optimal: ["hap"]
  variants:
    desktop:
      # Desktop-specific rules
    raspberrypi:
      rules:
        - condition: "bitrate > 50000000"
          level: "warning"
          message: "High bitrate may overwhelm Raspberry Pi"
```

Usage:
```python
checker = PlayoutBeeChecker(platform="raspberrypi")
issues = checker.check(video_info)
```

### 4. Limits and Constraints

```yaml
limits:
  max_file_size: 104857600  # 100MB
  max_duration: 60  # seconds
  max_resolution: [1080, 1920]
  optimal_bitrate_range: [8000000, 15000000]  # 8-15 Mbps
```

Engine automatically validates and generates warnings.

## Migration Path

### For End Users (Zero Changes)

Existing code continues to work:

```python
# This still works exactly the same
from videowise.compatibility import CasparCGChecker

checker = CasparCGChecker()
issues = checker.check(video_info)
```

### For Contributors (Simplified)

**Old Way (50-200 lines of Python):**

```python
class NewSystemChecker(CompatibilityChecker):
    SUPPORTED_CODECS = {"h264", "prores"}
    
    def check(self, video_info):
        issues = []
        codec = video_info.get("codec", "").lower()
        
        if codec not in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(...))
        # ... 30+ more lines ...
        return issues
```

**New Way (5-10 lines of YAML):**

```yaml
newsystem:
  name: "New System"
  category: "live_production"
  codecs:
    optimal: ["prores"]
    supported: ["h264"]
  containers:
    preferred: ["mov"]
```

## Adding a New System

### Step 1: Add to `profiles.yaml`

```yaml
category_name:
  system_key:
    name: "Display Name"
    category: "live_production|editing|social_media|browser|streaming"
    codecs:
      optimal: ["best_codec"]
      recommended: ["good_codec"]
      supported: ["basic_codec"]
    containers:
      preferred: ["mov", "mp4"]
    rules:
      - codec: "specific_codec"
        level: "compatible"
        message: "Helpful message"
```

### Step 2: Add Wrapper Class (Optional)

For backward compatibility or custom initialization:

```python
# In compatibility_v2.py
class NewSystemChecker(CompatibilityChecker):
    system_name = "newsystem"
    
    def __init__(self, custom_param: str = "default"):
        super().__init__()
        self.custom_param = custom_param
```

### Step 3: Test

```python
from videowise.rule_engine import RuleEngine

engine = RuleEngine()
issues = engine.check_compatibility(
    {"codec": "h264", "container": "mp4"},
    "newsystem"
)
print(issues)
```

## Rule Engine API

### Direct Usage

```python
from videowise.rule_engine import RuleEngine

engine = RuleEngine()

# Check compatibility
issues = engine.check_compatibility(
    video_info={"codec": "h264", "bitrate": 50000000},
    system="casparcg",
    variant=None  # Optional variant
)

# List all systems
systems = engine.list_systems()
print(systems)  # ['avid', 'casparcg', 'chrome', ...]

# Get system info
info = engine.get_system_info("davinci")
print(info)
# {
#   'name': 'DaVinci Resolve',
#   'category': 'editing',
#   'variants': ['free', 'studio'],
#   'optimal_codecs': ['dnxhd', 'dnxhr', 'prores']
# }
```

### Backward-Compatible API

```python
from videowise.compatibility_v2 import (
    CasparCGChecker,
    check_compatibility,
    get_available_systems
)

# Class-based (existing code)
checker = CasparCGChecker()
issues = checker.check(video_info)

# Function-based (new simplified API)
issues = check_compatibility(video_info, "casparcg")

# List systems
systems = get_available_systems()
```

## Advanced Rule Examples

### Complex Conditions

```yaml
rules:
  # Multiple conditions with AND
  - condition: "codec == 'h264' and resolution[0] >= 3840 and bitrate > 100000000"
    level: "warning"
    message: "4K H.264 at high bitrate may cause stuttering"
  
  # List membership check
  - condition: "codec in ['h264', 'hevc'] and profile == 'high'"
    level: "compatible"
    message: "High Profile provides best quality"
  
  # Resolution-based logic
  - condition: "resolution[0] > 1920 or resolution[1] > 1080"
    level: "warning"
    message: "Resolution exceeds 1080p"
    suggestion: "Downscale to 1080p for this platform"
```

### Platform-Specific Variants

```yaml
finalcut:
  codecs:
    optimal: ["prores"]
  variants:
    mac_apple_silicon:
      rules:
        - codec: "prores"
          message: "Hardware acceleration on M-series chips"
    mac_intel:
      rules:
        - codec: "prores"
          message: "Native ProRes support on Intel Mac"
```

### Profile-Based Checks

```yaml
instagram:
  codecs:
    optimal: ["h264"]
    profile_preferred: "baseline"
  rules:
    - condition: "codec == 'h264' and profile != 'baseline'"
      level: "warning"
      message: "Non-Baseline profiles will be re-encoded"
      suggestion: "Convert to Baseline profile"
```

## Testing

### Unit Tests

```python
import pytest
from videowise.rule_engine import RuleEngine
from videowise.compatibility import CompatibilityLevel

def test_casparcg_hap_codec():
    engine = RuleEngine()
    issues = engine.check_compatibility(
        {"codec": "hap", "container": "mov"},
        "casparcg"
    )
    
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("GPU-accelerated" in issue.message for issue in issues)

def test_conditional_rule_evaluation():
    engine = RuleEngine()
    issues = engine.check_compatibility(
        {
            "codec": "h264",
            "resolution": (3840, 2160),
            "bitrate": 250000000
        },
        "casparcg"
    )
    
    # Should trigger 4K high bitrate warning
    assert any("4K" in issue.message for issue in issues)
```

### Integration Tests

```python
def test_backward_compatibility():
    """Ensure old API still works."""
    from videowise.compatibility_v2 import CasparCGChecker
    
    checker = CasparCGChecker(version="2.3")
    issues = checker.check({"codec": "hap", "container": "mov"})
    
    assert len(issues) > 0
    assert issues[0].level == CompatibilityLevel.COMPATIBLE
```

## Performance Comparison

| Metric | Old System | New System | Improvement |
|--------|-----------|------------|-------------|
| Lines of Code | 3,500+ | ~1,200 | **66% reduction** |
| Add New System | 50-200 LOC | 5-10 lines YAML | **10x faster** |
| Code Duplication | ~90% | ~0% | **Eliminated** |
| Startup Time | Same | Same | No regression |
| Check Performance | Same | Same | No regression |
| Contributor Barrier | Python required | YAML only | **Much lower** |

## Deployment

### Gradual Rollout

1. **Phase 1**: Deploy alongside old system (both work)
2. **Phase 2**: Update CLI to use new engine
3. **Phase 3**: Mark old compatibility.py as deprecated
4. **Phase 4**: Remove old system in next major version

### Feature Flag

```python
# Environment variable to toggle engines
import os

if os.getenv("VIDEOWISE_USE_V2_ENGINE", "true").lower() == "true":
    from videowise.compatibility_v2 import *
else:
    from videowise.compatibility import *
```

## Future Enhancements

### 1. Plugin System

Allow users to provide custom YAML profiles:

```python
engine = RuleEngine(profiles_path="/path/to/custom_profiles.yaml")
```

### 2. Rule Inheritance

```yaml
social_media_base:  # Base profile
  codecs:
    optimal: ["h264"]

instagram:
  extends: social_media_base  # Inherit from base
  limits:
    max_file_size: 104857600
```

### 3. Auto-Generate FFmpeg Commands

```yaml
rules:
  - condition: "codec != 'h264'"
    level: "warning"
    message: "Convert to H.264"
    fix_command: "ffmpeg -i {input} -c:v libx264 -profile:v baseline {output}"
```

### 4. Web UI for Profile Editor

Visual editor for creating/editing system profiles without touching YAML.

## Conclusion

This refactoring achieves the Phase 2 goals:

✅ **Simplified Requirements**: Data-driven, not hardcoded  
✅ **Deleted Unnecessary Parts**: 66% code reduction  
✅ **Optimized Design**: Rule-based engine vs 31 classes  
✅ **Easier to Extend**: YAML vs Python for new systems  
✅ **Community-Friendly**: Lower barrier for contributions  

The new architecture positions VideoWise as a sustainable open-source project where adding new systems is trivial and doesn't require Python expertise.
