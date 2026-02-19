# Professional Editing Platform Compatibility Guide

This guide covers optimal video codec settings for professional editing software:
- **DaVinci Resolve** (Free and Studio)
- **Adobe Premiere Pro**
- **Final Cut Pro**
- **Avid Media Composer**
- **Adobe After Effects**

---

## Table of Contents

1. [DaVinci Resolve](#davinci-resolve)
2. [Adobe Premiere Pro](#adobe-premiere-pro)
3. [Final Cut Pro](#final-cut-pro)
4. [Avid Media Composer](#avid-media-composer)
5. [Adobe After Effects](#adobe-after-effects)
6. [Quick Reference Table](#quick-reference-table)
7. [Transcoding Recipes](#transcoding-recipes)

---

## DaVinci Resolve

**Optimal Codecs:** DNxHR, ProRes, H.264/H.265 (Studio only with GPU decode)

### Best Practices

#### For Editing Timeline
- **1080p Projects:** DNxHR SQ or ProRes 422
- **4K Projects:** DNxHR HQ or ProRes 422 HQ
- **8K Projects:** DNxHR HQX or ProRes 422 HQ

#### For Proxy Workflows
- **All Resolutions:** ProRes Proxy or DNxHR LB (Low Bandwidth)
- Proxies reduce file size by ~90% while maintaining editability

#### Resolve Free vs. Studio
| Feature | Free | Studio |
|---------|------|--------|
| H.264 GPU Decode | ❌ CPU only | ✅ GPU accelerated |
| H.265 GPU Decode | ❌ CPU only | ✅ GPU accelerated |
| AV1 Support | ❌ No | ✅ Yes (18.5+) |
| DNxHR/ProRes | ✅ Yes | ✅ Yes |

### Usage Examples

```bash
# Check video for DaVinci Resolve Studio
videowise davinci_resolve video.mp4

# Check for Free version (no GPU decode)
videowise davinci_resolve video.mp4 --version free
```

### Transcoding for Resolve

```bash
# Transcode to DNxHR SQ for HD editing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_sq -c:a pcm_s16le output.mov

# Transcode to DNxHR HQ for 4K editing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_hq -c:a pcm_s16le output.mov

# Create ProRes Proxy for 4K+ workflows
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 0 -c:a pcm_s16le output.mov
```

### Performance Tips

1. **Use NVMe SSDs** for media storage (3000+ MB/s read speeds)
2. **Generate Optimized Media** for H.264/H.265 in Free version
3. **Enable GPU acceleration** in Preferences > Memory & GPU
4. **Use Proxies for 4K+** to enable smooth playback on moderate hardware

---

## Adobe Premiere Pro

**Optimal Codecs:** DNxHR, ProRes (Mac), H.264/H.265 with hardware acceleration

### Best Practices

#### Platform Differences
| Platform | ProRes Support | Recommendation |
|----------|----------------|----------------|
| **macOS** | ✅ Native, hardware accelerated | Use ProRes 422 or ProRes 422 HQ |
| **Windows** | ⚠️ Requires license/payment | Use DNxHR SQ or DNxHR HQ |

#### Codec Recommendations by Resolution
- **1080p:** DNxHR SQ, ProRes 422, or H.264 (50 Mbps+)
- **4K:** DNxHR HQ, ProRes 422 HQ, or H.265 (100 Mbps+)
- **8K:** DNxHR HQX or ProRes 422 HQ (intraframe required)

### Hardware Acceleration

**Enable in:** File > Project Settings > General > Video Rendering and Playback

- **Intel:** QuickSync (H.264, H.265)
- **NVIDIA:** NVENC (H.264, H.265, AV1)
- **AMD:** VCE (H.264, H.265)

### Proxy Workflow

**Setup:** File > Project Settings > Ingest Settings

1. Check "Ingest"
2. Check "Create Proxies"
3. Choose format: H.264 Low Resolution or ProRes Proxy
4. Premiere auto-generates proxies on import

### Usage Examples

```bash
# Check video for Premiere Pro on Mac
videowise premiere_pro video.mp4 --platform mac

# Check video for Premiere Pro on Windows
videowise premiere_pro video.mp4 --platform windows
```

### Transcoding for Premiere

```bash
# DNxHR SQ for Windows editing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_sq -c:a pcm_s16le output.mov

# ProRes 422 for Mac editing
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 -c:a pcm_s16le output.mov

# H.264 optimized for editing (high bitrate, intra-frame)
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 15 -g 1 -c:a aac output.mp4
```

### Performance Tips

1. **Enable Hardware Acceleration** for H.264/H.265
2. **Use Ingest to create proxies** automatically on import
3. **Match sequence settings** to footage to avoid re-rendering
4. **Purge cache regularly** (Edit > Preferences > Media Cache)

---

## Final Cut Pro

**Optimal Codecs:** ProRes (all variants)

### Best Practices

#### Native ProRes on Apple Silicon

Final Cut Pro has **hardware-accelerated ProRes encode/decode** on M1/M2/M3/M4 Macs:

- M1/M2/M3/M4 can handle **multiple streams** of 4K ProRes in real-time
- ProRes 422 Proxy enables smooth editing on MacBook Air

#### Codec Recommendations
- **Laptop Editing (MacBook Air/Pro):** ProRes Proxy or ProRes LT
- **Desktop Editing (iMac/Mac Studio):** ProRes 422 or ProRes 422 HQ
- **High-End Finishing:** ProRes 422 HQ or ProRes 4444
- **Alpha Channel Workflows:** ProRes 4444

### Optimized vs. Proxy Media

| Workflow | When to Use | Format |
|----------|-------------|--------|
| **Optimized Media** | Non-ProRes footage (H.264/H.265) | ProRes 422 |
| **Proxy Media** | 4K+ footage, laptop editing | ProRes Proxy |

Final Cut Pro will **prompt you** to create Optimized Media when importing H.264/H.265.

### Usage Examples

```bash
# Check video for Final Cut Pro
videowise final_cut_pro video.mp4
```

### Transcoding for Final Cut Pro

```bash
# ProRes 422 for standard editing
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 -c:a pcm_s16le output.mov

# ProRes Proxy for 4K+ laptop editing
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 0 -c:a pcm_s16le output.mov

# ProRes 4444 for alpha channel workflows
ffmpeg -i input.mov -c:v prores_ks -profile:v 4 -c:a pcm_s16le output.mov
```

### Performance Tips

1. **Let FCP create Optimized Media** for H.264/H.265 footage
2. **Use Proxy Media** for 4K on MacBook Air/Pro
3. **Match timeline settings** to your delivery format
4. **Background rendering** happens automatically in idle time

---

## Avid Media Composer

**Optimal Codecs:** DNxHD (HD only), DNxHR (all resolutions)
**Required Container:** MXF (Material Exchange Format)

### Best Practices

#### Avid's Native Workflow

Avid Media Composer is **extremely strict** about codec conformity:
- Projects lock to specific frame rates
- All footage should be **transcoded to DNxHD/DNxHR on import**
- MXF container is required for native editing

#### DNxHD vs. DNxHR
| Codec | Resolution Support | Use Case |
|-------|-------------------|----------|
| **DNxHD** | Up to 1080p only | HD broadcast workflows |
| **DNxHR LB** | All resolutions | Proxy/offline editing |
| **DNxHR SQ** | All resolutions | Standard quality online |
| **DNxHR HQ** | All resolutions | High quality broadcast |
| **DNxHR HQX** | All resolutions | 10-bit 4:2:2 finishing |
| **DNxHR 444** | All resolutions | 10-bit 4:4:4 VFX/grading |

### AMA (Avid Media Access)

**AMA links** to non-Avid formats (H.264, ProRes) without importing:
- Good for quick review
- **Not recommended** for actual editing or collaboration
- **Always transcode** to DNxHR for serious projects

### Usage Examples

```bash
# Check video for Avid Media Composer
videowise avid_media_composer video.mp4
```

### Transcoding for Avid

```bash
# DNxHR SQ in MXF for HD/4K broadcast
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_sq -f mxf output.mxf

# DNxHR HQ in MXF for high-quality finishing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_hq -f mxf output.mxf

# DNxHR LB in MXF for proxy editing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_lb -f mxf output.mxf
```

### Performance Tips

1. **Transcode everything to DNxHR** during import
2. **Use MXF container** for native Avid workflows
3. **Conform frame rates** before importing (23.976, 24, 25, 29.97, 59.94)
4. **Use DNxHR LB** for offline editing to save storage space

---

## Adobe After Effects

**Optimal Codecs:** ProRes, DNxHR, Image Sequences (PNG, TIFF, EXR)

### Best Practices

#### Why Image Sequences?

For **VFX and compositing**, image sequences are superior to video files:
- **Frame-accurate scrubbing** (no GOP structures)
- **No re-encoding** when rendering specific frames
- **Easy to replace** individual frames
- **Alpha channel support** (PNG, TIFF, EXR)

#### Codec Recommendations by Workflow
| Workflow | Input Format | Output Format |
|----------|--------------|---------------|
| **Motion Graphics** | ProRes 4444 | ProRes 4444 (with alpha) |
| **VFX Compositing** | PNG/EXR sequence | PNG/EXR sequence |
| **Color Grading** | ProRes 422 HQ | ProRes 422 HQ |
| **Client Review** | H.264 (acceptable) | H.264 (delivery) |

### RAM Preview Performance

**Intraframe codecs** (ProRes, DNxHR) enable fast RAM previews:
- Each frame decodes independently
- Smooth scrubbing in timeline
- Fast reverse playback

**Interframe codecs** (H.264, H.265) are slow:
- Must decode entire GOP for each frame
- Stuttery scrubbing
- Poor performance with effects

### Multi-Frame Rendering

**Enable for 4K+ compositions:**
Edit > Preferences > Memory & Performance > Enable Multi-Frame Rendering

- Uses multiple CPU cores simultaneously
- Speeds up previews and final renders
- Requires sufficient RAM (32GB+ recommended)

### Usage Examples

```bash
# Check video for After Effects (motion graphics workflow)
videowise after_effects video.mp4 --workflow motion_graphics

# Check video for After Effects (VFX workflow)
videowise after_effects video.mp4 --workflow vfx
```

### Transcoding for After Effects

```bash
# ProRes 422 for general compositing
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 -c:a pcm_s16le output.mov

# ProRes 4444 for motion graphics with alpha
ffmpeg -i input.mov -c:v prores_ks -profile:v 4 -c:a pcm_s16le output.mov

# Convert video to PNG sequence (VFX workflow)
ffmpeg -i input.mp4 output_%04d.png

# Convert PNG sequence back to video
ffmpeg -framerate 24 -i frame_%04d.png -c:v prores_ks -profile:v 2 output.mov
```

### Performance Tips

1. **Use image sequences** for VFX-heavy projects
2. **Transcode H.264/H.265** to ProRes before importing
3. **Enable Multi-Frame Rendering** for 4K+ compositions
4. **Reduce preview resolution** (Quarter or Half) during work
5. **Purge cache** (Edit > Purge > All Memory & Disk Cache)

---

## Quick Reference Table

| Platform | Optimal Codec(s) | Container | Notes |
|----------|------------------|-----------|-------|
| **DaVinci Resolve** | DNxHR, ProRes | MOV, MXF | Studio has GPU decode for H.264/H.265 |
| **Premiere Pro** | DNxHR (Win), ProRes (Mac) | MOV, MXF | Hardware acceleration for H.264/H.265 |
| **Final Cut Pro** | ProRes (all variants) | MOV | Hardware accelerated on Apple Silicon |
| **Avid Media Composer** | DNxHD (HD), DNxHR (all) | MXF | Strict conformity; transcode everything |
| **After Effects** | ProRes, PNG sequence | MOV, N/A | Image sequences best for VFX |

---

## Transcoding Recipes

### DNxHR Quality Levels Explained

```bash
# DNxHR LB (Low Bandwidth) - Proxy editing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_lb -c:a pcm_s16le output.mov

# DNxHR SQ (Standard Quality) - Broadcast standard
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_sq -c:a pcm_s16le output.mov

# DNxHR HQ (High Quality) - High-end broadcast
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_hq -c:a pcm_s16le output.mov

# DNxHR HQX (High Quality 10-bit) - Finishing
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_hqx -c:a pcm_s16le output.mov

# DNxHR 444 (4:4:4 10-bit) - VFX and color grading
ffmpeg -i input.mp4 -c:v dnxhd -profile:v dnxhr_444 -c:a pcm_s16le output.mov
```

### ProRes Quality Levels Explained

```bash
# ProRes Proxy (profile 0) - Proxy editing
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 0 -c:a pcm_s16le output.mov

# ProRes LT (profile 1) - Light compression
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 1 -c:a pcm_s16le output.mov

# ProRes 422 (profile 2) - Standard quality
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 2 -c:a pcm_s16le output.mov

# ProRes 422 HQ (profile 3) - High quality
ffmpeg -i input.mp4 -c:v prores_ks -profile:v 3 -c:a pcm_s16le output.mov

# ProRes 4444 (profile 4) - Alpha channel support
ffmpeg -i input.mov -c:v prores_ks -profile:v 4 -c:a pcm_s16le output.mov

# ProRes 4444 XQ (profile 5) - Highest quality
ffmpeg -i input.mov -c:v prores_ks -profile:v 5 -c:a pcm_s16le output.mov
```

### Converting to Image Sequences

```bash
# Extract as PNG sequence (lossless with alpha)
ffmpeg -i input.mov frame_%04d.png

# Extract as TIFF sequence (lossless, larger files)
ffmpeg -i input.mov frame_%04d.tiff

# Extract as EXR sequence (32-bit float, HDR)
ffmpeg -i input.mov -pix_fmt rgb48le frame_%04d.exr

# Reassemble PNG sequence to ProRes
ffmpeg -framerate 24 -i frame_%04d.png -c:v prores_ks -profile:v 2 output.mov
```

### H.264 Optimized for Editing

If you must use H.264, optimize it for editing:

```bash
# High bitrate, all-intra H.264 (no inter-frame compression)
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset slow \
  -crf 15 \
  -g 1 \
  -c:a aac -b:a 320k \
  output.mp4
```

**Explanation:**
- `-crf 15`: Very high quality (lower = better quality)
- `-g 1`: All-intra (every frame is a keyframe)
- This creates a ~150-200 Mbps H.264 file that scrubs like intraframe

---

## Storage Requirements

### Bitrate Comparison (1080p, 24fps)

| Codec | Approximate Bitrate | 1 min File Size |
|-------|--------------------|-----------------|
| ProRes Proxy | 45 Mbps | 337 MB |
| ProRes LT | 102 Mbps | 765 MB |
| ProRes 422 | 147 Mbps | 1.1 GB |
| ProRes 422 HQ | 220 Mbps | 1.65 GB |
| DNxHR LB | 36 Mbps | 270 MB |
| DNxHR SQ | 145 Mbps | 1.08 GB |
| DNxHR HQ | 290 Mbps | 2.17 GB |
| H.264 (50 Mbps) | 50 Mbps | 375 MB |

### Recommended Storage

- **Laptop editing:** 1TB NVMe SSD minimum (ProRes Proxy workflows)
- **Desktop editing:** 2TB+ NVMe SSD (ProRes 422 or DNxHR SQ)
- **Professional workflows:** 4TB+ RAID array (ProRes HQ or DNxHR HQ)

---

## Common Questions

### Why not just edit H.264?

**H.264 is a delivery codec, not an editing codec:**
- Interframe compression requires decoding multiple frames to display one
- Scrubbing backwards/forwards is slow
- Effects and color grading are CPU-intensive
- Multiple layers cause timeline stuttering

**Intraframe codecs (ProRes, DNxHR) are designed for editing:**
- Each frame decodes independently
- Smooth scrubbing in any direction
- Low CPU overhead for effects
- Multiple layers play back smoothly

### When should I use proxies?

**Use proxy workflows when:**
- Editing 4K+ footage on a laptop
- Working with high bitrate codecs (ProRes HQ, DNxHR HQ)
- Your timeline has many layers/effects
- Storage space is limited

**Proxy workflow benefits:**
- Smooth playback on moderate hardware
- Faster scrubbing and timeline response
- 90% reduction in file size
- Final render uses original high-quality media

### Can I mix codecs in a timeline?

**Yes, but not recommended:**
- Modern NLEs can handle mixed codecs
- Performance suffers when switching between codec types
- Best practice: transcode everything to the same codec
- Exception: Proxy workflows intentionally use mixed media

### What about RAW formats?

**Camera RAW formats** (BRAW, ProRes RAW, R3D, etc.) are specialized:
- DaVinci Resolve has best RAW support (especially BRAW)
- Final Cut Pro supports ProRes RAW natively
- Premiere Pro supports most RAW formats via plugins
- After Effects can import RAW via Dynamic Link

**RAW workflow recommendation:**
- Edit in native RAW codec if supported (best quality)
- Otherwise, transcode to ProRes 422 HQ or DNxHR HQ

---

## Troubleshooting

### "Codec not supported" errors

**Avid Media Composer:**
- Only accepts DNxHD/DNxHR natively
- Use AMA for other formats (not recommended for editing)
- **Solution:** Transcode to DNxHR in MXF container

**Final Cut Pro:**
- Prompts to create Optimized Media for H.264/H.265
- **Solution:** Let FCP transcode, or pre-transcode to ProRes

**Premiere Pro on Windows:**
- ProRes decode requires license
- **Solution:** Use DNxHR instead of ProRes

### Slow playback / dropped frames

**Common causes:**
1. Interframe codec (H.264/H.265) without GPU acceleration
2. Very high bitrate footage exceeding storage bandwidth
3. Multiple layers without proxy media
4. Insufficient RAM for resolution

**Solutions:**
1. Enable hardware acceleration (if available)
2. Transcode to intraframe codec (ProRes, DNxHR)
3. Generate proxy media for 4K+ footage
4. Reduce playback resolution (Half or Quarter)

### Color shifts after transcoding

**Likely causes:**
- Color space mismatch (Rec.709 vs. Rec.2020)
- Incorrect gamma curve

**Solution:**
```bash
# Force Rec.709 color space
ffmpeg -i input.mp4 \
  -c:v prores_ks -profile:v 2 \
  -color_primaries bt709 \
  -color_trc bt709 \
  -colorspace bt709 \
  output.mov
```

---

## Additional Resources

### Official Documentation
- [DaVinci Resolve Manual](https://www.blackmagicdesign.com/support)
- [Premiere Pro Help](https://helpx.adobe.com/premiere-pro/user-guide.html)
- [Final Cut Pro User Guide](https://support.apple.com/guide/final-cut-pro)
- [Avid Media Composer Documentation](https://www.avid.com/media-composer/documentation)
- [After Effects User Guide](https://helpx.adobe.com/after-effects/user-guide.html)

### Codec Information
- [DNxHR/DNxHD Specifications](https://www.avid.com/dnxhd)
- [ProRes White Paper](https://www.apple.com/final-cut-pro/docs/Apple_ProRes_White_Paper.pdf)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
