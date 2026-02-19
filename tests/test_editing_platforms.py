"""Tests for editing platform compatibility checkers.

This module tests compatibility checkers for professional video editing software:
- DaVinci Resolve
- Adobe Premiere Pro
- Final Cut Pro
- Avid Media Composer
- After Effects
"""

import pytest

from videowise.compatibility import CompatibilityLevel
from videowise.editing_platforms import (
    AdobePremiereProChecker,
    AfterEffectsChecker,
    AvidMediaComposerChecker,
    DaVinciResolveChecker,
    FinalCutProChecker,
)

# =============================================================================
# DaVinci Resolve Tests (10 tests)
# =============================================================================


def test_davinci_dnxhd_optimal():
    """Test DNxHD is optimal for DaVinci Resolve."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any("optimal" in issue.message.lower() for issue in issues)
    assert any("dnxhd" in issue.message.lower() for issue in issues)


def test_davinci_dnxhr_4k_optimal():
    """Test DNxHR is optimal for 4K editing in DaVinci."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "dnxhr",
        "container": "mov",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "optimal" in issue.message.lower() or "4k" in issue.message.lower() for issue in issues
    )


def test_davinci_prores_apple_silicon():
    """Test ProRes hardware acceleration on Apple Silicon."""
    checker = DaVinciResolveChecker(platform="mac_apple_silicon")
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "apple silicon" in issue.message.lower() or "hardware" in issue.message.lower()
        for issue in issues
    )


def test_davinci_prores_intel_mac():
    """Test ProRes on Intel Mac (no hardware acceleration)."""
    checker = DaVinciResolveChecker(platform="mac_intel")
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # Should still be compatible, just without Apple Silicon acceleration
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_davinci_h264_warning():
    """Test H.264 gets re-encoding warning for heavy editing."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any(
        "re-encod" in issue.message.lower() or "transcode" in issue.message.lower()
        for issue in issues
    )


def test_davinci_braw_raw_format():
    """Test BRAW (Blackmagic RAW) detection."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "braw",
        "container": "braw",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "raw" in issue.message.lower() or "braw" in issue.message.lower() for issue in issues
    )
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_davinci_10bit_color_depth():
    """Test 10-bit color depth recommendation for grading."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "prores422hq",
        "container": "mov",
        "resolution": (1920, 1080),
        "bit_depth": 10,
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "10-bit" in issue.message.lower() or "color" in issue.message.lower() for issue in issues
    )


def test_davinci_mxf_container():
    """Test MXF container support in DaVinci."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_davinci_h265_4k_decode():
    """Test H.265 decode support for 4K."""
    checker = DaVinciResolveChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "decode" in issue.message.lower() or "4k" in issue.message.lower() for issue in issues
    )


def test_davinci_free_vs_studio():
    """Test Free version limitations vs Studio."""
    checker_free = DaVinciResolveChecker(version="free")
    checker_studio = DaVinciResolveChecker(version="studio")

    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (3840, 2160),
    }

    issues_free = checker_free.check(video_info)
    issues_studio = checker_studio.check(video_info)

    # Both should work but free might have warnings
    assert len(issues_free) >= 1
    assert len(issues_studio) >= 1


# =============================================================================
# Adobe Premiere Pro Tests (10 tests)
# =============================================================================


def test_premiere_prores_native():
    """Test ProRes is native codec in Premiere."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "native" in issue.message.lower() or "prores" in issue.message.lower() for issue in issues
    )
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_premiere_dnxhd_native():
    """Test DNxHD is native codec in Premiere."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "native" in issue.message.lower() or "dnxhd" in issue.message.lower() for issue in issues
    )


def test_premiere_h264_level_51_4k():
    """Test H.264 Level 5.1 validation for 4K."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "h264",
        "profile": "high",
        "level": "5.1",
        "container": "mp4",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "level" in issue.message.lower() or "4k" in issue.message.lower() for issue in issues
    )


def test_premiere_mercury_engine():
    """Test Mercury Playback Engine GPU acceleration."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "mercury" in issue.message.lower()
        or "gpu" in issue.message.lower()
        or "hardware" in issue.message.lower()
        for issue in issues
    )


def test_premiere_vfr_warning():
    """Test VFR (Variable Frame Rate) warning for timeline stability."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "frame_rate": "variable",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any(
        "vfr" in issue.message.lower() or "variable" in issue.message.lower() for issue in issues
    )


def test_premiere_high_bitrate_4k():
    """Test high bitrate warning for 4K footage."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 150_000_000,  # 150 Mbps
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # High bitrate should trigger performance warning
    assert any(
        "bitrate" in issue.message.lower() or "performance" in issue.message.lower()
        for issue in issues
    )


def test_premiere_proxy_workflow_8k():
    """Test proxy workflow recommendation for 8K."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "h265",
        "container": "mp4",
        "resolution": (7680, 4320),  # 8K
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "proxy" in issue.message.lower() or "8k" in issue.message.lower() for issue in issues
    )


def test_premiere_red_raw():
    """Test RED RAW format support."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "r3d",
        "container": "r3d",
        "resolution": (4096, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any("red" in issue.message.lower() or "raw" in issue.message.lower() for issue in issues)


def test_premiere_multicam_codec():
    """Test multi-cam editing codec recommendations."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # DNxHD should be recommended for multi-cam
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_premiere_xavc_native():
    """Test XAVC native codec support."""
    checker = AdobePremiereProChecker()
    video_info = {
        "codec": "xavc",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "native" in issue.message.lower() or "xavc" in issue.message.lower() for issue in issues
    )


# =============================================================================
# Final Cut Pro Tests (10 tests)
# =============================================================================


def test_finalcut_prores_optimal():
    """Test ProRes is optimal for Final Cut Pro."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any("prores" in issue.message.lower() for issue in issues)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_finalcut_prores_apple_silicon():
    """Test ProRes hardware acceleration on Apple Silicon."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "apple silicon" in issue.message.lower() or "hardware" in issue.message.lower()
        for issue in issues
    )


def test_finalcut_prores_raw():
    """Test ProRes RAW support in Final Cut Pro."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "prores_raw",
        "container": "mov",
        "resolution": (4096, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any("raw" in issue.message.lower() for issue in issues)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_finalcut_h264_hardware_decode():
    """Test H.264 hardware decode on Mac."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "hardware" in issue.message.lower() or "decode" in issue.message.lower() for issue in issues
    )


def test_finalcut_hevc_hardware_decode():
    """Test HEVC hardware decode on Mac."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "hevc",
        "container": "mov",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "hardware" in issue.message.lower() or "hevc" in issue.message.lower() for issue in issues
    )


def test_finalcut_mov_container_native():
    """Test MOV container is native to Final Cut Pro."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "mov" in issue.message.lower() or "quicktime" in issue.message.lower() for issue in issues
    )


def test_finalcut_optimized_media():
    """Test Optimized Media workflow detection."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "h265",
        "container": "mp4",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # HEVC should suggest Optimized Media workflow
    assert any("optimized" in issue.message.lower() for issue in issues)


def test_finalcut_magnetic_timeline():
    """Test codec recommendations for Magnetic Timeline."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "prores422",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_finalcut_background_rendering():
    """Test background rendering suggestion for complex codecs."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "h265",
        "container": "mp4",
        "resolution": (3840, 2160),
        "bitrate": 100_000_000,
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # High complexity should mention background rendering
    assert any(
        "render" in issue.message.lower() or "background" in issue.message.lower()
        for issue in issues
    )


def test_finalcut_iphone_footage():
    """Test iPhone/iPad footage optimization."""
    checker = FinalCutProChecker()
    video_info = {
        "codec": "hevc",
        "container": "mov",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # HEVC in MOV (typical iPhone format) should be well supported
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# =============================================================================
# Avid Media Composer Tests (10 tests)
# =============================================================================


def test_avid_dnxhd_native():
    """Test DNxHD is native codec in Avid."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "native" in issue.message.lower() or "optimal" in issue.message.lower() for issue in issues
    )
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_avid_dnxhr_4k():
    """Test DNxHR for 4K in Avid."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhr",
        "container": "mxf",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "dnxhr" in issue.message.lower() or "4k" in issue.message.lower() for issue in issues
    )


def test_avid_mxf_container_required():
    """Test MXF container requirement for Avid."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # MOV with DNxHD should warn about MXF preference
    assert any("mxf" in issue.message.lower() for issue in issues)


def test_avid_op1a_structure():
    """Test OP1a MXF structure validation."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "mxf_structure": "op1a",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "op1a" in issue.message.lower() or "mxf" in issue.message.lower() for issue in issues
    )


def test_avid_prores_collaboration():
    """Test ProRes support for collaboration with Final Cut Pro."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any("prores" in issue.message.lower() for issue in issues)
    # Should mention collaboration or compatibility
    assert any(
        "collaboration" in issue.message.lower() or "compatible" in issue.message.lower()
        for issue in issues
    )


def test_avid_h264_ama_linking():
    """Test H.264 AMA linking with transcoding recommendation."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "ama" in issue.message.lower() or "transcode" in issue.message.lower() for issue in issues
    )


def test_avid_codec_pack_requirement():
    """Test Avid codec pack requirement for third-party formats."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "xavc",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # Third-party codec should mention codec pack or AMA
    assert any(
        "codec" in issue.message.lower() or "ama" in issue.message.lower() for issue in issues
    )


def test_avid_mediacentral_cloud():
    """Test MediaCentral | Cloud collaboration format."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # DNxHD in MXF is ideal for MediaCentral
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_avid_broadcast_audio():
    """Test broadcast-compliant audio validation."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "audio_codec": "pcm",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # PCM audio should be mentioned as broadcast-compliant
    assert any(
        "audio" in issue.message.lower() or "pcm" in issue.message.lower() for issue in issues
    )


def test_avid_aaf_export():
    """Test AAF export compatibility."""
    checker = AvidMediaComposerChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mxf",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # DNxHD in MXF is perfect for AAF workflows
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# =============================================================================
# After Effects Tests (10 tests)
# =============================================================================


def test_aftereffects_prores4444_alpha():
    """Test ProRes 4444 with alpha channel is optimal."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "alpha" in issue.message.lower() or "4444" in issue.message.lower() for issue in issues
    )
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_aftereffects_animation_codec():
    """Test Animation Codec support for lossless alpha."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "qtrle",  # QuickTime Animation
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(
        "animation" in issue.message.lower() or "lossless" in issue.message.lower()
        for issue in issues
    )


def test_aftereffects_png_sequence_recommended():
    """Test PNG sequence recommendation over video files."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # Should suggest PNG/TIFF sequence for motion graphics work
    assert any(
        "sequence" in issue.message.lower() or "png" in issue.message.lower() for issue in issues
    )


def test_aftereffects_h264_warning():
    """Test H.264 warning for intermediate renders."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any(
        "h.264" in issue.message.lower() or "avoid" in issue.message.lower() for issue in issues
    )


def test_aftereffects_ram_preview():
    """Test RAM preview codec optimization."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores422",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # ProRes should be good for RAM preview
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_aftereffects_dynamic_link():
    """Test Dynamic Link compatibility with Premiere Pro."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # Should mention Dynamic Link or Premiere compatibility
    assert any(
        "dynamic link" in issue.message.lower() or "premiere" in issue.message.lower()
        for issue in issues
    )


def test_aftereffects_gpu_acceleration():
    """Test GPU-accelerated codec support."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # Should mention GPU or performance
    assert any(
        "gpu" in issue.message.lower() or "performance" in issue.message.lower() for issue in issues
    )


def test_aftereffects_render_queue():
    """Test Render Queue output format validation."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # ProRes 4444 is perfect for Render Queue output
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_aftereffects_multi_machine_rendering():
    """Test multi-machine rendering codec requirements."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "prores422",
        "container": "mov",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # ProRes should work well for multi-machine rendering
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_aftereffects_alpha_preservation():
    """Test alpha channel preservation checks."""
    checker = AfterEffectsChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }
    issues = checker.check(video_info)

    assert len(issues) >= 1
    # H.264 doesn't support alpha, should be warned
    assert any("alpha" in issue.message.lower() for issue in issues)
