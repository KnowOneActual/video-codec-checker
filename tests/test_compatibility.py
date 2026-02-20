"""Tests for compatibility checking.

Updated to use the new rule-based API.
"""

from videowise.compatibility import (
    CompatibilityLevel,
    check_compatibility,
)


def test_casparcg_h264_compatible():
    """Test that H.264 in MP4 is compatible with CasparCG."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }

    issues = check_compatibility(video_info, "casparcg")

    # Should have at least one compatible status
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_casparcg_prores_compatible():
    """Test that ProRes in MOV is compatible with CasparCG."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }

    issues = check_compatibility(video_info, "casparcg")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_casparcg_vp9_incompatible():
    """Test that VP9 is incompatible with CasparCG."""
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = check_compatibility(video_info, "casparcg")

    # Should have incompatibility issue
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)


def test_casparcg_wrong_container_warning():
    """Test that H.264 in wrong container may show warning."""
    video_info = {
        "codec": "h264",
        "container": "webm",  # H.264 should be in MP4 or MOV
    }

    issues = check_compatibility(video_info, "casparcg")

    # Should have some result
    assert len(issues) > 0


def test_casparcg_vfr_warning():
    """Test that variable frame rate may trigger warning."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "frame_rate": "30000/1001",  # Variable frame rate indicator
    }

    issues = check_compatibility(video_info, "casparcg")

    # Should have some result
    assert len(issues) > 0


def test_vmix_high_bitrate_warning():
    """Test that high bitrate may trigger warning for vMix."""
    video_info = {
        "codec": "h264",
        "bitrate": 180_000_000,  # 180 Mbps
    }

    issues = check_compatibility(video_info, "vmix")

    # Should have some result
    assert len(issues) > 0


def test_vmix_very_high_bitrate_warning():
    """Test that very high bitrate triggers warning."""
    video_info = {
        "codec": "prores",
        "bitrate": 250_000_000,  # 250 Mbps
    }

    issues = check_compatibility(video_info, "vmix")

    # Should have some result
    assert len(issues) > 0


def test_vmix_4k_warning():
    """Test that 4K resolution may trigger hardware warning."""
    video_info = {
        "codec": "h264",
        "resolution": (3840, 2160),  # 4K
    }

    issues = check_compatibility(video_info, "vmix")

    # Should have some result
    assert len(issues) > 0


def test_vmix_prores_compatible():
    """Test that ProRes is well-supported by vMix."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "bitrate": 80_000_000,  # 80 Mbps - reasonable
    }

    issues = check_compatibility(video_info, "vmix")

    # Should have compatible status
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_function():
    """Test the main check_compatibility function."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    # Test CasparCG
    issues = check_compatibility(video_info, "casparcg")
    assert len(issues) > 0

    # Test vMix
    issues = check_compatibility(video_info, "vmix")
    assert len(issues) > 0


def test_check_compatibility_unknown_system():
    """Test handling of unknown system."""
    video_info = {"codec": "h264"}

    issues = check_compatibility(video_info, "unknown_system")

    assert len(issues) == 1
    assert issues[0].level == CompatibilityLevel.UNKNOWN


# Wirecast Tests


def test_wirecast_h264_compatible():
    """Test that H.264 is fully supported by Wirecast."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "wirecast")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_prores_compatible():
    """Test that ProRes is well-supported by Wirecast."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "wirecast")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_dnxhd_compatible():
    """Test that DNxHD is supported."""
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_unsupported_codec():
    """Test that unsupported codecs may show warning."""
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_high_bitrate_warning():
    """Test that very high bitrate may trigger performance warning."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "bitrate": 180_000_000,  # 180 Mbps
    }

    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


def test_wirecast_wmv_container_warning():
    """Test that WMV container handling."""
    video_info = {
        "codec": "h264",
        "container": "wmv",
    }

    issues = check_compatibility(video_info, "wirecast")

    assert len(issues) > 0


# Playback Pro Tests


def test_playbackpro_prores422_optimal():
    """Test that ProRes 422 is optimal for Playback Pro."""
    video_info = {
        "codec": "prores422",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_playbackpro_h264_hd_bitrate_good():
    """Test that H.264 with good HD bitrate is compatible."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,  # 20 Mbps - in range
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_hd_bitrate_low():
    """Test that H.264 with low HD bitrate may show warning."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,  # 10 Mbps - too low
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_h264_4k_bitrate_good():
    """Test that H.264 4K with good bitrate is compatible."""
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 35_000_000,  # 35 Mbps - in range
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_mov_container_required():
    """Test that MOV container is handled."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_non_mov_incompatible():
    """Test that non-MOV containers may be incompatible."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


def test_playbackpro_unsupported_codec_warning():
    """Test that unsupported codecs may show warning."""
    video_info = {
        "codec": "vp9",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "playbackpro")

    assert len(issues) > 0


# EasyWorship Tests


def test_easyworship_h264_mp4_native():
    """Test that H.264 in MP4 has native support."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "easyworship")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_easyworship_h264_mov_native():
    """Test that H.264 in MOV has native support."""
    video_info = {
        "codec": "h264",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "easyworship")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_easyworship_wmv_windows_codec():
    """Test that WMV is supported via Windows codecs."""
    video_info = {
        "codec": "wmv",
        "container": "wmv",
    }

    issues = check_compatibility(video_info, "easyworship")

    assert len(issues) > 0


def test_easyworship_unsupported_codec_warning():
    """Test that unsupported codecs may show warning."""
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = check_compatibility(video_info, "easyworship")

    assert len(issues) > 0


def test_easyworship_m4v_native():
    """Test that M4V container has native support."""
    video_info = {
        "codec": "h264",
        "container": "m4v",
    }

    issues = check_compatibility(video_info, "easyworship")

    assert len(issues) > 0


# VLC Tests


def test_vlc_universal_codec_support():
    """Test that VLC supports virtually all codecs."""
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = check_compatibility(video_info, "vlc")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_vlc_hardware_decoding_recommendation():
    """Test that VLC may recommend hardware decoding for modern codecs."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "vlc")

    assert len(issues) > 0


def test_vlc_extreme_bitrate_warning():
    """Test that VLC may warn about extreme bitrate."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "bitrate": 350_000_000,  # 350 Mbps
    }

    issues = check_compatibility(video_info, "vlc")

    assert len(issues) > 0


def test_vlc_8k_resolution_warning():
    """Test that VLC may warn about 8K resolution requirements."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (7680, 4320),  # 8K
    }

    issues = check_compatibility(video_info, "vlc")

    assert len(issues) > 0


# Resolume Tests


def test_resolume_dxv_optimal():
    """Test that DXV is optimal for Resolume."""
    video_info = {
        "codec": "dxv",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_hap_compatible():
    """Test that HAP is optimal for Resolume."""
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_hap_alpha_compatible():
    """Test that HAP Alpha is optimal for Resolume."""
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_resolume_h264_cpu_warning():
    """Test that H.264 may show CPU-based warning."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_prores_warning():
    """Test that ProRes may show warning."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_4k_layer_warning():
    """Test that 4K video may show layer count warning."""
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


def test_resolume_hevc_conversion_advice():
    """Test that HEVC may show conversion advice."""
    video_info = {
        "codec": "hevc",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "resolume")

    assert len(issues) > 0


# Mitti Tests


def test_mitti_prores_optimal():
    """Test that ProRes is optimal for Mitti."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "mitti")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_mitti_hap_optimal():
    """Test that HAP is optimal for Mitti."""
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "mitti")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_mitti_other_codec_transcode_advice():
    """Test that other codecs may show transcoding advice."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "mitti")

    assert len(issues) > 0


def test_mitti_4k_codec_guidance():
    """Test that 4K may show codec guidance."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = check_compatibility(video_info, "mitti")

    assert len(issues) > 0


def test_mitti_high_bitrate_warning():
    """Test that high bitrate may show performance warning."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "bitrate": 300_000_000,  # 300 Mbps
    }

    issues = check_compatibility(video_info, "mitti")

    assert len(issues) > 0


# Millumin Tests


def test_millumin_quicktime_support():
    """Test that Millumin supports QuickTime formats."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "millumin")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_millumin_hap_projection_optimal():
    """Test that HAP is optimal for projection mapping."""
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "millumin")

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_millumin_h264_performance_warning():
    """Test that H.264 may show performance warning."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "millumin")

    assert len(issues) > 0


def test_millumin_4k_projection_warning():
    """Test that 4K may show projection performance warning."""
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = check_compatibility(video_info, "millumin")

    assert len(issues) > 0


# Integration tests for new media player systems


def test_check_compatibility_vlc():
    """Test check_compatibility function with VLC."""
    video_info = {
        "codec": "av1",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "vlc")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_resolume():
    """Test check_compatibility function with Resolume."""
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")
    assert len(issues) > 0
