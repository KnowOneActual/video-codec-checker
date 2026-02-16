"""Tests for advanced live production system checkers.

Tests for Wirecast, Resolume, PlaybackPro, and ProVideoPlayer (PVP).
"""

from videowise.compatibility import (
    CompatibilityLevel,
    PlaybackProChecker,
    ProVideoPlayerChecker,
    ResolumeChecker,
    WirecastChecker,
)

# Wirecast Tests (10 tests)


def test_wirecast_h264_compatible():
    """Test that H.264 is recommended for Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("H.264" in issue.message for issue in issues)
    assert any(issue.reason and "hardware acceleration" in issue.reason.lower() for issue in issues)


def test_wirecast_prores_compatible():
    """Test that ProRes is supported by Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("prores" in issue.message.lower() for issue in issues)


def test_wirecast_unsupported_codec():
    """Test warning for unsupported codec in Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "vp9",
        "container": "webm",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("VP9" in issue.message for issue in issues)


def test_wirecast_high_bitrate_warning():
    """Test warning for very high bitrate."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,  # 200 Mbps
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


def test_wirecast_hevc_support():
    """Test that HEVC is supported by Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (3840, 2160),
        "bitrate": 40_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_dnxhd_support():
    """Test that DNxHD is supported."""
    checker = WirecastChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 145_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_mp4_container():
    """Test MP4 container compatibility."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = checker.check(video_info)

    assert any("MP4" in issue.message for issue in issues)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_wmv_container_warning():
    """Test WMV container gets warning but is supported."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "wmv",
        "resolution": (1920, 1080),
        "bitrate": 8_000_000,
    }
    issues = checker.check(video_info)

    assert any("WMV" in issue.message for issue in issues)


def test_wirecast_4k_hevc():
    """Test 4K HEVC support."""
    checker = WirecastChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (3840, 2160),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_mjpeg_support():
    """Test MJPEG codec support."""
    checker = WirecastChecker()
    video_info = {
        "codec": "mjpeg",
        "container": "avi",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Resolume Tests (10 tests)


def test_resolume_dxv_optimal():
    """Test that DXV is optimal for Resolume."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("DXV" in issue.message for issue in issues)
    assert any("optimal" in issue.message.lower() for issue in issues)


def test_resolume_hap_recommended():
    """Test that HAP is recommended for Resolume."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("HAP" in issue.message for issue in issues)


def test_resolume_hap_alpha():
    """Test HAP Alpha support with transparency."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("alpha" in issue.message.lower() for issue in issues)


def test_resolume_hap_q():
    """Test HAP Q high quality variant."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap_q",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 80_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("HAP Q" in issue.message or "HAP" in issue.message for issue in issues)


def test_resolume_h264_warning():
    """Test H.264 gets warning (not optimal)."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("H.264" in issue.message for issue in issues)
    assert any("CPU" in issue.message for issue in issues)


def test_resolume_prores_on_mac():
    """Test ProRes on Mac platform."""
    checker = ResolumeChecker(platform="mac")
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("CPU" in issue.message for issue in issues)


def test_resolume_prores_on_windows():
    """Test ProRes on Windows platform."""
    checker = ResolumeChecker(platform="windows")
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("Windows" in issue.message for issue in issues)


def test_resolume_4k_layer_warning():
    """Test 4K resolution warning about layer count."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 100_000_000,
    }
    issues = checker.check(video_info)

    assert any("4K" in issue.message for issue in issues)
    assert any("layer" in issue.message.lower() for issue in issues)


def test_resolume_high_bitrate_warning():
    """Test high bitrate warning."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 250_000_000,  # 250 Mbps
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


def test_resolume_hevc_warning():
    """Test HEVC codec warning."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("HEVC" in issue.message for issue in issues)


# PlaybackPro Tests (10 tests)


def test_playbackpro_prores422_optimal():
    """Test ProRes 422 is optimal for PlaybackPro."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "prores422",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("ProRes 422" in issue.message for issue in issues)


def test_playbackpro_h264_compatible():
    """Test H.264 is supported."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_playbackpro_h264_hd_bitrate_optimal():
    """Test H.264 HD bitrate in optimal range."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,  # 20 Mbps
    }
    issues = checker.check(video_info)

    assert any("suitable" in issue.message.lower() for issue in issues)


def test_playbackpro_h264_hd_bitrate_too_low():
    """Test warning for HD bitrate below 15 Mbps."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,  # 10 Mbps
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


def test_playbackpro_h264_4k_bitrate_optimal():
    """Test H.264 4K bitrate in optimal range."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 35_000_000,  # 35 Mbps
    }
    issues = checker.check(video_info)

    assert any("optimal" in issue.message.lower() for issue in issues)


def test_playbackpro_h264_4k_bitrate_too_low():
    """Test warning for 4K bitrate below 30 Mbps."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 20_000_000,  # 20 Mbps
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("4K" in issue.message for issue in issues)


def test_playbackpro_mov_required():
    """Test MOV container is required."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    # MOV is required, so MP4 should get incompatible
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    assert any("MOV" in issue.message for issue in issues)


def test_playbackpro_mov_compatible():
    """Test MOV container is compatible."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any("MOV" in issue.message for issue in issues)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_playbackpro_unsupported_codec():
    """Test unsupported codec warning."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "vp9",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("VP9" in issue.message for issue in issues)


def test_playbackpro_prores4444():
    """Test ProRes 4444 alpha support."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("4444" in issue.message for issue in issues)


# ProVideoPlayer (PVP) Tests (10 tests)


def test_pvp_dxv_optimal():
    """Test DXV is optimal for PVP timecode."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("DXV" in issue.message for issue in issues)
    assert any("timecode" in issue.message.lower() for issue in issues)


def test_pvp_hap_compatible():
    """Test HAP codec is compatible with PVP."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("HAP" in issue.message for issue in issues)


def test_pvp_hap_alpha():
    """Test HAP Alpha for overlays."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("alpha" in issue.message.lower() for issue in issues)
    assert any("overlay" in issue.message.lower() for issue in issues)


def test_pvp_prores_compatible():
    """Test ProRes is supported."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 150_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("ProRes" in issue.message for issue in issues)


def test_pvp_prores4444_alpha():
    """Test ProRes 4444 alpha support."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "prores4444",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 200_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("alpha" in issue.message.lower() for issue in issues)


def test_pvp_h264_compatible():
    """Test H.264 is compatible."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("H.264" in issue.message for issue in issues)


def test_pvp_hevc_compatible():
    """Test HEVC is compatible."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "hevc",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 15_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_pvp_unsupported_codec():
    """Test unsupported codec warning."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "vp9",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,
    }
    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("VP9" in issue.message for issue in issues)


def test_pvp_mov_container():
    """Test MOV container is supported."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 50_000_000,
    }
    issues = checker.check(video_info)

    assert any("MOV" in issue.message for issue in issues)


def test_pvp_timecode_support_gpu():
    """Test timecode support note for GPU codecs."""
    checker = ProVideoPlayerChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 40_000_000,
    }
    issues = checker.check(video_info)

    assert any("timecode" in issue.message.lower() for issue in issues)
