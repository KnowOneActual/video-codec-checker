# Streaming Platform Compatibility Checkers

This document describes the new streaming platform compatibility checkers added to VideoWise.

## Overview

Six new compatibility checkers have been added for popular streaming platforms:

1. **Twitch** - Leading gaming and IRL streaming platform
2. **YouTube Live** - Google's live streaming service
3. **Kick** - Newer Twitch competitor
4. **Restream** - Multi-platform streaming service
5. **Zoom** - Video conferencing platform
6. **Discord** - Communication platform with Go Live and video sharing

## Usage

```python
from videowise.streaming_checkers import (
    TwitchChecker,
    YouTubeLiveChecker,
    KickChecker,
    RestreamChecker,
    ZoomChecker,
    DiscordChecker
)

# Example: Check video for Twitch compatibility
video_info = {
    "codec": "h264",
    "profile": "High",
    "container": "mp4",
    "resolution": (1920, 1080),
    "bitrate": 6_000_000,  # 6 Mbps
    "frame_rate": 60
}

checker = TwitchChecker()
issues = checker.check(video_info)

for issue in issues:
    print(f"{issue.level.value}: {issue.message}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

## Platform Requirements

### Twitch

**Codec Requirements:**
- **Required:** H.264 (AVC) only
- **Profile:** Main or High profile recommended
- **Audio:** AAC required

**Bitrate:**
- **Maximum:** 9 Mbps (hard limit)
- **Recommended 1080p60:** 6 Mbps
- **Recommended 720p60:** 4.5 Mbps
- **Minimum:** 3 Mbps for good quality

**Resolution:**
- **Maximum:** 1920x1080 (1080p)
- Partners/Affiliates get transcoding above 6 Mbps

**Special Requirements:**
- **Keyframe interval:** 2 seconds (critical!)
- **Frame rate:** Up to 60fps for Partners/Affiliates
- **Container:** MP4, MOV, FLV, or TS

**Example FFmpeg command:**
```bash
ffmpeg -i input.mp4 -c:v libx264 -profile:v high -level 4.1 \
  -b:v 6M -maxrate 6M -bufsize 12M -g 120 -keyint_min 120 \
  -c:a aac -b:a 160k -ar 44100 -f flv rtmp://live.twitch.tv/app/your_stream_key
```

### YouTube Live

**Codec Requirements:**
- **Recommended:** H.264
- **Also Supported:** HEVC (H.265) for 4K

**Bitrate:**
- **4K60:** Up to 85 Mbps
- **4K30:** Up to 51 Mbps
- **1080p60:** 9 Mbps recommended, up to 12 Mbps max
- **1080p30:** 6 Mbps recommended
- **720p:** 5-10 Mbps

**Resolution:**
- Supports up to 4K (3840x2160)
- Auto-transcoding for all quality levels

**Container:** MP4, MOV, FLV, or TS

### Kick

**Codec Requirements:**
- **Required:** H.264 only

**Bitrate:**
- **Maximum:** 10 Mbps
- **Recommended:** 8 Mbps for 1080p60
- **Minimum:** 3 Mbps

**Resolution:**
- **Recommended:** 1920x1080 (1080p)

**Note:** Similar to Twitch but with slightly higher bitrate allowance.

### Restream

**Codec Requirements:**
- **Recommended:** H.264 (ensures compatibility across all platforms)

**Bitrate:**
- **Conservative Recommended:** 4.5-6 Mbps
- Settings based on most restrictive platform (usually Twitch)

**Use Case:**
- Multi-platform streaming (Twitch + YouTube + Facebook, etc.)
- Lower bitrates ensure reliability across all destinations

### Zoom

**Codec Requirements:**
- **Supported:** H.264, HEVC
- Hardware acceleration available

**Bitrate:**
- **Recommended:** 2-3 Mbps for 1080p
- **Maximum practical:** 4 Mbps

**Resolution:**
- **Maximum:** 1920x1080 for most plans
- Higher resolutions will be downscaled

**Frame Rate:**
- **Recommended:** 30fps
- Zoom caps at 30fps for video sharing

**Use Case:**
- Video conferencing
- Screen sharing with video playback
- Optimized for lower bandwidth

### Discord

**Codec Requirements:**
- **Supported:** H.264, VP8, VP9

**File Upload Limits:**
- **Free accounts:** 8 MB
- **Nitro accounts:** 100 MB

**Go Live Streaming:**
- **Maximum bitrate:** 8 Mbps for Source quality
- **Recommended:** 6-8 Mbps

**Resolution:**
- **Free accounts:** Up to 720p
- **Nitro accounts:** Up to 1080p60

**Use Cases:**
- Go Live screen sharing
- Video file uploads
- Voice channel video

## Integration with VideoWise

### Option 1: Import from streaming_checkers module

```python
from videowise.streaming_checkers import TwitchChecker

checker = TwitchChecker(quality="1080p")
issues = checker.check(video_info)
```

### Option 2: Add to compatibility.py registry (future)

To integrate these checkers into the main `compatibility.py` module:

1. Import the streaming checkers:
```python
from .streaming_checkers import (
    TwitchChecker,
    YouTubeLiveChecker,
    KickChecker,
    RestreamChecker,
    ZoomChecker,
    DiscordChecker,
)
```

2. Add to `get_available_systems()`:
```python
return sorted([
    # ... existing systems ...
    "twitch",
    "youtubelive",
    "kick",
    "restream",
    "zoom",
    "discord",
])
```

3. Add to `check_compatibility()` checkers dict:
```python
checkers = {
    # ... existing checkers ...
    "twitch": TwitchChecker,
    "youtubelive": YouTubeLiveChecker,
    "kick": KickChecker,
    "restream": RestreamChecker,
    "zoom": ZoomChecker,
    "discord": DiscordChecker,
}
```

## Testing

```python
# Test Twitch with valid settings
twitch_video = {
    "codec": "h264",
    "profile": "High",
    "bitrate": 6_000_000,
    "resolution": (1920, 1080),
    "frame_rate": 60,
    "container": "mp4"
}

checker = TwitchChecker()
issues = checker.check(twitch_video)
assert all(i.level == CompatibilityLevel.COMPATIBLE or 
           i.level == CompatibilityLevel.WARNING for i in issues)

# Test Discord with file size limit
discord_video = {
    "codec": "h264",
    "file_size": 10 * 1024 * 1024,  # 10 MB (exceeds free limit)
    "bitrate": 5_000_000
}

checker = DiscordChecker(user_type="free")
issues = checker.check(discord_video)
assert any(i.level == CompatibilityLevel.INCOMPATIBLE for i in issues)
```

## Key Differences Between Platforms

| Platform | Codec | Max Bitrate | Max Resolution | Keyframe | Notes |
|----------|-------|-------------|----------------|----------|-------|
| Twitch | H.264 only | 9 Mbps | 1080p | 2s required | Strict requirements |
| YouTube Live | H.264/HEVC | 85 Mbps (4K) | 4K | Flexible | Most flexible |
| Kick | H.264 only | 10 Mbps | 1080p | Flexible | Like Twitch |
| Restream | H.264 rec | 6 Mbps | 1080p | 2s for Twitch | Multi-platform |
| Zoom | H.264/HEVC | 4 Mbps | 1080p | Flexible | Lower bitrates |
| Discord | H.264/VP8/VP9 | 8 Mbps | 720p/1080p | Flexible | File size limits |

## Common Issues and Solutions

### Issue: "Twitch requires H.264 codec"
**Solution:** Re-encode to H.264:
```bash
ffmpeg -i input.mp4 -c:v libx264 -profile:v high -c:a aac output.mp4
```

### Issue: "Bitrate exceeds platform maximum"
**Solution:** Lower bitrate with `-b:v` flag:
```bash
ffmpeg -i input.mp4 -c:v copy -c:a copy -b:v 6M output.mp4
```

### Issue: "Keyframe interval not set for Twitch"
**Solution:** Set keyframe interval to 2 seconds:
```bash
# For 60fps: -g 120 (60 * 2)
# For 30fps: -g 60 (30 * 2)
ffmpeg -i input.mp4 -c:v libx264 -g 120 -keyint_min 120 output.mp4
```

### Issue: "File size exceeds Discord limit"
**Solution:** Compress video:
```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -b:v 3M output.mp4
```

## References

- [Twitch Broadcasting Guidelines](https://help.twitch.tv/s/article/broadcasting-guidelines)
- [YouTube Live Encoder Settings](https://support.google.com/youtube/answer/2853702)
- [Kick Creator Handbook](https://help.kick.com/)
- [Restream Help Center](https://support.restream.io/)
- [Zoom Video Requirements](https://support.zoom.us/hc/en-us/articles/360000976852)
- [Discord Media Upload Guide](https://support.discord.com/hc/en-us/articles/360017479212)

## Contributing

To add support for additional streaming platforms:

1. Create a new checker class inheriting from `CompatibilityChecker`
2. Implement the `check()` method with platform-specific requirements
3. Add comprehensive docstrings and comments
4. Include platform constants (bitrates, resolutions, etc.)
5. Add tests and documentation
6. Update this README
