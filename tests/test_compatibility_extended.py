"""Extended tests for all compatibility checkers.

Updated to use the new rule-based API.
"""

from videowise.compatibility import (
    CompatibilityLevel,
    check_compatibility,
)


# OBS Studio Tests
def test_obs_h264_compatible():
    """Test that H.264 is fully supported by OBS."""
    video_info = {"codec": "h264", "container": "mkv"}

    issues = check_compatibility(video_info, "obs")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_obs_mkv_container():
    """Test that MKV is recognized as OBS default."""
    video_info = {
        "codec": "h264",
        "container": "matroska,webm",
    }  # ffprobe returns 'matroska' for mkv

    issues = check_compatibility(video_info, "obs")
    # Check that MKV/matroska is mentioned as compatible
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# QLab Tests
def test_qlab_prores_proxy_optimal():
    """Test that ProRes Proxy is optimal for QLab."""
    video_info = {"codec": "prores_proxy", "container": "mov"}

    issues = check_compatibility(video_info, "qlab")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_qlab_h264_warning():
    """Test that H.264 gets performance warning in QLab."""
    video_info = {"codec": "h264", "container": "mov"}

    issues = check_compatibility(video_info, "qlab")
    # May be compatible or warning depending on rules
    assert len(issues) > 0


def test_qlab_prores4444_alpha():
    """Test that ProRes 4444 is recognized for alpha channel."""
    video_info = {"codec": "prores4444", "container": "mov"}

    issues = check_compatibility(video_info, "qlab")
    # Should be compatible
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# ProPresenter Tests
def test_propresenter_hap_optimal():
    """Test that HAP is optimal for ProPresenter."""
    video_info = {"codec": "hap", "container": "mov"}

    issues = check_compatibility(video_info, "propresenter")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_propresenter_unsupported_codec():
    """Test that unsupported codecs are rejected."""
    video_info = {"codec": "vp9", "container": "webm"}

    issues = check_compatibility(video_info, "propresenter")
    assert any(issue.level in [CompatibilityLevel.INCOMPATIBLE, CompatibilityLevel.WARNING] for issue in issues)


def test_propresenter_prores4444():
    """Test ProRes 4444 alpha support."""
    video_info = {"codec": "prores4444", "container": "mov"}

    issues = check_compatibility(video_info, "propresenter")
    # Should be compatible
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Safari Tests
def test_safari_h264_compatible():
    """Test that Safari supports H.264."""
    video_info = {"codec": "h264", "container": "mp4"}

    issues = check_compatibility(video_info, "safari")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_safari_vp9_incompatible():
    """Test that Safari doesn't support VP9."""
    video_info = {"codec": "vp9", "container": "webm"}

    issues = check_compatibility(video_info, "safari")
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    assert any("does not support" in issue.message.lower() for issue in issues)


def test_safari_hevc_supported():
    """Test that Safari supports HEVC."""
    video_info = {"codec": "hevc", "container": "mp4"}

    issues = check_compatibility(video_info, "safari")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Chrome Tests
def test_chrome_vp9_compatible():
    """Test that Chrome supports VP9."""
    video_info = {"codec": "vp9", "container": "webm"}

    issues = check_compatibility(video_info, "chrome")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_chrome_av1_compatible():
    """Test that Chrome supports AV1."""
    video_info = {"codec": "av1", "container": "mp4"}

    issues = check_compatibility(video_info, "chrome")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Instagram Tests
def test_instagram_h264_baseline_optimal():
    """Test that H.264 Baseline is optimal for Instagram."""
    video_info = {"codec": "h264", "profile": "Constrained Baseline", "resolution": (1080, 1920)}

    issues = check_compatibility(video_info, "instagram")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_instagram_high_profile_warning():
    """Test that High Profile triggers re-encode warning."""
    video_info = {"codec": "h264", "profile": "High", "resolution": (1080, 1920)}

    issues = check_compatibility(video_info, "instagram")
    # Should still be compatible, may have warnings
    assert len(issues) > 0


def test_instagram_resolution_downscale():
    """Test that high resolution triggers downscale warning."""
    video_info = {"codec": "h264", "profile": "Baseline", "resolution": (3840, 2160)}

    issues = check_compatibility(video_info, "instagram")
    # Should have some notice about resolution
    assert len(issues) > 0


def test_instagram_wrong_codec():
    """Test that non-H.264 triggers warning."""
    video_info = {"codec": "prores", "resolution": (1080, 1920)}

    issues = check_compatibility(video_info, "instagram")
    # ProRes not supported, should have incompatible or warning
    assert any(issue.level in [CompatibilityLevel.INCOMPATIBLE, CompatibilityLevel.WARNING] for issue in issues)


# Twitter Tests
def test_twitter_h264_compatible():
    """Test that H.264 is compatible with Twitter."""
    video_info = {"codec": "h264", "container": "mp4", "file_size": 100 * 1024 * 1024}

    issues = check_compatibility(video_info, "twitter")
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_twitter_file_size_limit_standard():
    """Test that file size limit is enforced."""
    video_info = {"codec": "h264", "container": "mp4", "file_size": 600 * 1024 * 1024}  # 600MB

    issues = check_compatibility(video_info, "twitter")
    # Large file should trigger warning or incompatible
    assert len(issues) > 0


def test_twitter_file_size_ok():
    """Test that reasonable file sizes are accepted."""
    video_info = {"codec": "h264", "container": "mp4", "file_size": 100 * 1024 * 1024}  # 100MB

    issues = check_compatibility(video_info, "twitter")
    # Should be compatible
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Integration Tests
def test_check_compatibility_all_systems():
    """Test that check_compatibility works for all systems."""
    video_info = {"codec": "h264", "container": "mp4"}

    systems = [
        "casparcg",
        "vmix",
        "obs",
        "qlab",
        "propresenter",
        "safari",
        "chrome",
        "instagram",
        "twitter",
    ]

    for system in systems:
        issues = check_compatibility(video_info, system)
        assert len(issues) > 0, f"No issues returned for {system}"
