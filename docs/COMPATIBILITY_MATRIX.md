# VideoWise Compatibility Matrix

Detailed breakdown of compatibility features for each supported system.

## Table of Contents

- [Live Production Systems](#live-production-systems)
  - [CasparCG Server](#casparcg-server)
  - [vMix](#vmix)
  - [OBS Studio](#obs-studio)
  - [QLab](#qlab)
  - [ProPresenter](#propresenter)
- [Browser Compatibility](#browser-compatibility)
  - [Safari](#safari)
  - [Chrome](#chrome)
  - [Firefox](#firefox)
- [Social Media Platforms](#social-media-platforms)
  - [Instagram](#instagram)
  - [Twitter/X](#twitterx)
  - [YouTube](#youtube)

---

## Live Production Systems

### CasparCG Server

**Supported Codecs:**
- ✅ H.264 (in MP4 or MOV container)
- ✅ ProRes (all variants: 422, 422 HQ, 422 LT, 422 Proxy, 4444)
- ✅ DNxHD / DNxHR
- ✅ MPEG-2
- ✅ MJPEG
- ❌ VP9, AV1, HEVC (not supported)

**Container Formats:**
- Preferred: MP4, MOV, MXF
- Avoid: MKV, WebM

**Compatibility Checks:**
- ✅ Codec validation against supported list
- ✅ Container format recommendations
- ✅ **Variable Frame Rate (VFR) detection** - VFR causes timing issues in live production
- ✅ Warns about unsupported codecs
- ✅ Suggests alternative codecs for compatibility

**What VideoWise Checks:**
```
❌ VP9 codec not supported by CasparCG
   Reason: CasparCG 2.3 requires H.264, ProRes, DNxHD, or MPEG-2
   Suggestion: Convert to H.264 for broad compatibility

❌ Variable frame rate detected
   Reason: VFR videos cause timing issues in live production
   Suggestion: Convert to constant frame rate (CFR) before use
```

**Optimal Settings:**
- ProRes 422 or 422 HQ for highest quality
- H.264 High Profile for smaller file sizes
- Constant frame rate (CFR) required
- MP4 or MOV container

---

### vMix

**Supported Codecs:**
- ✅ H.264
- ✅ HEVC (H.265)
- ✅ ProRes (with hardware acceleration)
- ✅ DNxHD / DNxHR
- ✅ MPEG-2
- ⚠️ AV1 (limited support)

**Performance Considerations:**
- ⚠️ Bitrate > 100 Mbps: May cause performance issues
- ⚠️ Bitrate > 200 Mbps: Likely to cause dropped frames
- ⚠️ 4K resolution: Requires high-end hardware

**Compatibility Checks:**
- ✅ Bitrate performance warnings (100 Mbps and 200 Mbps thresholds)
- ✅ 4K resolution hardware requirement warnings
- ✅ ProRes/DNxHD optimization detection
- ✅ Suggests ProRes or DNxHD for best performance

**What VideoWise Checks:**
```
⚠️  High bitrate may cause performance issues
   Reason: Bitrate is 180 Mbps (vMix may struggle above 100 Mbps)
   Suggestion: Consider lower bitrate or ProRes for better performance

⚠️  4K resolution requires high-end hardware
   Reason: 3840x2160 resolution detected
   Suggestion: Ensure your system meets vMix 4K requirements
```

**Optimal Settings:**
- ProRes 422 LT or Proxy for best performance/quality balance
- H.264 with bitrate under 100 Mbps
- 1080p for standard systems, 4K requires dedicated hardware

---

### OBS Studio

**Supported Codecs:**
- ✅ H.264 (hardware accelerated)
- ✅ HEVC (H.265, with GPU support)
- ✅ AV1 (with modern GPUs)
- ✅ VP8, VP9
- ✅ ProRes, DNxHD
- ✅ Most common codecs

**Container Formats:**
- Default: MKV (most compatible)
- Also: MP4, MOV, FLV

**Compatibility Checks:**
- ✅ H.264/HEVC hardware acceleration detection
- ✅ MKV container as default format
- ✅ Multi-codec support validation
- ✅ Very permissive - warns only on rare issues

**What VideoWise Checks:**
```
✅ Video is compatible with OBS Studio
   Note: OBS has excellent codec support and hardware acceleration
```

**Optimal Settings:**
- H.264 with hardware encoding (NVENC, QuickSync, or AMD VCE)
- MKV container for recording (auto-repairs on crash)
- MP4 for final output

---

### QLab

**Supported Codecs:**
- ✅ ProRes (all variants) - **Optimal for performance**
- ✅ H.264
- ✅ HEVC
- ✅ MPEG-4
- ⚠️ Other codecs may have scrubbing performance issues

**Performance Optimization:**
- ✅ **ProRes 422 Proxy** - Best for scrubbing and cueing
- ✅ **ProRes 422 LT** - Good balance of quality and performance
- ⚠️ H.264 - May have scrubbing lag, especially at high resolutions
- ✅ ProRes 4444 - Supports alpha channel transparency

**Compatibility Checks:**
- ✅ Detects ProRes Proxy/LT for optimal performance
- ✅ Warns about H.264 scrubbing performance
- ✅ Recommends ProRes for smooth playback
- ✅ Detects ProRes 4444 alpha channel support

**What VideoWise Checks:**
```
✅ ProRes 422 LT detected - excellent for QLab
   Note: ProRes optimized for smooth scrubbing and cue performance

⚠️  H.264 may have scrubbing performance issues
   Reason: H.264 requires more CPU for decoding during scrubbing
   Suggestion: Convert to ProRes 422 Proxy for better QLab performance
```

**Optimal Settings:**
- ProRes 422 Proxy for cues that need scrubbing
- ProRes 422 LT for high-quality playback
- ProRes 4444 for videos with transparency
- MOV container

---

### ProPresenter

**Supported Codecs:**
- ✅ **HAP** - GPU-accelerated, best performance
- ✅ **HAP Alpha** - With transparency support
- ✅ **HAP Q** - Higher quality HAP
- ✅ ProRes (all variants)
- ✅ ProRes 4444 (alpha channel support)
- ✅ H.264
- ✅ HEVC

**Performance Tiers:**
1. **Best: HAP codec** - GPU-accelerated, real-time playback
2. **Good: ProRes** - High quality, smooth playback
3. **Acceptable: H.264/HEVC** - Works but may struggle with multiple layers

**Compatibility Checks:**
- ✅ HAP codec detection (best performance)
- ✅ ProRes 4444 transparency support
- ✅ H.264/HEVC compatibility validation
- ✅ Performance recommendations based on codec

**What VideoWise Checks:**
```
✅ HAP codec detected - optimal for ProPresenter
   Note: HAP is GPU-accelerated for best real-time performance

✅ ProRes 4444 with alpha channel support
   Note: Transparency works great in ProPresenter

⚠️  H.264 is compatible but HAP would be faster
   Reason: H.264 is CPU-decoded, HAP uses GPU for better performance
   Suggestion: Consider HAP codec for multiple simultaneous videos
```

**Optimal Settings:**
- HAP or HAP Q for best performance
- HAP Alpha for transparency
- ProRes 4444 for high-quality alpha channel
- MOV container

---

## Browser Compatibility

### Safari

**Supported Codecs:**
- ✅ H.264 (all profiles: Baseline, Main, High)
- ✅ HEVC (H.265) on supported devices
- ❌ VP9 (not supported)
- ❌ AV1 (not supported)
- ❌ Theora (not supported)

**Container Formats:**
- ✅ MP4 (preferred)
- ✅ MOV (QuickTime)
- ❌ WebM (not supported)
- ❌ OGG (not supported)

**Profile Recommendations:**
- ✅ Main Profile - Best compatibility
- ✅ High Profile - Works but may have issues on older devices
- ⚠️ Baseline Profile - Most compatible but least efficient

**Compatibility Checks:**
- ✅ H.264 and HEVC only
- ✅ Rejects VP9, AV1, WebM
- ✅ MP4 container recommendation
- ✅ Profile-based warnings

**What VideoWise Checks:**
```
❌ VP9 codec not supported in Safari
   Reason: Safari only supports H.264 and HEVC
   Suggestion: Convert to H.264 for Safari compatibility

⚠️  WebM container not recommended for Safari
   Reason: Safari prefers MP4 container
   Suggestion: Use MP4 container for best Safari compatibility
```

**Optimal Settings:**
- H.264 Main Profile
- MP4 container
- AAC audio

---

### Chrome

**Supported Codecs:**
- ✅ H.264
- ✅ VP8
- ✅ VP9
- ✅ AV1 (on supported devices)
- ✅ Theora

**Container Formats:**
- ✅ MP4
- ✅ WebM
- ✅ OGG

**Compatibility Checks:**
- ✅ Broad codec support validation
- ✅ Multi-format container support
- ✅ Rarely flags issues (very permissive)

**What VideoWise Checks:**
```
✅ Video is compatible with Chrome
   Note: Chrome has excellent codec support including VP9 and AV1
```

**Optimal Settings:**
- VP9 for best compression (modern web)
- H.264 for maximum compatibility (older devices)
- WebM or MP4 container

---

### Firefox

**Supported Codecs:**
- ✅ H.264 (all profiles)
- ✅ VP8
- ✅ VP9
- ✅ AV1
- ⚠️ HEVC (limited support - Windows 10+ only with extensions)
- ❌ ProRes (not supported)

**Container Formats:**
- ✅ MP4 (for H.264)
- ✅ WebM (preferred for VP8/VP9)
- ✅ OGG

**Codec-Container Pairings:**
- **Best:** VP9 in WebM - Native support, excellent compression
- **Best:** H.264 in MP4 - Universal compatibility
- **Good:** AV1 in WebM - Modern, efficient codec
- **Limited:** HEVC in MP4 - Requires Windows 10+ with HEVC Video Extensions

**Compatibility Checks:**
- ✅ H.264, VP8, VP9, and AV1 full support
- ✅ Optimal container pairing detection (VP9/WebM, H.264/MP4)
- ✅ HEVC limited support warning (Windows 10+ only)
- ✅ ProRes rejection with conversion suggestions

**What VideoWise Checks:**
```
✅ VP9 in WebM is natively supported by Firefox
   Reason: WebM is Firefox's preferred format for VP8/VP9

✅ H.264 in MP4 is fully supported by Firefox
   Reason: Universal browser compatibility

⚠️  HEVC has limited support in Firefox
   Reason: HEVC requires Windows 10+ with HEVC Video Extensions
   Suggestion: Convert to H.264 or VP9 for broader compatibility

❌ Firefox does not support ProRes codec
   Reason: Firefox supports H.264, VP8, VP9, and AV1
   Suggestion: Convert to H.264 (MP4) or VP9 (WebM) for Firefox
```

**Optimal Settings:**
- **For maximum compatibility:** H.264 Main Profile in MP4
- **For modern web:** VP9 in WebM
- **For future-proof:** AV1 in WebM (with H.264 fallback)
- AAC audio for MP4, Opus audio for WebM

**Browser Version Notes:**
- VP9 supported since Firefox 28 (2014)
- AV1 supported since Firefox 67 (2019)
- HEVC support varies by platform and requires codec pack on Windows

---

## Social Media Platforms

### Instagram

**Supported Codecs:**
- ✅ H.264 (required)
- ❌ All other codecs trigger re-encoding

**Profile Requirements:**
- ✅ **Baseline Profile** - No re-encoding (best quality)
- ⚠️ **Main Profile** - Will be re-encoded (quality loss)
- ⚠️ **High Profile** - Will be re-encoded (quality loss)

**Resolution:**
- Maximum: 1080p (1920x1080)
- ⚠️ Higher resolutions will be downscaled

**Container:**
- Required: MP4

**Compatibility Checks:**
- ✅ H.264 codec requirement
- ✅ Profile-specific re-encoding warnings
- ✅ Resolution downscaling detection (over 1080p)
- ✅ Quality loss warnings for non-Baseline profiles
- ✅ Container format validation

**What VideoWise Checks:**
```
⚠️  Instagram may re-encode this video
   Reason: H.264 High Profile detected (Instagram prefers Baseline)
   Suggestion: Convert to H.264 Baseline to avoid quality loss

⚠️  Resolution will be downscaled
   Reason: 4K (3840x2160) exceeds Instagram's 1080p limit
   Suggestion: Export at 1080p to maintain quality control
```

**Optimal Settings:**
- H.264 Baseline Profile
- 1080p maximum resolution
- MP4 container
- AAC audio
- 30 fps (24, 25, 30, or 60 fps supported)

---

### Twitter/X

**Supported Codecs:**
- ✅ H.264 (preferred)
- ✅ H.264 High Profile recommended
- ⚠️ Other codecs may be re-encoded

**File Size Limits:**
- **Standard accounts:** 512 MB
- **Premium accounts:** Up to 8 GB (2 hours max)

**Resolution:**
- Minimum: 32x32 pixels
- Maximum: 1920x1200 or 1200x1920 pixels
- Aspect ratio: 1:2.39 to 2.39:1

**Container:**
- Preferred: MP4
- Also: MOV

**Compatibility Checks:**
- ✅ H.264 High Profile recommendation
- ✅ File size limit validation (512 MB / 8 GB based on account)
- ✅ Container format validation
- ✅ Account tier awareness

**What VideoWise Checks:**
```
✅ Video is optimized for Twitter
   Note: H.264 High Profile and MP4 container are ideal

❌ File size exceeds Twitter limit
   Reason: 850 MB file, but Twitter limit is 512 MB for standard accounts
   Suggestion: Compress video or upgrade to Twitter Premium
```

**Optimal Settings:**
- H.264 High Profile
- MP4 or MOV container
- Under 512 MB for standard accounts
- AAC audio
- 30 fps recommended

---

### YouTube

**Supported Codecs:**
- ✅ **H.264** (recommended for uploads)
- ✅ HEVC (H.265)
- ✅ VP9
- ✅ AV1
- ✅ ProRes (accepted but not recommended)
- ⚠️ All uploads are re-encoded by YouTube

**Profile Recommendations:**
- ✅ **High Profile with CABAC** - Optimal upload quality
- ⚠️ Main Profile - Works but High Profile preferred
- ⚠️ Baseline Profile - Works but wastes bitrate

**Container Formats:**
- ✅ **MP4** (preferred - fastest processing)
- ✅ MOV (accepted)
- ✅ AVI (accepted)
- ⚠️ Other formats accepted but may process slower

**File Size & Duration Limits:**
- Maximum file size: 256 GB
- Maximum duration: 12 hours
- Verified accounts: 15 minutes default, up to 12 hours with verification

**Upload Strategy:**
- YouTube re-encodes ALL uploads to multiple formats (H.264, VP9, AV1)
- Upload highest quality source for best final quality
- H.264 High Profile gives you best control before re-encoding
- ProRes accepted but creates huge uploads with no quality benefit

**Compatibility Checks:**
- ✅ H.264 High Profile detection and recommendation
- ✅ Profile-based warnings (Baseline, Main suggest High)
- ✅ MP4 container preference detection
- ✅ File size validation (256 GB limit)
- ✅ Container format compatibility

**What VideoWise Checks:**
```
✅ H.264 High Profile is optimal for YouTube
   Reason: Best quality for YouTube's re-encoding process

✅ MP4 is YouTube's preferred container format
   Reason: Fastest processing and best compatibility

⚠️  H.264 Baseline Profile detected
   Reason: YouTube recommends High Profile for best quality
   Suggestion: Use High Profile with CABAC for optimal results

⚠️  YouTube recommends H.264, not ProRes for uploads
   Reason: YouTube re-encodes all uploads to multiple formats
   Suggestion: Upload as H.264 for best quality control and processing speed

⚠️  MOV is accepted but MP4 is preferred
   Suggestion: Use MP4 for faster upload processing

❌ File size 300GB exceeds YouTube's 256GB limit
   Reason: YouTube has a maximum file size of 256GB
   Suggestion: Compress video or split into multiple parts
```

**Optimal Settings:**
- **Codec:** H.264 High Profile with CABAC
- **Container:** MP4
- **Bitrate:** High (YouTube will re-encode anyway, so start with quality)
  - 1080p: 8-12 Mbps recommended
  - 4K: 35-45 Mbps recommended
- **Audio:** AAC at 320 kbps or higher
- **Frame Rate:** Match source (23.976, 24, 25, 29.97, 30, 50, 60 fps)

**Resolution Recommendations:**
- 2160p (4K): 3840x2160
- 1440p: 2560x1440
- 1080p: 1920x1080
- 720p: 1280x720

**Why H.264 for Uploads?**
1. **Predictable encoding:** You control the quality before YouTube's re-encode
2. **Fast processing:** MP4+H.264 processes faster than other formats
3. **Quality control:** High Profile gives best compression for upload
4. **Universal support:** Works on all devices during processing

**ProRes Warning:**
While YouTube accepts ProRes, uploading it provides no quality benefit:
- ProRes 422 HQ @ 1080p = ~220 Mbps = 99 GB per hour
- H.264 High @ 1080p = ~12 Mbps = 5.4 GB per hour
- **Result after YouTube re-encodes both: Identical quality**
- Save bandwidth and upload time - use H.264 High Profile

---

## Summary Table

| System | Best Codec(s) | Container | Special Notes |
|--------|---------------|-----------|---------------|
| **CasparCG** | H.264, ProRes | MP4, MOV | Requires CFR (no VFR) |
| **vMix** | ProRes, H.264 | MOV, MP4 | Watch bitrate (<100 Mbps) |
| **OBS** | H.264, HEVC | MKV, MP4 | Hardware acceleration |
| **QLab** | ProRes Proxy/LT | MOV | ProRes for smooth scrubbing |
| **ProPresenter** | HAP, ProRes | MOV | HAP = GPU accelerated |
| **Safari** | H.264, HEVC | MP4 | No VP9/AV1 support |
| **Chrome** | VP9, H.264, AV1 | WebM, MP4 | Very permissive |
| **Firefox** | H.264, VP9, AV1 | MP4, WebM | VP9/WebM native support |
| **Instagram** | H.264 Baseline | MP4 | Max 1080p, avoid re-encode |
| **Twitter** | H.264 High | MP4, MOV | 512 MB / 8 GB limit |
| **YouTube** | H.264 High | MP4 | Upload high quality source |

---

## Codec Profiles Explained

### H.264 Profiles

**Baseline Profile:**
- Most compatible
- Lowest complexity features
- Best for: Instagram, older devices, maximum compatibility
- File size: Largest

**Main Profile:**
- Good compatibility
- Moderate complexity
- Best for: General web use, Safari
- File size: Medium

**High Profile:**
- Best compression efficiency
- Highest complexity features
- Best for: YouTube, Twitter, modern devices, archival
- File size: Smallest

### ProRes Variants

**ProRes 422 Proxy:**
- Lowest bitrate ProRes
- Best for: QLab scrubbing, editing proxies
- File size: ~45 Mbps @ 1080p

**ProRes 422 LT:**
- Light variant
- Best for: QLab playback, general editing
- File size: ~100 Mbps @ 1080p

**ProRes 422:**
- Standard ProRes
- Best for: Professional editing, archival
- File size: ~145 Mbps @ 1080p

**ProRes 422 HQ:**
- High quality
- Best for: High-end production, color grading
- File size: ~220 Mbps @ 1080p

**ProRes 4444:**
- Highest quality with alpha channel support
- Best for: QLab/ProPresenter transparency, VFX
- File size: ~330 Mbps @ 1080p

### HAP Codec

**HAP:**
- GPU-decoded for real-time playback
- Best for: ProPresenter, real-time video playback
- No alpha channel

**HAP Alpha:**
- GPU-decoded with transparency
- Best for: ProPresenter with alpha channel

**HAP Q:**
- Higher quality HAP
- Best for: ProPresenter high-quality playback

---

## Variable vs Constant Frame Rate

### Constant Frame Rate (CFR)
- Fixed frame rate throughout video
- **Required for live production** (CasparCG, vMix, etc.)
- Predictable timing
- Best for: All professional video work

### Variable Frame Rate (VFR)
- Frame rate changes during playback
- Common in: Screen recordings, game capture
- **Causes timing issues in live production**
- Should convert to CFR before use

**VideoWise Detection:**
```
❌ Variable frame rate detected
   Reason: VFR causes timing issues in live production systems
   Suggestion: Convert to constant frame rate using:
   ffmpeg -i input.mp4 -r 30 -c:v libx264 output.mp4
```

---

For real-world usage examples, see [EXAMPLES.md](EXAMPLES.md).
