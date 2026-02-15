"""Tests for CasparCG and PlayoutBee playout system checkers."""

from videowise.compatibility import CasparCGChecker, CompatibilityLevel, PlayoutBeeChecker


class TestCasparCGChecker:
    """Test cases for enhanced CasparCG Server compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = CasparCGChecker(version="2.3")

    # HAP Codec Tests
    def test_hap_codec_supported(self):
        """HAP codec should be supported for GPU acceleration."""
        video_info = {"codec": "hap", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1
        assert any("GPU-accelerated" in i.message for i in compatible_issues)

    def test_hap_alpha_transparency_support(self):
        """HAP Alpha should be recognized for transparency support."""
        video_info = {"codec": "hap_alpha", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("alpha" in i.message.lower() for i in compatible_issues)
        assert any("transparency" in i.reason.lower() for i in compatible_issues)

    def test_hap_q_high_quality(self):
        """HAP Q should be recognized as high-quality variant."""
        video_info = {"codec": "hap_q", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any(
            "high-quality" in i.message.lower() or "HAP Q" in i.message for i in compatible_issues
        )

    def test_hap_requires_mov_container(self):
        """HAP codec in non-MOV container should show warning."""
        video_info = {"codec": "hap", "container": "mp4"}
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("MOV" in i.message or "container" in i.message.lower() for i in warning_issues)

    # NotchLC Tests
    def test_notchlc_codec_supported(self):
        """NotchLC should be supported for broadcast quality."""
        video_info = {"codec": "notchlc", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1
        assert any("NotchLC" in i.message for i in compatible_issues)

    # ProRes Alpha Channel
    def test_prores4444_alpha_channel(self):
        """ProRes 4444 should be recognized for alpha channel support."""
        video_info = {"codec": "prores4444", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("alpha" in i.message.lower() for i in compatible_issues)
        assert any("transparency" in i.reason.lower() for i in compatible_issues)

    # Legacy Codec Support
    def test_h264_still_supported(self):
        """H.264 should still be supported after enhancements."""
        video_info = {"codec": "h264", "container": "mp4"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_prores_still_supported(self):
        """ProRes should still be supported after enhancements."""
        video_info = {"codec": "prores", "container": "mov"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    def test_dnxhd_still_supported(self):
        """DNxHD should still be supported after enhancements."""
        video_info = {"codec": "dnxhd", "container": "mxf"}
        issues = self.checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    # 4K Bandwidth Warnings
    def test_4k_high_bitrate_warning(self):
        """4K content with very high bitrate should show warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 250_000_000,  # 250 Mbps
        }
        issues = self.checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("4K" in i.message and "bandwidth" in i.message.lower() for i in warning_issues)

    def test_4k_moderate_bitrate_no_warning(self):
        """4K content with moderate bitrate should not show bandwidth warning."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
            "bitrate": 150_000_000,  # 150 Mbps
        }
        issues = self.checker.check(video_info)

        bandwidth_warnings = [
            i
            for i in issues
            if i.level == CompatibilityLevel.WARNING and "bandwidth" in i.message.lower()
        ]
        assert len(bandwidth_warnings) == 0

    # Unsupported Codec
    def test_unsupported_codec_incompatible(self):
        """Unsupported codecs should still be marked as incompatible."""
        video_info = {"codec": "av1", "container": "mp4"}
        issues = self.checker.check(video_info)

        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) == 1
        assert "does not support" in incompatible_issues[0].message


class TestPlayoutBeeChecker:
    """Test cases for PlayoutBee playout software compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.desktop_checker = PlayoutBeeChecker(platform="desktop")
        self.pi_checker = PlayoutBeeChecker(platform="raspberrypi")

    # HAP Codec Tests
    def test_hap_optimal_for_playoutbee(self):
        """HAP codec should be marked as optimal."""
        video_info = {"codec": "hap", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("optimal" in i.message.lower() for i in compatible_issues)
        assert any("GPU-accelerated" in i.reason for i in compatible_issues)

    def test_hap_alpha_transparency(self):
        """HAP Alpha should be recognized for transparency."""
        video_info = {"codec": "hap_alpha", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any(
            "transparency" in i.message.lower() or "alpha" in i.message.lower()
            for i in compatible_issues
        )

    def test_hap_q_desktop_optimal(self):
        """HAP Q should be optimal for desktop systems."""
        video_info = {"codec": "hap_q", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any(
            "high-quality" in i.message.lower() or "HAP Q" in i.message for i in compatible_issues
        )

    def test_hap_q_raspberry_pi_warning(self):
        """HAP Q should show warning on Raspberry Pi."""
        video_info = {"codec": "hap_q", "container": "mov"}
        issues = self.pi_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("Raspberry Pi" in i.message for i in warning_issues)
        assert any("standard HAP" in i.suggestion for i in warning_issues)

    def test_hap_requires_mov_container(self):
        """HAP codec without MOV container should show warning."""
        video_info = {"codec": "hap", "container": "mp4"}
        issues = self.desktop_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("MOV" in i.message and "requires" in i.message for i in warning_issues)

    # H.264 Tests
    def test_h264_compatible_desktop(self):
        """H.264 should be compatible on desktop."""
        video_info = {"codec": "h264", "container": "mp4", "bitrate": 30_000_000}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("H.264" in i.message for i in compatible_issues)

    def test_h264_high_bitrate_pi_warning(self):
        """High bitrate H.264 should show warning on Raspberry Pi."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "bitrate": 60_000_000,  # 60 Mbps
        }
        issues = self.pi_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("Raspberry Pi" in i.message for i in warning_issues)
        assert any("50 Mbps" in i.suggestion or "HAP" in i.suggestion for i in warning_issues)

    def test_h264_low_bitrate_pi_ok(self):
        """Low bitrate H.264 should be fine on Raspberry Pi."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "bitrate": 30_000_000,  # 30 Mbps
        }
        issues = self.pi_checker.check(video_info)

        # Should not have Raspberry Pi-specific bitrate warnings
        pi_warnings = [
            i
            for i in issues
            if i.level == CompatibilityLevel.WARNING
            and "Raspberry Pi" in i.message
            and "bitrate" in i.message.lower()
        ]
        assert len(pi_warnings) == 0

    # ProRes Tests
    def test_prores4444_alpha_support(self):
        """ProRes 4444 should be recognized for alpha channel."""
        video_info = {"codec": "prores4444", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("alpha" in i.message.lower() for i in compatible_issues)

    def test_prores_on_raspberry_pi_warning(self):
        """ProRes should show warning on Raspberry Pi."""
        video_info = {"codec": "prores", "container": "mov"}
        issues = self.pi_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("Raspberry Pi" in i.message and "demanding" in i.message for i in warning_issues)
        assert any("HAP" in i.suggestion for i in warning_issues)

    def test_prores_on_desktop_compatible(self):
        """ProRes should be compatible on desktop."""
        video_info = {"codec": "prores", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) >= 1

    # Container Tests
    def test_mov_container_supported(self):
        """MOV container should be supported."""
        video_info = {"codec": "h264", "container": "mov"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MOV" in i.message for i in compatible_issues)

    def test_mp4_container_supported(self):
        """MP4 container should be supported."""
        video_info = {"codec": "h264", "container": "mp4"}
        issues = self.desktop_checker.check(video_info)

        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert any("MP4" in i.message for i in compatible_issues)

    # Resolution Tests - Raspberry Pi
    def test_1080p_on_raspberry_pi_ok(self):
        """1080p should be fine on Raspberry Pi."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (1920, 1080),
        }
        issues = self.pi_checker.check(video_info)

        # Should not have resolution warnings
        resolution_warnings = [
            i
            for i in issues
            if i.level == CompatibilityLevel.WARNING and "resolution" in i.message.lower()
        ]
        assert len(resolution_warnings) == 0

    def test_4k_on_raspberry_pi_warning(self):
        """4K should show warning on Raspberry Pi."""
        video_info = {
            "codec": "h264",
            "container": "mp4",
            "resolution": (3840, 2160),
        }
        issues = self.pi_checker.check(video_info)

        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("too high" in i.message and "Raspberry Pi" in i.message for i in warning_issues)
        assert any("1080p" in i.suggestion for i in warning_issues)
