"""Tests for compatibility checking."""

from videowise.compatibility import (
    CasparCGChecker,
    CompatibilityLevel,
    EasyWorshipChecker,
    MilluminChecker,
    MittiChecker,
    PlaybackProChecker,
    ResolumeChecker,
    VLCChecker,
    VmixChecker,
    WirecastChecker,
    check_compatibility,
)


def test_casparcg_h264_compatible():
    """Test that H.264 in MP4 is compatible with CasparCG."""
    checker = CasparCGChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "resolution": (1920, 1080),
    }

    issues = checker.check(video_info)

    # Should have at least one compatible status
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_casparcg_prores_compatible():
    """Test that ProRes in MOV is compatible with CasparCG."""
    checker = CasparCGChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (1920, 1080),
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_casparcg_vp9_incompatible():
    """Test that VP9 is incompatible with CasparCG."""
    checker = CasparCGChecker()
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = checker.check(video_info)

    # Should have incompatibility issue
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    # Should mention the codec is not supported
    assert any("does not support" in issue.message.lower() for issue in issues)
    # Should have a suggestion
    assert any(issue.suggestion is not None for issue in issues)


def test_casparcg_wrong_container_warning():
    """Test that H.264 in wrong container shows warning."""
    checker = CasparCGChecker()
    video_info = {
        "codec": "h264",
        "container": "webm",  # H.264 should be in MP4 or MOV
    }

    issues = checker.check(video_info)

    # Should have warning about container
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)


def test_casparcg_vfr_warning():
    """Test that variable frame rate triggers warning."""
    checker = CasparCGChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "frame_rate": "30000/1001",  # Variable frame rate indicator
    }

    issues = checker.check(video_info)

    # Should have warning about frame rate
    assert any("frame rate" in issue.message.lower() for issue in issues)


def test_vmix_high_bitrate_warning():
    """Test that high bitrate triggers warning for vMix."""
    checker = VmixChecker()
    video_info = {
        "codec": "h264",
        "bitrate": 180_000_000,  # 180 Mbps
    }

    issues = checker.check(video_info)

    # Should have warning about high bitrate
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


def test_vmix_very_high_bitrate_warning():
    """Test that very high bitrate triggers stronger warning."""
    checker = VmixChecker()
    video_info = {
        "codec": "prores",
        "bitrate": 250_000_000,  # 250 Mbps
    }

    issues = checker.check(video_info)

    # Should have warning
    assert any(
        "very high bitrate" in issue.message.lower() or "dropped frames" in issue.message.lower()
        for issue in issues
    )


def test_vmix_4k_warning():
    """Test that 4K resolution triggers hardware warning."""
    checker = VmixChecker()
    video_info = {
        "codec": "h264",
        "resolution": (3840, 2160),  # 4K
    }

    issues = checker.check(video_info)

    # Should have warning about 4K
    assert any("4k" in issue.message.lower() for issue in issues)


def test_vmix_prores_compatible():
    """Test that ProRes is well-supported by vMix."""
    checker = VmixChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "bitrate": 80_000_000,  # 80 Mbps - reasonable
    }

    issues = checker.check(video_info)

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
    assert "unknown system" in issues[0].message.lower()


# Wirecast Tests


def test_wirecast_h264_compatible():
    """Test that H.264 is fully supported by Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("hardware acceleration" in issue.reason.lower() for issue in issues if issue.reason)


def test_wirecast_prores_compatible():
    """Test that ProRes is well-supported by Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("professional" in issue.reason.lower() for issue in issues if issue.reason)


def test_wirecast_dnxhd_compatible():
    """Test that DNxHD is supported by Wirecast."""
    checker = WirecastChecker()
    video_info = {
        "codec": "dnxhd",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_wirecast_unsupported_codec():
    """Test that unsupported codecs show warning."""
    checker = WirecastChecker()
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("may not be supported" in issue.message.lower() for issue in issues)


def test_wirecast_high_bitrate_warning():
    """Test that very high bitrate triggers performance warning."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "bitrate": 180_000_000,  # 180 Mbps
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


def test_wirecast_wmv_container_warning():
    """Test that WMV container shows preference for MP4/MOV."""
    checker = WirecastChecker()
    video_info = {
        "codec": "h264",
        "container": "wmv",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("mp4/mov preferred" in issue.message.lower() for issue in issues)


# Playback Pro Tests


def test_playbackpro_prores422_optimal():
    """Test that ProRes 422 is optimal for Playback Pro."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "prores422",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any(
        "recommended" in issue.message.lower() or "optimal" in issue.message.lower()
        for issue in issues
    )


def test_playbackpro_h264_hd_bitrate_good():
    """Test that H.264 with good HD bitrate is compatible."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 20_000_000,  # 20 Mbps - in range
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any(
        "suitable" in issue.message.lower() or "within recommended" in issue.message.lower()
        for issue in issues
    )


def test_playbackpro_h264_hd_bitrate_low():
    """Test that H.264 with low HD bitrate shows warning."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (1920, 1080),
        "bitrate": 10_000_000,  # 10 Mbps - too low
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("outside recommended range" in issue.message.lower() for issue in issues)


def test_playbackpro_h264_4k_bitrate_good():
    """Test that H.264 4K with good bitrate is compatible."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
        "resolution": (3840, 2160),
        "bitrate": 35_000_000,  # 35 Mbps - in range
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_playbackpro_mov_container_required():
    """Test that MOV container is required by Playback Pro."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = checker.check(video_info)

    # Should have compatible message about MOV
    assert any("mov container is required" in issue.message.lower() for issue in issues)


def test_playbackpro_non_mov_incompatible():
    """Test that non-MOV containers are incompatible."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    assert any("requires mov" in issue.message.lower() for issue in issues)


def test_playbackpro_unsupported_codec_warning():
    """Test that unsupported codecs show warning."""
    checker = PlaybackProChecker()
    video_info = {
        "codec": "vp9",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("may not be optimal" in issue.message.lower() for issue in issues)


# EasyWorship Tests


def test_easyworship_h264_mp4_native():
    """Test that H.264 in MP4 has native support."""
    checker = EasyWorshipChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("native support" in issue.message.lower() for issue in issues)


def test_easyworship_h264_mov_native():
    """Test that H.264 in MOV has native support."""
    checker = EasyWorshipChecker()
    video_info = {
        "codec": "h264",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_easyworship_wmv_windows_codec():
    """Test that WMV is supported via Windows codecs."""
    checker = EasyWorshipChecker()
    video_info = {
        "codec": "wmv",
        "container": "wmv",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("windows" in issue.message.lower() for issue in issues)


def test_easyworship_unsupported_codec_warning():
    """Test that unsupported codecs show warning."""
    checker = EasyWorshipChecker()
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("may require additional codecs" in issue.message.lower() for issue in issues)


def test_easyworship_m4v_native():
    """Test that M4V container has native support."""
    checker = EasyWorshipChecker()
    video_info = {
        "codec": "h264",
        "container": "m4v",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("native support" in issue.message.lower() for issue in issues)


# VLC Tests


def test_vlc_universal_codec_support():
    """Test that VLC supports virtually all codecs."""
    checker = VLCChecker()
    video_info = {
        "codec": "vp9",
        "container": "webm",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("supported by vlc" in issue.message.lower() for issue in issues)
    assert any("ffmpeg" in issue.reason.lower() for issue in issues if issue.reason)


def test_vlc_hardware_decoding_recommendation():
    """Test that VLC recommends hardware decoding for modern codecs."""
    checker = VLCChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any("hardware acceleration" in issue.message.lower() for issue in issues)


def test_vlc_extreme_bitrate_warning():
    """Test that VLC warns about extreme bitrate."""
    checker = VLCChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
        "bitrate": 350_000_000,  # 350 Mbps
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("very high bitrate" in issue.message.lower() for issue in issues)


def test_vlc_8k_resolution_warning():
    """Test that VLC warns about 8K resolution requirements."""
    checker = VLCChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
        "resolution": (7680, 4320),  # 8K
    }

    issues = checker.check(video_info)

    assert any("8k" in issue.message.lower() for issue in issues)
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)


# Resolume Tests


def test_resolume_dxv_optimal():
    """Test that DXV is optimal for Resolume."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "dxv",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("optimal" in issue.message.lower() for issue in issues)
    assert any("gpu" in issue.reason.lower() for issue in issues if issue.reason)


def test_resolume_hap_compatible():
    """Test that HAP is optimal for Resolume."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("optimal" in issue.message.lower() for issue in issues)


def test_resolume_hap_alpha_compatible():
    """Test that HAP Alpha is optimal for Resolume."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap_alpha",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("alpha" in issue.message.lower() for issue in issues)


def test_resolume_h264_cpu_warning():
    """Test that H.264 shows CPU-based warning."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("cpu" in issue.message.lower() for issue in issues)
    assert any("dxv or hap" in issue.suggestion.lower() for issue in issues if issue.suggestion)


def test_resolume_prores_mac_warning():
    """Test that ProRes shows platform-specific warning on Mac."""
    checker = ResolumeChecker(platform="mac")
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("cpu-based" in issue.message.lower() for issue in issues)


def test_resolume_4k_layer_warning():
    """Test that 4K video shows layer count warning."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = checker.check(video_info)

    assert any("layer" in issue.message.lower() for issue in issues)


def test_resolume_hevc_conversion_advice():
    """Test that HEVC shows conversion advice."""
    checker = ResolumeChecker()
    video_info = {
        "codec": "hevc",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("convert" in issue.suggestion.lower() for issue in issues if issue.suggestion)


# Mitti Tests


def test_mitti_prores_optimal():
    """Test that ProRes is optimal for Mitti."""
    checker = MittiChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("optimal" in issue.message.lower() for issue in issues)
    assert any("apple silicon" in issue.reason.lower() for issue in issues if issue.reason)


def test_mitti_hap_optimal():
    """Test that HAP is optimal for Mitti."""
    checker = MittiChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any("optimal" in issue.message.lower() for issue in issues)


def test_mitti_other_codec_transcode_advice():
    """Test that other codecs show transcoding advice."""
    checker = MittiChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("transcode" in issue.message.lower() for issue in issues)


def test_mitti_4k_codec_guidance():
    """Test that 4K shows codec guidance."""
    checker = MittiChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = checker.check(video_info)

    assert any("4k" in issue.message.lower() for issue in issues)
    assert any(
        "hap" in issue.message.lower() or "prores" in issue.message.lower() for issue in issues
    )


def test_mitti_high_bitrate_warning():
    """Test that high bitrate shows performance warning."""
    checker = MittiChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "bitrate": 300_000_000,  # 300 Mbps
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("bitrate" in issue.message.lower() for issue in issues)


# Millumin Tests


def test_millumin_quicktime_support():
    """Test that Millumin supports QuickTime formats."""
    checker = MilluminChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any(
        "quicktime" in issue.reason.lower() or "avfoundation" in issue.reason.lower()
        for issue in issues
        if issue.reason
    )


def test_millumin_hap_projection_optimal():
    """Test that HAP is optimal for projection mapping."""
    checker = MilluminChecker()
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = checker.check(video_info)

    assert any("projection" in issue.message.lower() for issue in issues)
    assert any("gpu" in issue.reason.lower() for issue in issues if issue.reason)


def test_millumin_h264_performance_warning():
    """Test that H.264 shows performance warning."""
    checker = MilluminChecker()
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = checker.check(video_info)

    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any("prores/hap recommended" in issue.message.lower() for issue in issues)


def test_millumin_4k_projection_warning():
    """Test that 4K shows projection performance warning."""
    checker = MilluminChecker()
    video_info = {
        "codec": "prores",
        "container": "mov",
        "resolution": (3840, 2160),  # 4K
    }

    issues = checker.check(video_info)

    assert any("4k" in issue.message.lower() for issue in issues)
    assert any("projection" in issue.message.lower() for issue in issues)


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
        "codec": "dxv",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "resolume")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_mitti():
    """Test check_compatibility function with Mitti."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "mitti")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_millumin():
    """Test check_compatibility function with Millumin."""
    video_info = {
        "codec": "hap",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "millumin")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Integration tests for previous systems


def test_check_compatibility_wirecast():
    """Test check_compatibility function with Wirecast."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "wirecast")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_playbackpro():
    """Test check_compatibility function with Playback Pro."""
    video_info = {
        "codec": "prores",
        "container": "mov",
    }

    issues = check_compatibility(video_info, "playbackpro")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_check_compatibility_easyworship():
    """Test check_compatibility function with EasyWorship."""
    video_info = {
        "codec": "h264",
        "container": "mp4",
    }

    issues = check_compatibility(video_info, "easyworship")
    assert len(issues) > 0
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
