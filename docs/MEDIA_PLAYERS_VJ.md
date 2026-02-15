# Media Players & VJ Software

Detailed compatibility guide for media players and VJ (Video Jockey) software systems supported by VideoWise.

## Table of Contents

- [VLC Media Player](#vlc-media-player)
- [Resolume Arena/Avenue](#resolume-arenaavenue)
- [Mitti](#mitti)
- [Millumin](#millumin)

---

## VLC Media Player

**Platform:** Windows, macOS, Linux  
**Type:** Universal media player  
**Best For:** Testing video compatibility, playback on any platform

### Supported Codecs

- ✅ **Virtually all codecs** via FFmpeg libraries
- ✅ H.264, HEVC (H.265), VP8, VP9, AV1
- ✅ ProRes, DNxHD, DNxHR
- ✅ MPEG-2, MPEG-4, DivX, XviD
- ✅ Theora, WMV, and hundreds more
- ❌ Extremely rare or proprietary codecs only

### Container Formats

- ✅ **All major formats:** MP4, MOV, MKV, AVI, WebM, OGG, FLV, TS, M2TS, and more

### Hardware Acceleration

- ✅ **H.264** - NVENC (NVIDIA), QuickSync (Intel), AMD VCE, VideoToolbox (Apple)
- ✅ **HEVC** - GPU acceleration on modern hardware
- ✅ **VP9** - GPU decode on supported GPUs
- ✅ **AV1** - Hardware decode on latest GPUs (RTX 30/40 series, Intel Arc)

**Enabling Hardware Acceleration:**
1. Tools → Preferences → Input/Codecs
2. Hardware-accelerated decoding: Automatic or choose specific method
3. Save and restart VLC

### Performance Considerations

- ⚠️ **Bitrate > 300 Mbps** - May cause stuttering on slow storage (HDD)
- ⚠️ **8K resolution** - Requires powerful CPU/GPU
- ⚠️ **Multiple 4K streams** - Needs fast NVMe SSD

### What VideoWise Checks

```
✅ VP9 is supported by VLC media player
   Reason: VLC uses FFmpeg libraries for universal codec support

✅ HEVC may benefit from hardware acceleration
   Reason: Enable hardware decoding in VLC preferences for better performance

⚠️  Very high bitrate (350Mbps) may cause stuttering
   Reason: Extreme bitrates can exceed disk I/O capabilities
   Suggestion: Ensure fast storage (NVMe SSD) for smooth playback

⚠️  8K video requires powerful hardware
   Reason: 8K playback needs modern CPU/GPU and fast storage
   Suggestion: Enable hardware decoding and use VLC 3.0+
```

### Optimal Settings

- **Any codec works** - VLC plays virtually everything
- **Enable hardware decoding** for H.264, HEVC, VP9, AV1
- **Fast storage** (NVMe SSD) for high-bitrate files (>100 Mbps)
- **VLC 3.0+** recommended for best performance

### Platform-Specific Notes

- **Windows:** Full hardware acceleration support (NVENC, QuickSync, AMD VCE)
- **macOS:** VideoToolbox acceleration for H.264/HEVC
- **Linux:** VDPAU/VAAPI support for hardware decoding

### Why VLC for Testing

VLC is the "gold standard" for testing video compatibility:
- If VLC can't play it, the file is likely corrupted
- If VLC plays it but target system doesn't → codec compatibility issue
- Universal codec support helps identify the actual problem

---

## Resolume Arena/Avenue

**Platform:** Windows, macOS  
**Type:** VJ software for concerts, festivals, clubs  
**Best For:** Real-time video mixing, multiple layers, live performance

### Supported Codecs

- ✅ **DXV, DXV2, DXV3** - Optimal (Resolume proprietary GPU codec)
- ✅ **HAP, HAP Alpha, HAP Q, HAP Q Alpha** - Optimal (GPU-accelerated)
- ✅ H.264 (CPU-based, not recommended for multiple layers)
- ✅ HEVC (CPU-intensive, convert to DXV/HAP)
- ✅ ProRes (CPU-based, Mac only, not recommended)
- ✅ MJPEG (CPU-based)

### Performance Tiers

1. **Best: DXV codec family** - Resolume's proprietary GPU codec
2. **Also Best: HAP codec family** - Cross-platform GPU codec
3. **Acceptable: H.264** - CPU decode limits layer count
4. **Poor: ProRes on Windows** - CPU decode, very slow
5. **Avoid: HEVC** - CPU-intensive, poor VJ performance

### Container Formats

- ✅ **MOV** - Required for DXV and HAP
- ✅ MP4 - For H.264/HEVC
- ⚠️ DXV and HAP **MUST** be in MOV container

### What VideoWise Checks

```
✅ DXV is the optimal codec for Resolume
   Reason: GPU-accelerated, proprietary to Resolume for best performance

✅ HAP Alpha provides GPU-accelerated playback with alpha
   Reason: HAP Alpha perfect for overlays and VJ graphics

⚠️  H.264 will use CPU decoding, not GPU
   Reason: H.264 performs poorly with multiple layers in Resolume
   Suggestion: Convert to DXV or HAP for GPU acceleration

⚠️  ProRes on Windows is CPU-based and slow
   Reason: ProRes not optimized for Windows, limits layers
   Suggestion: Convert to DXV or HAP for GPU acceleration

⚠️  4K video limits the number of simultaneous layers
   Reason: 4K requires 4x bandwidth of 1080p
   Suggestion: Use 1080p for more layers, or DXV/HAP for best 4K performance

⚠️  Very high bitrate (250Mbps) may limit layer count
   Reason: High bitrate stresses disk I/O even with GPU codecs
   Suggestion: Use DXV or HAP with moderate bitrate for more layers
```

### Optimal Settings

- **Best Codec:** DXV (Resolume only) or HAP (universal VJ)
- **Container:** MOV required for DXV/HAP
- **Resolution:** 1080p for multiple layers, 4K for single layer
- **Bitrate:** Moderate (50-150 Mbps) for best layer count

### DXV vs HAP

**DXV:**
- Resolume-only codec
- Slightly better compression than HAP
- Best performance in Resolume

**HAP:**
- Works in other VJ software (VDPAU, Mitti, TouchDesigner)
- GPU-accelerated
- Equal performance to DXV in Resolume
- Better for cross-platform workflows

**Both provide:**
- GPU texture decompression
- Real-time playback of multiple layers
- Low CPU usage

### Platform-Specific Notes

**Windows:**
- DXV and HAP optimal
- Avoid ProRes (slow CPU decode)
- H.264 acceptable for single layer

**macOS:**
- DXV and HAP optimal
- ProRes acceptable but CPU-based (limits layers)
- H.264 acceptable for single layer

### Converting to DXV/HAP

Resolume includes **Alley** - a conversion tool for DXV:
```bash
# Using Alley (included with Resolume)
Alley -i input.mp4 -o output.mov -c dxv
```

For HAP, use ffmpeg with HAP codec:
```bash
ffmpeg -i input.mp4 -c:v hap output.mov
```

### Real-World Performance

**1080p HAP @ 60fps:**
- Single layer: ~80-100 Mbps
- Can play 8-12 layers simultaneously on modern GPU

**4K HAP @ 30fps:**
- Single layer: ~200-250 Mbps
- Can play 2-4 layers on high-end GPU

**1080p H.264:**
- Single layer: Works fine
- 2-3 layers: CPU bottleneck, dropped frames
- 4+ layers: Not recommended

---

## Mitti

**Platform:** macOS only  
**Type:** Professional playback for theatre, corporate events  
**Best For:** Rock-solid reliability, multi-output, show control

### Supported Codecs

- ✅ **ProRes (all variants)** - Optimal on Apple Silicon
- ✅ **HAP, HAP Alpha, HAP Q** - Optimal for multi-output
- ✅ H.264 (transcoding recommended)
- ✅ HEVC (transcoding recommended)
- ✅ All QuickTime codecs

### Transcoding Philosophy

Mitti has **built-in transcoding** to ProRes or HAP:
- Import any format
- Mitti converts to optimal codec
- Transcoding happens once, playback is flawless
- Save transcoded library for future shows

### Performance Tiers

1. **ProRes on Apple Silicon** - Hardware accelerated (M1/M2/M3)
2. **HAP for multi-output** - GPU path for HDMI/DisplayPort
3. **ProRes for SDI output** - Best quality for broadcast
4. **H.264 (after transcode)** - Good for single output

### Container Formats

- ✅ **MOV** (preferred)
- ✅ MP4 (works, MOV preferred)
- ✅ Most formats (Mitti transcodes automatically)

### Apple Silicon Optimization

- **M1/M2/M3 Macs** have hardware ProRes encoding/decoding
- ProRes playback is extremely efficient on Apple Silicon
- Multiple 4K ProRes streams = no problem on M1+
- ProRes decode is essentially "free" on Apple Silicon

### What VideoWise Checks

```
✅ ProRes is optimal for Mitti
   Reason: Hardware accelerated on Apple Silicon Macs (M1/M2/M3)

✅ HAP is optimal for Mitti
   Reason: GPU-accelerated, especially for 4K and multi-output

⚠️  H.264 should be transcoded for Mitti
   Reason: Mitti recommends ProRes or HAP for reliable playback
   Suggestion: Use Mitti's built-in transcoding to ProRes (Apple Silicon) or HAP (multi-output)

⚠️  4K video: use HAP for multi-output, ProRes for single output
   Reason: 4K ProRes great on Apple Silicon; 4K HAP better for HDMI/DisplayPort multi-output
   Suggestion: HAP for GPU path (external displays), ProRes for SDI

⚠️  High bitrate (300Mbps) may stress playback
   Reason: Very high bitrate can cause dropped frames
   Suggestion: Use ProRes 422 or HAP with moderate bitrate
```

### Optimal Settings

**Apple Silicon Mac + Single output:**
- ProRes 422 or ProRes 422 LT
- MOV container
- Let Apple Silicon hardware handle decode

**Apple Silicon Mac + Multi-output:**
- HAP or HAP Q
- MOV container
- GPU path for external displays

**Intel Mac + Multi-output:**
- HAP (GPU path)
- Avoid ProRes (CPU bottleneck)

**SDI output (Blackmagic/AJA):**
- ProRes 422 HQ
- Highest quality for broadcast

**4K content:**
- HAP for HDMI/DisplayPort output
- ProRes for SDI output

### Workflow Best Practices

1. **Import any video format** into Mitti
2. **Let Mitti transcode** to ProRes or HAP
3. **Use transcoded files** for show
4. **Save transcoded library** for future use
5. Never use original files in production

### Integration Notes

**NDI Support:**
- Receive NDI streams from network
- Mix local files with remote NDI sources

**ATEM Control:**
- Control Blackmagic ATEM switchers
- Synchronize video cues with switching

**Multi-Projector:**
- Use HAP codec for GPU-accelerated output
- Edge blending support
- Warping and geometry correction

**Show Control:**
- MIDI, OSC, DMX, Art-Net
- Timecode synchronization
- QLab integration

### Real-World Use Cases

**Corporate Events:**
- ProRes 422 LT for reliability
- Multi-output to projectors/confidence monitors
- ATEM integration for live switching

**Theatre Productions:**
- ProRes 422 for quality
- QLab integration for show control
- Long-running shows (months) without issues

**Museum Installations:**
- HAP for 24/7 playback
- Multiple outputs with different content
- Auto-restart on power loss

---

## Millumin

**Platform:** macOS only (10.13+)  
**Type:** Video mapping and projection software  
**Best For:** Projection mapping, multi-projector, interactive installations

### Supported Codecs

- ✅ **All QuickTime formats**
- ✅ **All AVFoundation-supported codecs**
- ✅ **ProRes (all variants)** - Native Mac codec
- ✅ **HAP, HAP Alpha, HAP Q** - Optimal for projection mapping
- ✅ H.264, HEVC
- ✅ MPEG-4, MJPEG

### Performance Tiers

1. **HAP codec** - GPU-accelerated, best for multi-projector
2. **ProRes** - Hardware accelerated on Apple Silicon
3. **H.264** - CPU-based, works but not optimal

### Container Formats

- ✅ **MOV** (preferred - QuickTime native)
- ✅ MP4 (compatible)

### Projection Mapping Optimization

- **HAP codec** is optimal for **multi-projector setups**
- GPU acceleration crucial for real-time edge blending
- ProRes works but HAP performs better with multiple outputs
- HAP allows more projectors with less hardware

### Apple Silicon Performance

- **M1/M2/M3 Macs** have hardware ProRes decode
- ProRes excellent for single-projector high-quality output
- HAP still better for multi-projector (GPU path)
- Apple Silicon + HAP = best projection mapping performance

### What VideoWise Checks

```
✅ ProRes is supported by Millumin
   Reason: Millumin uses QuickTime and AVFoundation for codec support

✅ ProRes is excellent for Millumin
   Reason: Native Mac codec with hardware acceleration on Apple Silicon

✅ HAP is optimal for Millumin projection mapping
   Reason: GPU-accelerated, ideal for multi-projector setups

⚠️  H.264 works but ProRes/HAP recommended for projection
   Reason: H.264 is CPU-based, can limit real-time performance
   Suggestion: Use ProRes or HAP for better projection mapping performance

⚠️  4K video requires powerful Mac for smooth projection
   Reason: 4K projection mapping is GPU-intensive
   Suggestion: Use HAP codec for best 4K projection performance
```

### Optimal Settings

**Multi-projector:**
- HAP or HAP Q (GPU acceleration)
- MOV container
- 1080p per projector for best performance

**Single projector:**
- ProRes 422 or 422 LT
- MOV container
- Apple Silicon for hardware decode

**Interactive content:**
- HAP for best real-time performance
- Low latency for interaction

**High quality:**
- ProRes 422 HQ
- For museum/permanent installations

### Use Cases

**Theatre Productions:**
- ProRes 422 for single-screen playback
- Syphon integration for live effects
- Show control via MIDI/OSC

**Museum Installations:**
- HAP for multi-screen, long-running
- 24/7 reliability
- Auto-restart on power loss

**Dance/Concerts:**
- HAP for real-time triggering
- Interactive effects with audio analysis
- Multiple outputs synchronized

**Projection Mapping:**
- HAP for multi-projector edge blending
- Warping and geometry correction
- 3D projection mapping on complex surfaces

**Interactive Art:**
- HAP with Syphon for real-time processing
- TouchDesigner integration
- Kinect/sensor input

### Hardware Requirements

**Minimum:**
- Mac with Apple Silicon (M1+) or Intel i7+
- 16 GB RAM
- Dedicated GPU (for Intel Macs)

**Recommended for Multi-Projector:**
- Mac Studio (M1 Max or Ultra)
- 32 GB RAM
- Multiple Thunderbolt outputs
- Fast NVMe SSD

**4K Projection:**
- Apple Silicon (M1 Pro or better)
- 32 GB RAM
- HAP codec for GPU acceleration

### Integration Features

**Syphon:**
- Real-time video sharing between apps
- Connect to TouchDesigner, VDMX, etc.
- Low-latency video routing

**MIDI/OSC:**
- Show control from external controllers
- QLab integration
- Custom control surfaces

**DMX/Art-Net:**
- Lighting integration
- Synchronized video and lighting cues

**NDI:**
- Network video input/output
- Remote camera feeds
- Multi-location synchronization

### Best Practices

1. **Use HAP for projection mapping** - GPU path essential
2. **Test on actual hardware** - Projection mapping is GPU-intensive
3. **Calibrate projectors** before final render
4. **Use MOV container** for all content
5. **Keep backups** of calibration files
6. **Test auto-restart** for installations

---

## Comparison Table

| Feature | VLC | Resolume | Mitti | Millumin |
|---------|-----|----------|-------|----------|
| **Platform** | Win/Mac/Linux | Win/Mac | Mac only | Mac only |
| **Primary Use** | Universal playback | VJ/concerts | Theatre/corporate | Projection mapping |
| **Best Codec** | Any | DXV/HAP | ProRes/HAP | HAP/ProRes |
| **GPU Acceleration** | Optional | Required | Optional | Required |
| **Multi-Output** | No | Yes | Yes | Yes |
| **Real-Time Mixing** | No | Yes | No | Yes |
| **Show Control** | No | Limited | Extensive | Extensive |
| **Projection Mapping** | No | No | No | Yes |
| **Learning Curve** | Easy | Moderate | Easy | Moderate |
| **Price** | Free | $449-899 | $59 | $499 |

---

## Quick Reference

### When to Use Each System

**VLC:**
- Testing any video file
- Universal playback on any platform
- Quick preview before import
- Diagnosing compatibility issues

**Resolume:**
- VJ work at concerts/festivals
- Real-time video mixing
- Multiple layer compositing
- Audio-reactive visuals

**Mitti:**
- Theatre productions
- Corporate events
- Museum installations (with HAP)
- Multi-output playback
- Rock-solid reliability required

**Millumin:**
- Projection mapping
- Multi-projector setups
- Interactive installations
- Dance/performance with video
- 3D surface mapping

### Codec Decision Tree

**Need transparency (alpha channel)?**
→ HAP Alpha or ProRes 4444

**Multiple video layers/projectors?**
→ HAP or DXV (GPU codecs)

**Single output, maximum quality?**
→ ProRes 422 HQ

**Long-running installation (24/7)?**
→ HAP (GPU, reliable)

**Cross-platform compatibility?**
→ HAP (works everywhere)

**Testing/troubleshooting?**
→ VLC (plays anything)

---

For additional systems, see the main [Compatibility Matrix](COMPATIBILITY_MATRIX.md).
