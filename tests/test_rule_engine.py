"""Tests for rule-based compatibility engine."""

from videowise.compatibility import CompatibilityLevel
from videowise.rule_engine import RuleBasedChecker, RuleEngine


class TestRuleEngine:
    """Test rule engine functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()

    def test_get_available_systems(self):
        """Test retrieving list of available systems."""
        systems = self.engine.get_available_systems()
        assert isinstance(systems, list)
        assert len(systems) > 0
        assert "casparcg" in systems
        assert "instagram" in systems
        assert "davinci" in systems

    def test_get_profile_systems(self):
        """Test retrieving systems by profile."""
        live_systems = self.engine.get_profile_systems("live_production")
        assert "casparcg" in live_systems
        assert "vmix" in live_systems
        assert "obs" in live_systems

        editing_systems = self.engine.get_profile_systems("editing")
        assert "davinci" in editing_systems
        assert "premiere" in editing_systems
        assert "finalcut" in editing_systems

    def test_casparcg_hap_codec(self):
        """Test CasparCG HAP codec detection."""
        video_info = {
            "codec": "hap",
            "container": "mov",
            "resolution": (1920, 1080),
            "bitrate": 50_000_000,
        }
        issues = self.engine.check_compatibility(video_info, "casparcg")

        assert len(issues) > 0
        # Should have compatible issue for HAP
        hap_issues = [i for i in issues if "HAP" in i.message]
        assert len(hap_issues) > 0
        assert hap_issues[0].level == CompatibilityLevel.COMPATIBLE

    def test_casparcg_unsupported_codec(self):
        """Test CasparCG with unsupported codec."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
        }
        issues = self.engine.check_compatibility(video_info, "casparcg")

        # Should have incompatible issue
        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) > 0

    def test_instagram_h264_baseline(self):
        """Test Instagram H.264 baseline profile."""
        video_info = {
            "codec": "h264",
            "profile": "baseline",
            "resolution": (1080, 1920),
        }
        issues = self.engine.check_compatibility(video_info, "instagram")

        # Should NOT have warnings about re-encoding
        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        # May have resolution warnings, but not codec warnings
        codec_warnings = [i for i in warning_issues if "re-encode" in i.message.lower()]
        assert len(codec_warnings) == 0

    def test_instagram_wrong_codec(self):
        """Test Instagram with non-H.264 codec."""
        video_info = {
            "codec": "prores",
            "resolution": (1080, 1080),
        }
        issues = self.engine.check_compatibility(video_info, "instagram")

        # Should have warning about re-encoding
        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warning_issues) > 0
        assert any("re-encode" in i.message.lower() for i in warning_issues)

    def test_safari_incompatible_codec(self):
        """Test Safari with VP9 codec (unsupported)."""
        video_info = {
            "codec": "vp9",
            "container": "webm",
        }
        issues = self.engine.check_compatibility(video_info, "safari")

        # Should be incompatible
        incompatible_issues = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible_issues) > 0
        assert any("does not support" in i.message.lower() for i in incompatible_issues)

    def test_chrome_supported_codecs(self):
        """Test Chrome with supported codecs."""
        for codec in ["h264", "vp8", "vp9", "av1"]:
            video_info = {"codec": codec}
            issues = self.engine.check_compatibility(video_info, "chrome")

            # Should have at least one compatible issue
            compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
            assert len(compatible_issues) > 0, f"{codec} should be compatible with Chrome"

    def test_bitrate_conditions(self):
        """Test bitrate-based rules."""
        # High bitrate for vMix
        video_info = {
            "codec": "h264",
            "bitrate": 250_000_000,  # 250 Mbps
        }
        issues = self.engine.check_compatibility(video_info, "vmix")

        # Should have warning about high bitrate
        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warning_issues) > 0
        assert any("bitrate" in i.message.lower() for i in warning_issues)

    def test_resolution_conditions(self):
        """Test resolution-based rules."""
        # Large resolution for Instagram
        video_info = {
            "codec": "h264",
            "profile": "baseline",
            "resolution": (3840, 2160),  # 4K
        }
        issues = self.engine.check_compatibility(video_info, "instagram")

        # Should have warning about downscaling
        warning_issues = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        downscale_warnings = [i for i in warning_issues if "downscale" in i.message.lower()]
        assert len(downscale_warnings) > 0

    def test_template_substitution(self):
        """Test message template variable substitution."""
        video_info = {
            "codec": "h264",
            "bitrate": 150_000_000,  # 150 Mbps
            "resolution": (1920, 1080),
        }
        issues = self.engine.check_compatibility(video_info, "vmix")

        # Check that bitrate is properly formatted in message
        for issue in issues:
            if "Mbps" in issue.message:
                # Should show "150Mbps" not "150000000"
                assert "150" in issue.message
                assert "150000000" not in issue.message

    def test_unknown_system(self):
        """Test checking against unknown system."""
        video_info = {"codec": "h264"}
        issues = self.engine.check_compatibility(video_info, "nonexistent_system")

        assert len(issues) == 1
        assert issues[0].level == CompatibilityLevel.UNKNOWN
        assert "Unknown system" in issues[0].message

    def test_multiple_conditions(self):
        """Test rules with multiple conditions matching."""
        video_info = {
            "codec": "h264",
            "resolution": (3840, 2160),
            "bitrate": 250_000_000,
        }
        issues = self.engine.check_compatibility(video_info, "vmix")

        # Should trigger multiple rules (4K + high bitrate)
        assert len(issues) >= 2


class TestRuleBasedChecker:
    """Test RuleBasedChecker wrapper class."""

    def test_checker_interface(self):
        """Test that RuleBasedChecker implements CompatibilityChecker interface."""
        checker = RuleBasedChecker("casparcg")
        video_info = {"codec": "h264", "container": "mp4"}

        issues = checker.check(video_info)
        assert isinstance(issues, list)
        assert len(issues) > 0

    def test_different_systems(self):
        """Test creating checkers for different systems."""
        systems = ["casparcg", "instagram", "safari", "davinci"]
        video_info = {"codec": "h264"}

        for system in systems:
            checker = RuleBasedChecker(system)
            issues = checker.check(video_info)
            assert isinstance(issues, list)


class TestConditionEvaluation:
    """Test individual condition evaluation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RuleEngine()

    def test_codec_eq(self):
        """Test codec equality condition."""
        condition = {"codec_eq": "h264"}
        video_info = {"codec": "h264"}
        assert self.engine._evaluate_condition(condition, video_info) is True

        video_info = {"codec": "prores"}
        assert self.engine._evaluate_condition(condition, video_info) is False

    def test_codec_in(self):
        """Test codec in list condition."""
        condition = {"codec_in": ["h264", "prores", "dnxhd"]}

        for codec in ["h264", "prores", "dnxhd"]:
            video_info = {"codec": codec}
            assert self.engine._evaluate_condition(condition, video_info) is True

        video_info = {"codec": "vp9"}
        assert self.engine._evaluate_condition(condition, video_info) is False

    def test_codec_contains(self):
        """Test codec substring match."""
        condition = {"codec_contains": "prores"}

        for codec in ["prores", "prores422", "prores4444", "prores_proxy"]:
            video_info = {"codec": codec}
            assert self.engine._evaluate_condition(condition, video_info) is True

        video_info = {"codec": "h264"}
        assert self.engine._evaluate_condition(condition, video_info) is False

    def test_resolution_gte(self):
        """Test resolution greater than or equal condition."""
        condition = {"resolution_gte": [1920, 1080]}

        # Exactly 1080p
        video_info = {"resolution": (1920, 1080)}
        assert self.engine._evaluate_condition(condition, video_info) is True

        # 4K
        video_info = {"resolution": (3840, 2160)}
        assert self.engine._evaluate_condition(condition, video_info) is True

        # 720p
        video_info = {"resolution": (1280, 720)}
        assert self.engine._evaluate_condition(condition, video_info) is False

    def test_bitrate_gt(self):
        """Test bitrate greater than condition."""
        condition = {"bitrate_gt": 100_000_000}  # 100 Mbps

        video_info = {"bitrate": 150_000_000}
        assert self.engine._evaluate_condition(condition, video_info) is True

        video_info = {"bitrate": 50_000_000}
        assert self.engine._evaluate_condition(condition, video_info) is False

    def test_profile_contains(self):
        """Test profile substring condition."""
        condition = {"profile_contains": "baseline"}

        video_info = {"profile": "baseline"}
        assert self.engine._evaluate_condition(condition, video_info) is True

        video_info = {"profile": "high"}
        assert self.engine._evaluate_condition(condition, video_info) is False


class TestBackwardCompatibility:
    """Test backward compatibility with old API."""

    def test_module_level_functions(self):
        """Test that module-level functions still work."""
        from videowise.rule_engine import check_compatibility, get_available_systems

        # Test get_available_systems
        systems = get_available_systems()
        assert isinstance(systems, list)
        assert len(systems) > 0

        # Test check_compatibility
        video_info = {"codec": "h264"}
        issues = check_compatibility(video_info, "casparcg")
        assert isinstance(issues, list)
