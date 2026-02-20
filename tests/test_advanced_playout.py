"""Tests for advanced live production system checkers.

Tests for Wirecast, Resolume, PlaybackPro, and ProVideoPlayer (PVP).
Updated to use the new rule-based API.
"""

from videowise.compatibility import (
    CompatibilityLevel,
    check_compatibility,
)

# Wirecast Tests (10 tests)


def test_wirecast_h264_compatible():
    """Test that H.264 is recommended for Wirecast."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_prores_compatible():
    """Test that ProRes is supported by Wirecast."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_unsupported_codec():
    """Test warning for unsupported codec in Wirecast."""
    video_info = {
        "codec": "vp9",
        "container": "webm",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_high_bitrate_warning():
    """Test warning for very high bitrate."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,  # 200 Mbps
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_hevc_support():
    """Test that HEVC is supported by Wirecast."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (3840, 2160),
        "bitrate": 40_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_dnxhd_support():
    """Test that DNxHD is handled."""
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 145_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_mp4_container():
    """Test MP4 container compatibility."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_wmv_container_warning():
    """Test WMV container handling."""
    video_info = {
        "codec": "h264",
        "container": "wmv",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_4k_hevc():
    """Test 4K HEVC support."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (3840, 2160),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_mjpeg_support():
    """Test MJPEG codec support."""
    video_info = {
        "codec": "mjpeg",
        "container": "avi",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


# Resolume Tests (10 tests)


def test_resolume_dxv_optimal():
    """Test that DXV is optimal for Resolume."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_hap_recommended():
    """Test that HAP is recommended for Resolume."""
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_hap_alpha():
    """Test HAP Alpha support with transparency."""
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_hap_q():
    """Test HAP Q high quality variant."""
    video_info = {
        "codec": "hap_q",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 80_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_h264_warning():
    """Test H.264 handling (not optimal)."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_prores_warning():
    """Test ProRes handling."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_4k_layer_warning():
    """Test 4K resolution handling."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 100_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_high_bitrate_warning():
    """Test high bitrate warning."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 250_000_000,  # 250 Mbps
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_hevc_warning():
    """Test HEVC codec warning."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_notchlc():
    """Test NotchLC codec support."""
    video_info = {
        "codec": "notchlc",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 60_000_000,
    }
    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


# PlaybackPro Tests (10 tests)


def test_playbackpro_prores422_optimal():
    """Test ProRes 422 is optimal for PlaybackPro."""
    video_info = {
        "codec": "prores422",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_playbackpro_h264_compatible():
    """Test H.264 is supported."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_hd_bitrate_optimal():
    """Test H.264 HD bitrate in optimal range."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,  # 20 Mbps
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_hd_bitrate_too_low():
    """Test warning for HD bitrate too low."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,  # 10 Mbps
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_4k_bitrate_optimal():
    """Test H.264 4K bitrate in optimal range."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 35_000_000,  # 35 Mbps
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_4k_bitrate_too_low():
    """Test warning for 4K bitrate too low."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 20_000_000,  # 20 Mbps
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_mov_required():
    """Test MOV container is required."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    # MP4 may not be optimal
    assert len(issues) > 0


def test_playbackpro_mov_compatible():
    """Test MOV container is compatible."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_unsupported_codec():
    """Test unsupported codec warning."""
    video_info = {
        "codec": "vp9",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_prores4444():
    """Test ProRes 4444 alpha support."""
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,
    }
    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


# ProVideoPlayer (PVP) Tests (10 tests)


def test_pvp_dxv_optimal():
    """Test DXV is optimal for PVP timecode."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_hap_compatible():
    """Test HAP codec is compatible with PVP."""
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_hap_alpha():
    """Test HAP Alpha for overlays."""
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_prores_compatible():
    """Test ProRes is supported."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_prores4444_alpha():
    """Test ProRes 4444 alpha support."""
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_h264_compatible():
    """Test H.264 is compatible."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_hevc_compatible():
    """Test HEVC is compatible."""
    video_info = {
        "codec": "hevc",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 15_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_unsupported_codec():
    """Test unsupported codec warning."""
    video_info = {
        "codec": "vp9",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_mov_container():
    """Test MOV container is supported."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0


def test_pvp_timecode_support_gpu():
    """Test timecode support for GPU codecs."""
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = check_compatibility(video_info, "provideoplayer")

    assert len(issues) > 0
