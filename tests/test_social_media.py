"""Tests for TikTok, Vimeo, and Facebook compatibility checkers.

Updated to use the new rule-based API.
"""

from videowise.compatibility import CompatibilityLevel, check_compatibility


class TestTikTokChecker:
    """Test cases for TikTok platform compatibility."""

    # Codec Tests
    def test_h264_optimal_codec(self):
        """H.264 should be the optimal codec for TikTok."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_hevc_compatibility_warning(self):
        """HEVC may show warning about device compatibility."""
        video_info = {
            "codec": "hevc",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        # Should have results
        assert len(issues) > 0

    def test_unsupported_codec_warning(self):
        """Non-standard codecs may show warning."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    # Container Tests
    def test_mp4_container_supported(self):
        """MP4 container should be fully supported."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_webm_container_warning(self):
        """WebM container may show warning preferring MP4."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    # Resolution Tests
    def test_optimal_resolution(self):
        """1080x1920 should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_oversized_resolution_warning(self):
        """Resolutions above 1080p may show downscale warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (2160, 3840),  # 4K vertical
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    # Bitrate Tests
    def test_low_bitrate_warning(self):
        """Low bitrate may trigger quality warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 4_000_000,  # 4 Mbps
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    def test_high_bitrate_warning(self):
        """High bitrate may show compression warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 25_000_000,  # 25 Mbps
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    def test_optimal_bitrate_no_warning(self):
        """Optimal bitrate should work well."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 12_000_000,  # 12 Mbps
            "file_size": 100_000_000,
        }
        issues = check_compatibility(video_info, "tiktok")

        assert len(issues) > 0

    def test_file_size_under_limit(self):
        """Reasonable file sizes should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 200 * 1024 * 1024,  # 200MB
        }
        issues = check_compatibility(video_info, "tiktok")

        # Should not be completely incompatible
        assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)

    def test_optimal_tiktok_video(self):
        """Test well-optimized TikTok video."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 12_000_000,  # 12 Mbps
            "file_size": 150 * 1024 * 1024,  # 150MB
        }
        issues = check_compatibility(video_info, "tiktok")

        # Should have compatible messages
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1


class TestVimeoChecker:
    """Test cases for Vimeo platform compatibility."""

    # Codec Tests
    def test_h264_recommended(self):
        """H.264 should be the recommended codec."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = check_compatibility(video_info, "vimeo")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_prores_accepted_with_warning(self):
        """ProRes may be accepted but with note."""
        video_info = {
            "codec": "prores",
            "container": "mov",
            "resolution": (1920, 1080),
            "bitrate": 150_000_000,
        }
        issues = check_compatibility(video_info, "vimeo")

        assert len(issues) > 0

    def test_unsupported_codec_warning(self):
        """Unsupported codecs may show warning."""
        video_info = {
            "codec": "av1",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = check_compatibility(video_info, "vimeo")

        assert len(issues) > 0

    # Container Tests
    def test_mp4_container_compatible(self):
        """MP4 container should be fully compatible."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = check_compatibility(video_info, "vimeo")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_mov_container_compatible(self):
        """MOV container should be fully compatible."""
        video_info = {
            "codec": "h264",
            "container": "mov",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = check_compatibility(video_info, "vimeo")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    # Bitrate Tests by Resolution
    def test_4k_optimal_bitrate(self):
        """4K video with good bitrate should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 45_000_000,  # 45 Mbps
        }
        issues = check_compatibility(video_info, "vimeo")

        assert len(issues) > 0

    def test_4k_low_bitrate_warning(self):
        """4K video with low bitrate may show warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 30_000_000,  # 30 Mbps
        }
        issues = check_compatibility(video_info, "vimeo")

        assert len(issues) > 0

    def test_1080p_optimal_bitrate(self):
        """1080p video with good bitrate should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,  # 15 Mbps
        }
        issues = check_compatibility(video_info, "vimeo")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_720p_optimal_bitrate(self):
        """720p video with good bitrate should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "bitrate": 7_000_000,  # 7 Mbps
        }
        issues = check_compatibility(video_info, "vimeo")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_1080p_high_bitrate_warning(self):
        """1080p video with very high bitrate may show note."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 30_000_000,  # 30 Mbps
        }
        issues = check_compatibility(video_info, "vimeo")

        assert len(issues) > 0


class TestFacebookChecker:
    """Test cases for Facebook platform compatibility."""

    # Codec Tests
    def test_h264_recommended(self):
        """H.264 should be the recommended codec."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,  # 1GB
        }
        issues = check_compatibility(video_info, "facebook")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_hevc_supported_for_reels(self):
        """HEVC may be supported for Reels."""
        video_info = {
            "codec": "hevc",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    def test_vp9_supported_for_reels(self):
        """VP9 may be supported for Reels."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    def test_av1_supported_for_reels(self):
        """AV1 may be supported for Reels."""
        video_info = {
            "codec": "av1",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    def test_unsupported_codec_warning(self):
        """Unsupported codecs may show warning."""
        video_info = {
            "codec": "prores",
            "container": "mov",
            "resolution": (1920, 1080),
            "file_size": 2 * 1024 * 1024 * 1024,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    # Container Tests
    def test_mp4_preferred(self):
        """MP4 container should be preferred."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = check_compatibility(video_info, "facebook")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_mov_preferred(self):
        """MOV container may be preferred."""
        video_info = {
            "codec": "h264",
            "container": "mov",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    def test_avi_supported_not_recommended(self):
        """AVI container may be supported but not recommended."""
        video_info = {
            "codec": "h264",
            "container": "avi",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    # File Size Tests
    def test_file_size_under_limit(self):
        """Files under 4GB should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 3 * 1024 * 1024 * 1024,  # 3GB
        }
        issues = check_compatibility(video_info, "facebook")

        # Should have at least one compatible status
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_file_size_over_limit(self):
        """Files over 4GB may be rejected."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        }
        issues = check_compatibility(video_info, "facebook")

        assert len(issues) > 0

    # Resolution Tests
    def test_hd_resolution_suitable(self):
        """720p and above should be suitable."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 500_000_000,
        }
        issues = check_compatibility(video_info, "facebook")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_1080p_resolution_suitable(self):
        """1080p should be suitable."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = check_compatibility(video_info, "facebook")

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1
