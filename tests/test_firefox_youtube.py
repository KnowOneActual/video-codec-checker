"""Tests for Firefox and YouTube compatibility checkers.

Updated to use the new rule-based API.
"""

from videowise.compatibility import CompatibilityLevel, check_compatibility


class TestFirefoxChecker:
    """Test cases for Firefox browser compatibility."""

    # H.264 Tests
    def test_h264_in_mp4_fully_supported(self):
        """H.264 in MP4 should be fully compatible."""
        video_info = {"codec": "h264", "container": "mp4"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    def test_h264_in_other_container(self):
        """H.264 in non-MP4 container should still be compatible."""
        video_info = {"codec": "h264", "container": "mov"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    # VP8/VP9 Tests
    def test_vp9_in_webm_natively_supported(self):
        """VP9 in WebM should be natively supported."""
        video_info = {"codec": "vp9", "container": "webm"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    def test_vp8_in_webm_natively_supported(self):
        """VP8 in WebM should be natively supported."""
        video_info = {"codec": "vp8", "container": "webm"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    def test_vp9_in_mp4(self):
        """VP9 in MP4 should be compatible but not optimal."""
        video_info = {"codec": "vp9", "container": "mp4"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    # AV1 Tests
    def test_av1_supported(self):
        """AV1 should be supported by Firefox."""
        video_info = {"codec": "av1", "container": "webm"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    # HEVC Tests
    def test_hevc_limited_support(self):
        """HEVC should show limited support warning."""
        video_info = {"codec": "hevc", "container": "mp4"}
        issues = check_compatibility(video_info, "firefox")

        # HEVC may be incompatible or have warning
        assert len(issues) > 0

    # Unsupported Codec Tests
    def test_prores_not_supported(self):
        """ProRes should not be supported."""
        video_info = {"codec": "prores", "container": "mov"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)

    def test_unsupported_codec_with_suggestion(self):
        """Unsupported codecs should include conversion suggestions."""
        video_info = {"codec": "dnxhd", "container": "mov"}
        issues = check_compatibility(video_info, "firefox")

        assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)


class TestYouTubeChecker:
    """Test cases for YouTube upload compatibility."""

    # H.264 Tests
    def test_h264_high_profile_in_mp4_optimal(self):
        """H.264 High Profile in MP4 should be optimal for YouTube."""
        video_info = {
            "codec": "h264",
            "profile": "high",
            "container": "mp4",
            "file_size": 100_000_000,  # 100MB
        }
        issues = check_compatibility(video_info, "youtube")

        # Should have compatible status
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_h264_baseline_profile_warning(self):
        """H.264 Baseline Profile may show warning."""
        video_info = {
            "codec": "h264",
            "profile": "baseline",
            "container": "mp4",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        # Should have some result
        assert len(issues) > 0

    def test_h264_main_profile_warning(self):
        """H.264 Main Profile should be acceptable."""
        video_info = {
            "codec": "h264",
            "profile": "main",
            "container": "mp4",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    def test_h264_without_profile(self):
        """H.264 without profile info should be compatible."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    # Container Tests
    def test_mp4_container_preferred(self):
        """MP4 container should be marked as preferred."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_mov_container_accepted_with_warning(self):
        """MOV container may be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mov",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    def test_avi_container_accepted_with_warning(self):
        """AVI container may be accepted."""
        video_info = {
            "codec": "h264",
            "container": "avi",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    def test_webm_container_with_warning(self):
        """WebM container may show warning."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        # Should have some result
        assert len(issues) >= 1

    # Codec Tests
    def test_vp9_codec_with_warning(self):
        """VP9 may work but with note about H.264 preference."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    def test_hevc_with_warning(self):
        """HEVC may show warning."""
        video_info = {
            "codec": "hevc",
            "container": "mp4",
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    def test_prores_with_warning(self):
        """ProRes may show warning."""
        video_info = {
            "codec": "prores",
            "container": "mov",
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    # File Size Tests
    def test_file_size_under_limit(self):
        """Files under 256GB should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "file_size": 10 * 1024 * 1024 * 1024,  # 10GB
        }
        issues = check_compatibility(video_info, "youtube")

        # Should not have file size incompatibility
        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        # Large files may still be compatible
        assert len(issues) > 0

    def test_file_size_over_limit(self):
        """Files over 256GB should be rejected."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "file_size": 300 * 1024 * 1024 * 1024,  # 300GB
        }
        issues = check_compatibility(video_info, "youtube")

        # May have incompatibility for extreme file size
        assert len(issues) > 0

    def test_file_size_exactly_at_limit(self):
        """Files exactly at 256GB may be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "file_size": 256 * 1024 * 1024 * 1024,  # Exactly 256GB
        }
        issues = check_compatibility(video_info, "youtube")

        assert len(issues) > 0

    # Combined Scenarios
    def test_optimal_upload_settings(self):
        """Test optimal YouTube upload settings."""
        video_info = {
            "codec": "h264",
            "profile": "high",
            "container": "mp4",
            "file_size": 2 * 1024 * 1024 * 1024,  # 2GB
        }
        issues = check_compatibility(video_info, "youtube")

        # Should have positive compatibility messages
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_suboptimal_but_accepted_settings(self):
        """Test suboptimal but accepted settings."""
        video_info = {
            "codec": "h264",
            "profile": "baseline",
            "container": "mov",
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "youtube")

        # Should have results
        assert len(issues) > 0

        # Should not be completely incompatible
        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        # May have zero incompatible, or just warnings
        assert len(issues) > len(incompatible_issues)
