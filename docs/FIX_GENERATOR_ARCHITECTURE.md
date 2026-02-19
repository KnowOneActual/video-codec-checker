# FFmpeg Fix Generator Architecture

**Status:** 📋 Planning (Phase 4.2)  
**Target Release:** v0.6.0  
**Priority:** HIGH - Top community request

---

## Overview

The FFmpeg Fix Generator will transform VideoWise from a diagnostic tool into a complete solution by automatically generating (and optionally executing) ffmpeg commands to fix compatibility issues.

### Key Principles

1. **Safety First** - Generate commands, don't execute by default
2. **Multiple Options** - Offer quality/speed/size tradeoffs
3. **Educational** - Show users what each fix does
4. **Extensible** - Easy to add new fix strategies
5. **Production-Ready** - Backup, validation, error handling

---

## User Experience

### Example 1: Instagram H.264 Profile Issue

**Current Output (v0.5.0):**
```
❌ INCOMPATIBLE: Instagram
- H.264 High Profile will be re-encoded (quality loss)
- Suggestion: Re-encode to H.264 Baseline Profile
```

**With Fix Generator (v0.6.0):**
```
❌ INCOMPATIBLE: Instagram
- H.264 High Profile will be re-encoded (quality loss)
- Suggestion: Re-encode to H.264 Baseline Profile

🔧 FIX COMMAND:
ffmpeg -i video.mp4 -c:v libx264 -profile:v baseline -level 3.1 \
  -pix_fmt yuv420p -c:a aac -b:a 128k video_instagram.mp4

💡 Run: videowise fix video.mp4 --system instagram --apply
```

### Example 2: CasparCG Container Issue

```bash
$ videowise fix video.mp4 --system casparcg

Found 2 possible fix(es):

============================================================
Fix 1: Rewrap from MP4 to MOV without re-encoding
Quality: lossless | Speed: instant
Estimated time: 0.5s
File size change: 1.0x

🔧 Command:
  ffmpeg -i video.mp4 -c copy video_mov.mov

📁 Output: video_mov.mov
Issues fixed: MP4 container not recommended - use MOV for CasparCG

============================================================
Fix 2: Transcode to ProRes 422 (10-bit, high quality for editing)
Quality: high | Speed: medium
Estimated time: 45.2s
File size change: 5.0x

🔧 Command:
  ffmpeg -i video.mp4 -c:v prores_ks -profile:v 2 -pix_fmt yuv422p10le \
    -c:a pcm_s16le video_prores422.mov

📁 Output: video_prores422.mov
Issues fixed: MP4 container not recommended - use MOV for CasparCG

💡 Tip: Add --apply flag to execute the fix
💡 Tip: Add --dry-run flag for safe testing
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         VideoWise CLI                            │
│  (check, fix, batch commands with --fix, --apply flags)         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FixGenerator                                 │
│  • Analyzes CompatibilityIssue objects                          │
│  • Generates FixCommand objects                                  │
│  • Selects optimal strategy per system                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│FixStrategy   │ │ FFmpegBuilder│ │ FixValidator │
│   Base       │ │              │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤
│• analyze()   │ │• build_cmd() │ │• validate()  │
│• generate()  │ │• add_input() │ │• verify()    │
│• estimate()  │ │• add_video() │ │• compare()   │
└──────────────┘ │• add_audio() │ └──────────────┘
                 │• add_output()│
                 └──────────────┘
        │
        ├─── ContainerRewrapStrategy
        ├─── CodecTranscodeStrategy
        ├─── ProfileChangeStrategy
        ├─── ResolutionScaleStrategy
        ├─── BitrateAdjustStrategy
        └─── FrameRateConvertStrategy
```

---

## Core Data Structures

### `FixCommand` (Data Class)

Represents a single fix operation with all metadata.

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class FixQuality(Enum):
    """Quality tier for the fix."""
    LOSSLESS = "lossless"      # No quality loss (copy, rewrap)
    HIGH = "high"              # Minimal loss (ProRes, DNxHD)
    MEDIUM = "medium"          # Balanced (H.264 high bitrate)
    LOW = "low"                # Compressed (H.264 low bitrate)

class FixSpeed(Enum):
    """Encoding speed tier."""
    INSTANT = "instant"        # Container rewrap, <1s
    FAST = "fast"              # Quick encode, ~1x realtime
    MEDIUM = "medium"          # Balanced, ~0.5x realtime
    SLOW = "slow"              # High quality, ~0.2x realtime

class FixStrategy(Enum):
    """Type of fix being applied."""
    CONTAINER_REWRAP = "container_rewrap"
    CODEC_TRANSCODE = "codec_transcode"
    PROFILE_CHANGE = "profile_change"
    RESOLUTION_SCALE = "resolution_scale"
    BITRATE_ADJUST = "bitrate_adjust"
    FRAMERATE_CONVERT = "framerate_convert"
    AUDIO_FIX = "audio_fix"
    COMBINED = "combined"

@dataclass
class FixCommand:
    """
    Represents a single ffmpeg fix command.
    
    Attributes:
        command: Full ffmpeg command string
        strategy: Type of fix being applied
        description: Human-readable explanation
        quality: Quality tier of output
        speed: Encoding speed tier
        output_file: Suggested output filename
        estimated_seconds: Estimated encoding time
        file_size_change: Expected size change (multiplier)
        issues_fixed: List of issue reasons this fixes
        hardware_accel: Whether GPU acceleration is used
        two_pass: Whether two-pass encoding is used
        safe: Whether this is a safe operation (no re-encoding)
        metadata: Additional command metadata
    """
    command: str
    strategy: FixStrategy
    description: str
    quality: FixQuality
    speed: FixSpeed
    output_file: str
    estimated_seconds: float
    file_size_change: float
    issues_fixed: List[str]
    hardware_accel: bool = False
    two_pass: bool = False
    safe: bool = True
    metadata: Dict[str, Any] = None
```

### Example `FixCommand` Object

```python
FixCommand(
    command="ffmpeg -i video.mp4 -c copy video.mov",
    strategy=FixStrategy.CONTAINER_REWRAP,
    description="Rewrap from MP4 to MOV without re-encoding",
    quality=FixQuality.LOSSLESS,
    speed=FixSpeed.INSTANT,
    output_file="video_mov.mov",
    estimated_seconds=0.5,
    file_size_change=1.0,
    issues_fixed=["MP4 container not recommended - use MOV"],
    safe=True,
    metadata={"target_container": "mov"}
)
```

---

## Core Classes

### `FFmpegBuilder` (Command Builder)

Fluent API for building ffmpeg commands safely.

```python
class FFmpegBuilder:
    """
    Build ffmpeg commands with fluent API.
    
    Example:
        builder = FFmpegBuilder()
        cmd = (builder
            .input("video.mp4")
            .video_codec("libx264")
            .video_profile("baseline")
            .video_bitrate("5M")
            .audio_codec("aac")
            .output("video_fixed.mp4")
            .build())
    """
    
    def input(self, path: str) -> 'FFmpegBuilder':
        """Set input file."""
        
    def output(self, path: str) -> 'FFmpegBuilder':
        """Set output file."""
        
    def video_codec(self, codec: str) -> 'FFmpegBuilder':
        """Set video codec (libx264, prores, hap)."""
        
    def video_profile(self, profile: str) -> 'FFmpegBuilder':
        """Set video profile (baseline, main, high)."""
        
    def audio_codec(self, codec: str) -> 'FFmpegBuilder':
        """Set audio codec (aac, pcm_s16le, copy)."""
        
    def copy_streams(self) -> 'FFmpegBuilder':
        """Copy all streams without re-encoding."""
        
    def build(self) -> str:
        """Build final ffmpeg command."""
```

**Full implementation:** See [FFmpegBuilder Reference](#ffmpegbuilder-reference)

---

### `FixStrategy` (Base Class)

Abstract base class for all fix strategies.

```python
from abc import ABC, abstractmethod
from typing import List
from videowise.compatibility import CompatibilityIssue

class FixStrategy(ABC):
    """
    Base class for fix strategies.
    
    Each strategy knows how to fix a specific type of issue.
    """
    
    def __init__(self, issue: CompatibilityIssue, input_file: str, 
                 metadata: dict):
        self.issue = issue
        self.input_file = input_file
        self.metadata = metadata
    
    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this strategy can handle the issue."""
        pass
    
    @abstractmethod
    def generate(self) -> List[FixCommand]:
        """
        Generate one or more fix commands.
        
        Returns:
            List of FixCommand objects, sorted by preference
        """
        pass
```

---

## Concrete Strategies

### 1. `ContainerRewrapStrategy`

**Purpose:** Change container format without re-encoding (fastest, lossless)

**Use Cases:**
- MP4 → MOV for CasparCG
- MOV → MP4 for web
- Any → MKV for archival

**Example:**
```python
class ContainerRewrapStrategy(FixStrategy):
    def can_handle(self) -> bool:
        reasons = self.issue.reason.lower()
        return any(keyword in reasons for keyword in [
            "container", "mov recommended", "mp4 preferred"
        ])
    
    def generate(self) -> List[FixCommand]:
        target = self._detect_target_container()
        
        builder = FFmpegBuilder()
        command = (builder
            .input(self.input_file)
            .copy_streams()  # No re-encoding!
            .output(f"video_{target}.{target}")
            .build())
        
        return [FixCommand(
            command=command,
            strategy=FixStrategy.CONTAINER_REWRAP,
            description=f"Rewrap to {target.upper()}",
            quality=FixQuality.LOSSLESS,
            speed=FixSpeed.INSTANT,
            # ... other fields
        )]
```

---

### 2. `ProfileChangeStrategy`

**Purpose:** Change H.264 profile (High → Baseline, etc.)

**Use Cases:**
- Instagram: High → Baseline
- Legacy devices: High → Main
- Streaming: Main → High for compression

**Example:**
```python
class ProfileChangeStrategy(FixStrategy):
    def can_handle(self) -> bool:
        codec = self.metadata.get("codec", "").lower()
        reasons = self.issue.reason.lower()
        return codec == "h264" and "profile" in reasons
    
    def generate(self) -> List[FixCommand]:
        target_profile = self._detect_target_profile()
        
        # Option 1: CRF mode (best quality)
        crf_fix = self._generate_crf_fix(target_profile)
        
        # Option 2: Bitrate mode (predictable size)
        cbr_fix = self._generate_bitrate_fix(target_profile)
        
        return [crf_fix, cbr_fix]
```

**Generated Command (CRF):**
```bash
ffmpeg -i video.mp4 -c:v libx264 -profile:v baseline -level 3.1 \
  -crf 23 -preset medium -pix_fmt yuv420p -c:a copy video_h264_baseline.mp4
```

---

### 3. `CodecTranscodeStrategy`

**Purpose:** Full codec transcode (H.264 → ProRes, HAP, DNxHD)

**Use Cases:**
- H.264 → ProRes for editing (DaVinci, Premiere)
- H.264 → HAP for Resolume VJ performance
- ProRes → H.264 for delivery

**Example:**
```python
class CodecTranscodeStrategy(FixStrategy):
    def can_handle(self) -> bool:
        reasons = self.issue.reason.lower()
        return any(codec in reasons for codec in [
            "prores", "hap", "dnxhd", "dnxhr"
        ])
    
    def generate(self) -> List[FixCommand]:
        target = self._detect_target_codec()
        
        if target == "prores":
            return self._generate_prores_fixes()
        elif target == "hap":
            return self._generate_hap_fixes()
        elif target == "dnxhd":
            return self._generate_dnxhd_fixes()
```

**Generated Command (ProRes 422):**
```bash
ffmpeg -i video.mp4 -c:v prores_ks -profile:v 2 -pix_fmt yuv422p10le \
  -c:a pcm_s16le video_prores422.mov
```

**Generated Command (HAP):**
```bash
ffmpeg -i video.mp4 -c:v hap -c:a pcm_s16le video_hap.mov
```

---

### 4. Additional Strategies (TODO)

#### `ResolutionScaleStrategy`
- 4K → 1080p for Instagram
- Downscale for performance

#### `BitrateAdjustStrategy`
- Lower bitrate for streaming
- Increase bitrate for quality

#### `FrameRateConvertStrategy`
- VFR → CFR for CasparCG
- 60fps → 30fps for social media

---

## `FixGenerator` (Main Class)

Orchestrates all strategies and generates fixes.

```python
class FixGenerator:
    """
    Main fix generator that orchestrates all strategies.
    
    Usage:
        generator = FixGenerator()
        fixes = generator.generate_fixes(
            input_file="video.mp4",
            system="instagram"
        )
        for fix in fixes:
            print(fix.description)
            print(fix.command)
    """
    
    def __init__(self):
        self.analyzer = VideoAnalyzer()
        self.strategies = [
            ContainerRewrapStrategy,
            ProfileChangeStrategy,
            CodecTranscodeStrategy,
            ResolutionScaleStrategy,
            BitrateAdjustStrategy,
            FrameRateConvertStrategy,
        ]
    
    def generate_fixes(self, input_file: str, system: str,
                      prefer_quality: bool = True) -> List[FixCommand]:
        """
        Generate fixes for all issues with a system.
        
        Args:
            input_file: Path to video file
            system: Target system (e.g. 'instagram', 'casparcg')
            prefer_quality: Prefer quality over speed/size
        
        Returns:
            List of FixCommand objects, sorted by preference
        """
        # 1. Analyze file
        metadata = self.analyzer.get_metadata(input_file)
        
        # 2. Check compatibility
        result = check_compatibility(input_file, system)
        
        # 3. Generate fixes for each issue
        all_fixes = []
        for issue in result.issues:
            fixes = self._generate_fixes_for_issue(
                issue, input_file, metadata
            )
            all_fixes.extend(fixes)
        
        # 4. Sort and deduplicate
        all_fixes = self._sort_fixes(all_fixes, prefer_quality)
        all_fixes = self._deduplicate_fixes(all_fixes)
        
        return all_fixes
```

---

## CLI Integration

### New `fix` Command

```bash
# Show fixes without executing
videowise fix video.mp4 --system instagram

# Apply the best fix
videowise fix video.mp4 --system instagram --apply

# Apply with backup (default)
videowise fix video.mp4 --system instagram --apply --backup

# Dry run (show what would happen)
videowise fix video.mp4 --system instagram --apply --dry-run

# Prefer quality over speed
videowise fix video.mp4 --system resolume --quality --apply
```

### Enhanced `check` Command

```bash
# Show fixes alongside compatibility check
videowise check video.mp4 --system instagram --fix

# Check all systems and show fixes
videowise check video.mp4 --all --fix
```

### Batch Fix Generation

```bash
# Generate shell script to fix all videos
videowise batch videos/ --system casparcg --generate-fixes > fix_all.sh

# Review and execute
chmod +x fix_all.sh
./fix_all.sh
```

---

## Implementation Plan

### Phase 4.2a: MVP (2-3 weeks) ⭐ PRIORITY

**Goal:** Generate commands, don't execute

- [ ] `FixCommand` data class with enums
- [ ] `FFmpegBuilder` fluent API
- [ ] `FixStrategy` base class
- [ ] `ContainerRewrapStrategy` implementation
- [ ] `ProfileChangeStrategy` implementation
- [ ] Basic `FixGenerator` class
- [ ] `--fix` flag on `check` command
- [ ] 20+ unit tests
- [ ] User documentation

**Deliverable:** `videowise check video.mp4 --system instagram --fix`

---

### Phase 4.2b: Interactive Mode (2 weeks)

**Goal:** Execute fixes safely

- [ ] `videowise fix` command
- [ ] `--apply` flag with confirmation
- [ ] `--dry-run` mode (show without executing)
- [ ] `--backup` automatic backups
- [ ] Progress bars for long encodes
- [ ] Output validation (re-analyze fixed file)
- [ ] Error handling and rollback
- [ ] 15+ integration tests

**Deliverable:** `videowise fix video.mp4 --system instagram --apply`

---

### Phase 4.2c: Advanced Strategies (3 weeks)

**Goal:** Complete fix coverage

- [ ] `CodecTranscodeStrategy` (ProRes, HAP, DNxHD)
- [ ] `ResolutionScaleStrategy` (4K → 1080p)
- [ ] `BitrateAdjustStrategy` (streaming optimization)
- [ ] `FrameRateConvertStrategy` (VFR → CFR)
- [ ] Hardware acceleration detection (NVENC, QuickSync, VideoToolbox)
- [ ] Two-pass encoding support
- [ ] Multiple fix options per issue
- [ ] 30+ tests for all strategies

**Deliverable:** `videowise fix video.mp4 --system resolume --quality`

---

### Phase 4.2d: Batch & Automation (2 weeks)

**Goal:** Production workflows

- [ ] Batch fix generation (`--generate-fixes`)
- [ ] Shell script export
- [ ] Preset library ("instagram-story", "casparcg-prores")
- [ ] Watch folder integration
- [ ] CI/CD hooks
- [ ] Parallel processing for batch
- [ ] Summary reports

**Deliverable:** `videowise batch videos/ --system casparcg --generate-fixes > fix.sh`

---

## Testing Strategy

### Unit Tests

```python
# tests/test_fix_generator.py

def test_container_rewrap_strategy():
    """Test container rewrapping without re-encoding."""
    issue = CompatibilityIssue(
        severity="warning",
        reason="MP4 container not recommended - use MOV",
        suggestion="Rewrap to MOV"
    )
    metadata = {
        "container": "mp4",
        "codec": "h264",
        "file_size": 10485760
    }
    
    strategy = ContainerRewrapStrategy(issue, "test.mp4", metadata)
    assert strategy.can_handle()
    
    fixes = strategy.generate()
    assert len(fixes) == 1
    assert fixes[0].quality == FixQuality.LOSSLESS
    assert fixes[0].speed == FixSpeed.INSTANT
    assert "-c copy" in fixes[0].command
    assert ".mov" in fixes[0].output_file

def test_profile_change_strategy():
    """Test H.264 profile change."""
    issue = CompatibilityIssue(
        severity="warning",
        reason="H.264 High Profile - Instagram prefers Baseline",
        suggestion="Re-encode to Baseline"
    )
    metadata = {
        "codec": "h264",
        "profile": "high",
        "file_size": 10485760,
        "resolution": "1920x1080"
    }
    
    strategy = ProfileChangeStrategy(issue, "test.mp4", metadata)
    assert strategy.can_handle()
    
    fixes = strategy.generate()
    assert len(fixes) >= 1
    assert "baseline" in fixes[0].command
    assert fixes[0].safe == False  # Re-encoding
```

### Integration Tests

```python
def test_fix_generator_instagram():
    """Test complete fix generation for Instagram."""
    generator = FixGenerator()
    fixes = generator.generate_fixes(
        "tests/fixtures/h264_high_profile.mp4",
        "instagram"
    )
    
    assert len(fixes) >= 1
    assert "baseline" in fixes[0].command
    assert fixes[0].quality in [FixQuality.HIGH, FixQuality.MEDIUM]

def test_fix_command_execution():
    """Test actual fix execution (requires ffmpeg)."""
    # Create test video
    test_file = create_test_video(codec="h264", profile="high")
    
    # Generate fix
    generator = FixGenerator()
    fixes = generator.generate_fixes(test_file, "instagram")
    
    # Execute fix
    fix = fixes[0]
    result = subprocess.run(fix.command, shell=True, capture_output=True)
    assert result.returncode == 0
    
    # Verify output
    assert os.path.exists(fix.output_file)
    analyzer = VideoAnalyzer()
    metadata = analyzer.get_metadata(fix.output_file)
    assert metadata["profile"].lower() == "baseline"
```

---

## Safety & Error Handling

### Safeguards

1. **Command Generation First**
   - Always show command before executing
   - Require explicit `--apply` flag

2. **Automatic Backups**
   - Create `.bak` files by default
   - `--no-backup` to disable (dangerous!)

3. **Dry Run Mode**
   - `--dry-run` shows what would happen
   - No files modified

4. **Output Validation**
   - Re-analyze fixed file
   - Verify issues are resolved
   - Compare file sizes

5. **Error Recovery**
   - Rollback on failure
   - Restore from backup
   - Clear error messages

### Error Messages

```bash
❌ Error: FFmpeg not found
💡 Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)

❌ Error: Fix failed - output file corrupt
✅ Original file restored from backup: video.mp4.bak

⚠️  Warning: HAP codec requires special ffmpeg build
💡 Install: brew install ffmpeg --with-options hap
```

---

## Open Questions

### 1. Execution vs Generation

**Question:** Should we execute ffmpeg directly or just generate commands?

**Decision:** Start with generation only (Phase 4.2a), add execution in Phase 4.2b

**Rationale:**
- Safer for MVP
- Easier to test
- Users can review commands
- Add execution when stable

---

### 2. FFmpeg Not Installed

**Question:** How to handle ffmpeg not being installed?

**Decision:** Check for ffmpeg, provide install instructions

**Implementation:**
```python
def check_ffmpeg_installed() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
```

---

### 3. Output Validation

**Question:** Should we validate output files after fixing?

**Decision:** Yes, re-run analyzer to verify

**Implementation:**
```python
def validate_fix(output_file: str, system: str) -> bool:
    result = check_compatibility(output_file, system)
    return result.is_compatible()
```

---

### 4. Special Codec Builds

**Question:** How to handle HAP, DXV, and other special codecs?

**Decision:** Detect available codecs, show warning if missing

**Implementation:**
```python
def check_codec_available(codec: str) -> bool:
    result = subprocess.run(
        ["ffmpeg", "-codecs"],
        capture_output=True,
        text=True
    )
    return codec in result.stdout
```

---

### 5. Hardware Acceleration

**Question:** Should we support auto-detection of hardware acceleration?

**Decision:** Yes for Phase 4.2c (not MVP)

**Detection:**
- **macOS:** VideoToolbox (always available on modern Macs)
- **Windows:** NVENC (NVIDIA), QuickSync (Intel)
- **Linux:** NVENC, VAAPI

---

## FFmpegBuilder Reference

### Full Method List

```python
class FFmpegBuilder:
    # Input/Output
    def input(path: str) -> FFmpegBuilder
    def output(path: str) -> FFmpegBuilder
    
    # Video Encoding
    def video_codec(codec: str) -> FFmpegBuilder
    def video_profile(profile: str) -> FFmpegBuilder
    def video_level(level: str) -> FFmpegBuilder
    def video_bitrate(bitrate: str) -> FFmpegBuilder
    def video_preset(preset: str) -> FFmpegBuilder
    def video_crf(crf: int) -> FFmpegBuilder
    
    # Audio Encoding
    def audio_codec(codec: str) -> FFmpegBuilder
    def audio_bitrate(bitrate: str) -> FFmpegBuilder
    
    # Video Processing
    def pixel_format(fmt: str) -> FFmpegBuilder
    def scale(width: int, height: int) -> FFmpegBuilder
    def framerate(fps: str) -> FFmpegBuilder
    def keyframe_interval(seconds: int) -> FFmpegBuilder
    
    # Performance
    def hardware_accel(accel: str) -> FFmpegBuilder
    def two_pass_encoding(enable: bool) -> FFmpegBuilder
    
    # Shortcuts
    def copy_streams() -> FFmpegBuilder
    def extra_flag(flag: str) -> FFmpegBuilder
    
    # Build
    def build() -> str
    def build_two_pass() -> tuple[str, str]
```

### Usage Examples

#### Simple Rewrap
```python
cmd = (FFmpegBuilder()
    .input("video.mp4")
    .copy_streams()
    .output("video.mov")
    .build())
# Result: ffmpeg -i video.mp4 -c copy video.mov
```

#### Instagram Baseline
```python
cmd = (FFmpegBuilder()
    .input("video.mp4")
    .video_codec("libx264")
    .video_profile("baseline")
    .video_level("3.1")
    .video_crf(23)
    .pixel_format("yuv420p")
    .audio_codec("aac")
    .audio_bitrate("128k")
    .output("video_instagram.mp4")
    .build())
```

#### ProRes for Editing
```python
cmd = (FFmpegBuilder()
    .input("video.mp4")
    .video_codec("prores_ks")
    .extra_flag("-profile:v").extra_flag("2")  # ProRes 422
    .pixel_format("yuv422p10le")
    .audio_codec("pcm_s16le")
    .output("video_prores.mov")
    .build())
```

---

## Resources

### FFmpeg Documentation
- [Official FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [H.264 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/H.264)
- [ProRes Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/ProRes)
- [Hardware Acceleration](https://trac.ffmpeg.org/wiki/HWAccelIntro)

### Codec References
- [HAP Codec](https://github.com/Vidvox/hap)
- [DNxHD/DNxHR Specs](https://www.avid.com/dnxhr)
- [ProRes White Paper](https://www.apple.com/final-cut-pro/docs/Apple_ProRes_White_Paper.pdf)

---

## Success Metrics

**Phase 4.2a (MVP) Goals:**
- [ ] 3+ fix strategies implemented
- [ ] 20+ unit tests passing
- [ ] `--fix` flag working on `check` command
- [ ] User documentation complete
- [ ] Zero critical bugs

**Phase 4.2 Complete Goals:**
- [ ] All 6 fix strategies implemented
- [ ] 80+ tests passing (unit + integration)
- [ ] `videowise fix` command fully functional
- [ ] Hardware acceleration support
- [ ] Batch fix generation working
- [ ] 90%+ user satisfaction (based on feedback)

---

## Next Steps

1. **Review this architecture** with team/community
2. **Start Phase 4.2a implementation** (MVP)
3. **Create GitHub issues** for each component
4. **Set up project board** for tracking
5. **Write initial tests** (TDD approach)
6. **Implement `FixCommand` and `FFmpegBuilder`** first
7. **Add strategies one by one**
8. **Iterate based on feedback**

---

*Last updated: February 19, 2026*  
*Target release: v0.6.0 (Phase 4.2)*  
*Status: 📋 Planning*
