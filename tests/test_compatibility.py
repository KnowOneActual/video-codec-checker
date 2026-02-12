"""Tests for compatibility checking."""

from videowise.compatibility import (
    CasparCGChecker,
    CompatibilityLevel,
    VmixChecker,
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
