# VideoWise Architecture

This document explains how VideoWise is structured and how the components work together.

## Overview

VideoWise follows a simple three-layer architecture:

```
┌──────────────────────────┐
│  CLI / User Interface    │
│  (Coming in Phase 2)     │
└─────────┬───────────────┘
          │
┌─────────┴───────────────┐
│  Compatibility Engine   │
│  (9 System Checkers)    │
└─────────┬───────────────┘
          │
┌─────────┴───────────────┐
│  Video Analyzer          │
│  (FFprobe Wrapper)       │
└─────────────────────────┘
```

## Core Components

### 1. Video Analyzer (`analyzer.py`)

**Responsibility:** Extract metadata from video files

**Key Classes:**
- `VideoAnalyzer` - Main class for file analysis

**Workflow:**
1. Validate file exists and is readable
2. Run ffprobe to extract metadata
3. Parse JSON output into structured data
4. Cache metadata for performance
5. Provide convenient accessors for common properties

**Example:**
```python
analyzer = VideoAnalyzer('video.mp4')
video_info = analyzer.get_video_info()
print(video_info['codec'])  # 'h264'
print(video_info['container'])  # 'mp4'
```

### 2. Compatibility Engine (`compatibility.py`)

**Responsibility:** Check video compatibility against specific systems

**Key Classes:**
- `CompatibilityLevel` (Enum) - COMPATIBLE, WARNING, INCOMPATIBLE, UNKNOWN
- `CompatibilityIssue` (Dataclass) - Structured issue with message, reason, suggestion
- `CompatibilityChecker` (Base Class) - Abstract base for all checkers
- System-specific checkers (9 implementations)

**Design Pattern:** Strategy Pattern

Each system implements the `check()` method:
```python
class SystemChecker(CompatibilityChecker):
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        # System-specific logic
        return issues
```

**Workflow:**
1. Receive video_info dict from analyzer
2. Apply system-specific rules
3. Return list of issues (may be empty for fully compatible)

### 3. Explanation System (`explainer.py` - Coming in Phase 2)

**Responsibility:** Format compatibility issues for human consumption

**Planned Features:**
- Colored terminal output
- Grouped issue display
- Severity-based formatting
- Suggested fixes

## Data Flow

```
Video File → VideoAnalyzer → video_info dict
                                    │
                                    v
                      CompatibilityChecker(s)
                                    │
                                    v
                         List[CompatibilityIssue]
                                    │
                                    v
                            Explainer (Phase 2)
                                    │
                                    v
                          Formatted Output
```

## Key Design Decisions

### Why FFprobe instead of direct parsing?
- FFprobe is battle-tested and handles edge cases
- Supports all major video formats
- Already required dependency for video work
- JSON output is easy to parse

### Why separate checkers instead of one big function?
- **Extensibility:** Easy to add new systems
- **Testability:** Each checker can be tested independently
- **Maintainability:** System-specific logic is isolated
- **Clarity:** Each checker focuses on one system

### Why dataclasses for issues?
- Type safety with Python 3.7+
- Clear structure for issue data
- Easy to serialize (JSON, YAML)
- IDE autocomplete support

### Why three-level severity (COMPATIBLE/WARNING/INCOMPATIBLE)?
- **COMPATIBLE:** File will work perfectly
- **WARNING:** File will work but with caveats (re-encoding, performance issues)
- **INCOMPATIBLE:** File will not work at all

This matches real-world scenarios better than binary compatible/incompatible.

## Testing Strategy

### Test Organization
1. **Unit tests** - Individual functions and methods
2. **Integration tests** - Full workflow with generated videos
3. **Fixtures** - Generate test videos with ffmpeg

### Test Video Generation
Tests generate real video files with specific codecs:
```python
@pytest.fixture
def h264_video(tmp_path):
    # Generate H.264 video using ffmpeg
    return video_path
```

This ensures tests use realistic data, not mocked objects.

## Adding New System Checkers

1. Create new checker class inheriting from `CompatibilityChecker`
2. Implement `check()` method
3. Add to `check_compatibility()` dispatcher
4. Write comprehensive tests
5. Document in COMPATIBILITY_RULES.md

**Example:**
```python
class NewSystemChecker(CompatibilityChecker):
    """Compatibility checker for NewSystem."""
    
    SUPPORTED_CODECS = {'h264', 'prores'}
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        
        if codec not in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message=f"NewSystem doesn't support {codec}",
                reason="Only H.264 and ProRes are supported",
                suggestion="Convert to H.264 or ProRes"
            ))
        else:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="Compatible with NewSystem"
            ))
        
        return issues
```

## Performance Considerations

### Current State
- Metadata extraction is cached per analyzer instance
- Single file analysis is fast (<100ms)
- Tests run in ~1 second

### Future Optimizations (Phase 4)
- Async file processing for batch operations
- Parallel checker execution
- Persistent cache for frequently-checked files
- Incremental analysis (only re-check changed attributes)

## Error Handling

### File Validation
- Check file exists before ffprobe
- Handle ffprobe errors gracefully
- Return meaningful error messages

### Checker Errors
- Missing video_info keys are handled with `.get()` defaults
- Unknown systems return UNKNOWN CompatibilityLevel
- Malformed data doesn't crash, returns WARNING

## Dependencies

### Required
- `ffmpeg-python` - Python wrapper for ffmpeg/ffprobe
- FFmpeg/ffprobe - Must be installed on system

### Development
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting

### Future (Phase 2)
- `click` or `argparse` - CLI framework
- `rich` - Beautiful terminal output
- `pyyaml` - YAML output format

## Code Organization

```
videowise/
├── __init__.py           # Package initialization
├── analyzer.py          # Video file analysis
├── compatibility.py     # Rules engine and checkers
├── cli.py               # CLI interface (Phase 2)
└── explainer.py         # Output formatting (Phase 2)

tests/
├── conftest.py          # Shared fixtures
├── test_analyzer.py    # Analyzer tests
├── test_codec_parsing.py  # Parsing tests
├── test_compatibility.py  # Core checker tests
└── test_compatibility_extended.py  # Extended tests
```

## Future Architecture Changes

### Phase 2: CLI Layer
- Add command-line interface
- Argument parsing and validation
- Output formatting

### Phase 3: Plugin System?
- Consider plugin architecture for third-party checkers
- Configuration file support
- Custom rule definitions

### Phase 4: Web API
- REST API for web interface
- Async processing for large batches
- Result caching and storage

---

*For system-specific compatibility details, see [COMPATIBILITY_RULES.md](COMPATIBILITY_RULES.md)*
