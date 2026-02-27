# System Profiles

This directory contains YAML-based system profiles that define compatibility rules for video codecs, containers, and formats across different platforms.

## Quick Start: Adding a New System

### 1. Edit `videowise/system_profiles.yaml`

Add your system under the appropriate category:

```yaml
category_name:  # live_production, editing, social_media, browsers, streaming
  your_system:
    name: "Display Name"
    category: "category_name"
    codecs:
      optimal: ["best_codec"]
      recommended: ["good_codec"]
      supported: ["basic_codec"]
    containers:
      preferred: ["mov", "mp4"]
    rules:
      - codec: "specific_codec"
        level: "compatible"
        message: "This codec works great"
        reason: "Hardware acceleration available"
```

### 2. Test Your Profile

```python
from videowise.rule_engine import RuleEngine

engine = RuleEngine()
issues = engine.check_compatibility(
    {"codec": "h264", "container": "mp4"},
    "your_system"
)
print(issues)
```

### 3. Submit Pull Request

That's it! No Python code needed.

## Profile Structure

### Basic Profile

```yaml
system_key:  # Used in code: check_compatibility(video_info, "system_key")
  name: "Human-Readable Name"  # Displayed in messages
  category: "live_production"  # Group classification
  
  codecs:
    optimal: ["codec1", "codec2"]      # Best performance/quality
    recommended: ["codec3"]            # Good compatibility
    supported: ["codec4", "codec5"]    # Works but not ideal
    alpha_support: ["prores4444"]      # Optional: supports transparency
    hardware_accelerated: ["h264"]     # Optional: GPU decode available
  
  containers:
    required: ["mxf"]                   # Must use this container
    # OR
    preferred: ["mov", "mp4"]           # Recommended containers
  
  limits:
    max_file_size: 104857600            # Bytes (100MB)
    max_duration: 60                    # Seconds
    max_resolution: [1920, 1080]        # [width, height]
    optimal_bitrate_range: [8000000, 15000000]  # [min, max] in bps
```

### With Conditional Rules

```yaml
system_key:
  name: "System Name"
  codecs:
    optimal: ["prores"]
  
  rules:
    # Simple codec match
    - codec: "h264"
      level: "warning"
      message: "H.264 may require transcoding"
      suggestion: "Use ProRes for best performance"
    
    # Multiple codecs
    - codec: ["h264", "hevc"]
      level: "compatible"
      message: "Hardware decode available"
    
    # Conditional expression
    - condition: "bitrate > 100000000"  # 100 Mbps
      level: "warning"
      message: "High bitrate may cause stuttering"
      suggestion: "Keep bitrate under 100 Mbps"
    
    # Complex condition
    - condition: "codec == 'h264' and resolution[0] >= 3840"
      level: "warning"
      message: "4K H.264 requires powerful hardware"
      reason: "High resolution with CPU-based codec"
```

### With Variants

```yaml
system_key:
  name: "System Name"
  codecs:
    optimal: ["prores"]
  
  variants:
    free:
      rules:
        - codec: "h264"
          level: "warning"
          message: "Free version lacks GPU decode"
    
    pro:
      rules:
        - codec: "h264"
          level: "compatible"
          message: "Pro version has GPU acceleration"
```

Usage:
```python
checker = SystemChecker(version="pro")
issues = checker.check(video_info)
```

## Available Condition Variables

Use these in `condition` expressions:

| Variable | Type | Example |
|----------|------|----------|
| `codec` | string | `"h264"`, `"prores"` |
| `container` | string | `"mp4"`, `"mov"` |
| `profile` | string | `"baseline"`, `"high"` |
| `bitrate` | int | `50000000` (50 Mbps) |
| `resolution` | tuple | `(1920, 1080)` |
| `frame_rate` | float/string | `29.97` or `"variable"` |
| `file_size` | int | `104857600` (100MB) |

### Condition Examples

```yaml
rules:
  # Equality
  - condition: "codec == 'h264'"
  
  # Numeric comparison
  - condition: "bitrate > 100000000"
  - condition: "resolution[0] >= 3840"  # Width >= 3840
  
  # List membership
  - condition: "codec in ['h264', 'hevc']"
  
  # Logical AND
  - condition: "codec == 'h264' and profile != 'baseline'"
  
  # Logical OR
  - condition: "resolution[0] > 1920 or bitrate > 50000000"
  
  # String contains (use 'in')
  - condition: "'4444' in codec"  # Matches prores4444
  
  # Nested conditions
  - condition: "(codec == 'h264' and resolution[0] >= 3840) or bitrate > 200000000"
```

## Compatibility Levels

- **`compatible`**: Works perfectly, recommended
- **`warning`**: Works but not ideal, may have issues
- **`incompatible`**: Will not work, must be converted
- **`unknown`**: Insufficient information to determine

## Real-World Examples

### Live Production System (CasparCG)

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
        reason: "Optimal for real-time playout"
      
      - condition: "codec == 'hap' and container != 'mov'"
        level: "warning"
        message: "HAP codec requires MOV container"
        suggestion: "Remux to MOV"
      
      - condition: "resolution[0] >= 3840 and bitrate > 200000000"
        level: "warning"
        message: "4K at high bitrate may stress system"
        suggestion: "Use HAP codec for GPU-accelerated 4K"
```

### Social Media Platform (Instagram)

```yaml
social_media:
  instagram:
    name: "Instagram"
    category: "social_media"
    codecs:
      optimal: ["h264"]
      profile_preferred: "baseline"
    limits:
      max_file_size: 104857600  # 100MB
      max_duration: 60
      max_resolution: [1080, 1920]
    rules:
      - condition: "codec != 'h264'"
        level: "warning"
        message: "Instagram will re-encode to H.264 (quality loss)"
        suggestion: "Pre-encode to H.264"
      
      - condition: "profile != 'baseline'"
        level: "warning"
        message: "Instagram prefers H.264 Baseline profile"
        suggestion: "Convert to Baseline"
```

### Editing Platform (DaVinci Resolve)

```yaml
editing:
  davinci:
    name: "DaVinci Resolve"
    category: "editing"
    codecs:
      optimal: ["dnxhd", "dnxhr", "prores", "braw"]
      supported: ["h264", "hevc"]
    variants:
      free:
        rules:
          - codec: ["h264", "hevc"]
            level: "warning"
            message: "Free version lacks GPU decode"
            suggestion: "Transcode to DNxHR or upgrade to Studio"
      
      studio:
        rules:
          - codec: ["h264", "hevc"]
            level: "compatible"
            message: "GPU hardware decode available"
    rules:
      - codec: "braw"
        level: "compatible"
        message: "Blackmagic RAW natively supported"
        reason: "Excellent color grading flexibility"
      
      - condition: "codec in ['h264', 'hevc'] and resolution[0] >= 1920"
        level: "warning"
        message: "Long-GOP compression may slow frame-accurate work"
        suggestion: "Generate optimized media (DNxHR/ProRes)"
```

## Testing Your Profile

### Unit Test Template

```python
import pytest
from videowise.rule_engine import RuleEngine
from videowise.compatibility import CompatibilityLevel

def test_your_system_optimal_codec():
    engine = RuleEngine()
    issues = engine.check_compatibility(
        {"codec": "your_optimal_codec", "container": "mov"},
        "your_system"
    )
    
    assert len(issues) > 0
    compatible = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
    assert len(compatible) > 0

def test_your_system_incompatible_codec():
    engine = RuleEngine()
    issues = engine.check_compatibility(
        {"codec": "unsupported_codec", "container": "mp4"},
        "your_system"
    )
    
    warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
    assert len(warnings) > 0

def test_your_system_conditional_rule():
    engine = RuleEngine()
    issues = engine.check_compatibility(
        {
            "codec": "h264",
            "bitrate": 200_000_000,  # Trigger high bitrate rule
            "container": "mp4",
        },
        "your_system"
    )
    
    assert any("bitrate" in i.message.lower() for i in issues)
```

## Common Codec Names

### Video Codecs
- `h264` - H.264/AVC
- `hevc`, `h265` - H.265/HEVC
- `av1` - AV1
- `vp8`, `vp9` - VP8/VP9
- `prores`, `prores422`, `prores4444` - Apple ProRes
- `prores_proxy`, `prores_lt`, `prores_hq` - ProRes variants
- `dnxhd`, `dnxhr` - Avid DNx
- `hap`, `hap_alpha`, `hap_q` - HAP (GPU accelerated)
- `braw` - Blackmagic RAW
- `r3d` - RED RAW
- `xavc` - Sony XAVC
- `mjpeg` - Motion JPEG
- `mpeg2video` - MPEG-2

### Containers
- `mp4` - MP4/MPEG-4
- `mov` - QuickTime MOV
- `mxf` - Material Exchange Format
- `mkv`, `matroska` - Matroska
- `avi` - AVI
- `webm` - WebM

## Contributing Guidelines

1. **Test before submitting**: Use the test template above
2. **Be specific**: Include `reason` and `suggestion` in rules
3. **Use real-world knowledge**: Base rules on actual platform behavior
4. **Keep it simple**: Start with basic codec/container checks
5. **Document sources**: Add comments linking to official docs

### Example with Documentation

```yaml
# Source: https://example.com/video-specs
your_system:
  name: "Your System"
  codecs:
    optimal: ["prores"]  # Recommended by official docs
    supported: ["h264"]   # Works but not optimal
  
  # From official specs: max 1080p, H.264 only for web uploads
  limits:
    max_resolution: [1920, 1080]
  
  rules:
    # Confirmed behavior: H.264 High Profile re-encoded to Baseline
    - condition: "codec == 'h264' and profile == 'high'"
      level: "warning"
      message: "High Profile will be re-encoded to Baseline"
      reason: "Platform automatically converts profiles"
```

## Need Help?

- **Examples**: Look at existing profiles in `videowise/system_profiles.yaml`
- **Discussion**: [Open a discussion](https://github.com/KnowOneActual/video-codec-checker/discussions)
- **Issues**: [Report bugs](https://github.com/KnowOneActual/video-codec-checker/issues)
- **Documentation**: See `docs/REFACTORING_GUIDE.md`

## Advanced: Custom Profiles

You can provide your own profile file:

```python
from pathlib import Path
from videowise.rule_engine import RuleEngine

engine = RuleEngine(profiles_path=Path("my_custom_profiles.yaml"))
issues = engine.check_compatibility(video_info, "my_system")
```

This allows you to:
- Add proprietary/internal systems
- Override default profiles
- Experiment with new rules without modifying the main file
