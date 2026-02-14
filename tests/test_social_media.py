"""Tests for TikTok, Vimeo, and Facebook compatibility checkers."""

import pytest

from videowise.compatibility import (
    CompatibilityLevel,
    TikTokChecker,
    VimeoChecker,
    FacebookChecker,
)


class TestTikTokChecker:
    """Test cases for TikTok platform compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mobile_checker = TikTokChecker(upload_source="mobile")
        self.desktop_checker = TikTokChecker(upload_source="desktop")

    # Codec Tests
    def test_h264_optimal_codec(self):
        """H.264 should be the optimal codec for TikTok."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 2  # Codec + Container
        assert any("optimal" in i.message.lower() for i in compatible_issues)

    def test_hevc_compatibility_warning(self):
        """HEVC should show warning about device compatibility."""
        video_info = {
            "codec": "hevc",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warning_issues) >= 1
        assert any("playback issues" in i.message for i in warning_issues)
        assert any("iOS" in i.reason for i in warning_issues)

    def test_unsupported_codec_warning(self):
        """Non-standard codecs should show warning."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warning_issues) >= 1
        assert any("recommends H.264" in i.message for i in warning_issues)

    # Container Tests
    def test_mp4_container_supported(self):
        """MP4 container should be fully supported."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MP4" in i.message for i in compatible_issues)

    def test_webm_container_warning(self):
        """WebM container should show warning preferring MP4."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("MP4 is preferred" in i.message for i in warning_issues)

    # Resolution Tests
    def test_optimal_resolution(self):
        """1080x1920 should be marked as optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("1080x1920" in i.message for i in compatible_issues)
        assert any("9:16" in i.reason for i in compatible_issues)

    def test_oversized_resolution_warning(self):
        """Resolutions above 1080p should show downscale warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (2160, 3840),  # 4K vertical
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("downscaled" in i.message for i in warning_issues)

    # Bitrate Tests
    def test_low_bitrate_warning(self):
        """Bitrate below 5 Mbps should trigger quality warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 4_000_000,  # 4 Mbps
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("quality downgrade" in i.message for i in warning_issues)

    def test_high_bitrate_warning(self):
        """Bitrate above 20 Mbps should show compression warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 25_000_000,  # 25 Mbps
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("compressed" in i.message or "flattens" in i.reason for i in warning_issues)

    def test_optimal_bitrate_no_warning(self):
        """Bitrate within 8-15 Mbps should have no bitrate warnings."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 12_000_000,  # 12 Mbps
            "file_size": 100_000_000,
        }
        issues = self.mobile_checker.check(video_info)

        bitrate_warnings = [
            i
            for i in issues
            if i.level == CompatibilityLevel.WARNING and "bitrate" in i.message.lower()
        ]
        assert len(bitrate_warnings) == 0

    # File Size Tests - Mobile
    def test_mobile_file_size_under_limit(self):
        """Mobile uploads under 287MB should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 200 * 1024 * 1024,  # 200MB
        }
        issues = self.mobile_checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 0

    def test_mobile_file_size_over_limit(self):
        """Mobile uploads over 287MB should be rejected."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 300 * 1024 * 1024,  # 300MB
        }
        issues = self.mobile_checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 1
        assert "287MB" in incompatible_issues[0].reason or "mobile" in incompatible_issues[0].message

    # File Size Tests - Desktop
    def test_desktop_file_size_under_limit(self):
        """Desktop uploads under 10GB should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        }
        issues = self.desktop_checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 0

    def test_desktop_file_size_over_limit(self):
        """Desktop uploads over 10GB should be rejected."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 12 * 1024 * 1024 * 1024,  # 12GB
        }
        issues = self.desktop_checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 1
        assert "10GB" in incompatible_issues[0].reason or "desktop" in incompatible_issues[0].message

    def test_optimal_tiktok_video(self):
        """Test perfectly optimized TikTok video."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1080, 1920),
            "bitrate": 12_000_000,  # 12 Mbps
            "file_size": 150 * 1024 * 1024,  # 150MB
        }
        issues = self.mobile_checker.check(video_info)

        # Should have multiple compatible messages, no warnings/errors
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 3

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 0


class TestVimeoChecker:
    """Test cases for Vimeo platform compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = VimeoChecker()

    # Codec Tests
    def test_h264_recommended(self):
        """H.264 should be the recommended codec."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("recommended" in i.message for i in compatible_issues)

    def test_prores_accepted_with_warning(self):
        """ProRes should be accepted but with warning about upload time."""
        video_info = {
            "codec": "prores",
            "container": "mov",
            "resolution": (1920, 1080),
            "bitrate": 150_000_000,
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warning_issues) >= 1
        assert any("not recommended" in i.message for i in warning_issues)
        assert any("slow to upload" in i.reason for i in warning_issues)

    def test_unsupported_codec_warning(self):
        """Unsupported codecs should show warning."""
        video_info = {
            "codec": "av1",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("recommends H.264" in i.message for i in warning_issues)

    # Container Tests
    def test_mp4_container_compatible(self):
        """MP4 container should be fully compatible."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MP4" in i.message for i in compatible_issues)

    def test_mov_container_compatible(self):
        """MOV container should be fully compatible."""
        video_info = {
            "codec": "h264",
            "container": "mov",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MOV" in i.message for i in compatible_issues)

    # Bitrate Tests by Resolution
    def test_4k_optimal_bitrate(self):
        """4K video with 40-50 Mbps should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 45_000_000,  # 45 Mbps
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("4K" in i.message and "optimal" in i.message for i in compatible_issues)

    def test_4k_low_bitrate_warning(self):
        """4K video below 40 Mbps should show warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 30_000_000,  # 30 Mbps
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("4K" in i.message and "40-50 Mbps" in i.reason for i in warning_issues)

    def test_1080p_optimal_bitrate(self):
        """1080p video with 10-20 Mbps should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 15_000_000,  # 15 Mbps
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("1080p" in i.message and "optimal" in i.message for i in compatible_issues)

    def test_720p_optimal_bitrate(self):
        """720p video with 5-10 Mbps should be optimal."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "bitrate": 7_000_000,  # 7 Mbps
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("720p" in i.message and "optimal" in i.message for i in compatible_issues)

    def test_1080p_high_bitrate_warning(self):
        """1080p video above 20 Mbps should show warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "bitrate": 30_000_000,  # 30 Mbps
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("1080p" in i.message and "10-20 Mbps" in i.reason for i in warning_issues)


class TestFacebookChecker:
    """Test cases for Facebook platform compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = FacebookChecker()

    # Codec Tests
    def test_h264_recommended(self):
        """H.264 should be the recommended codec."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,  # 1GB
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("recommended" in i.message for i in compatible_issues)

    def test_hevc_supported_for_reels(self):
        """HEVC should be marked as supported for Reels."""
        video_info = {
            "codec": "hevc",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("Reels" in i.message for i in compatible_issues)

    def test_vp9_supported_for_reels(self):
        """VP9 should be marked as supported for Reels."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("Reels" in i.message for i in compatible_issues)

    def test_av1_supported_for_reels(self):
        """AV1 should be marked as supported for Reels."""
        video_info = {
            "codec": "av1",
            "container": "mp4",
            "resolution": (1080, 1920),
            "file_size": 500_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("Reels" in i.message for i in compatible_issues)

    def test_unsupported_codec_warning(self):
        """Unsupported codecs should show warning."""
        video_info = {
            "codec": "prores",
            "container": "mov",
            "resolution": (1920, 1080),
            "file_size": 2 * 1024 * 1024 * 1024,
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("recommends H.264" in i.message for i in warning_issues)

    # Container Tests
    def test_mp4_preferred(self):
        """MP4 container should be marked as preferred."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MP4" in i.message and "preferred" in i.message for i in compatible_issues)

    def test_mov_preferred(self):
        """MOV container should be marked as preferred."""
        video_info = {
            "codec": "h264",
            "container": "mov",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MOV" in i.message and "preferred" in i.message for i in compatible_issues)

    def test_avi_supported_not_recommended(self):
        """AVI container should be supported but not recommended."""
        video_info = {
            "codec": "h264",
            "container": "avi",
            "resolution": (1280, 720),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("not recommended" in i.message for i in warning_issues)

    # File Size Tests
    def test_file_size_under_limit(self):
        """Files under 4GB should be accepted."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 3 * 1024 * 1024 * 1024,  # 3GB
        }
        issues = self.checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 0

    def test_file_size_over_limit(self):
        """Files over 4GB should be rejected."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        }
        issues = self.checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 1
        assert "4GB" in incompatible_issues[0].message or "4GB" in incompatible_issues[0].reason

    # Resolution Tests
    def test_hd_resolution_suitable(self):
        """720p and above should be marked as suitable."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1280, 720),
            "file_size": 500_000_000,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any(
            "1280x720" in i.message and "suitable" in i.message for i in compatible_issues
        )

    def test_1080p_resolution_suitable(self):
        """1080p should be marked as suitable."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
            "file_size": 1024 * 1024 * 1024,
        }
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any(
            "1920x1080" in i.message and "suitable" in i.message for i in compatible_issues
        )
