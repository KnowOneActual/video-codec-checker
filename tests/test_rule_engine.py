"""Tests for rule engine and YAML-based compatibility system."""

import pytest
from videowise.rule_engine import RuleEngine
from videowise.compatibility_v2 import (
    CompatibilityLevel,
    CasparCGChecker,
    DaVinciResolveChecker,
    InstagramChecker,
    check_compatibility,
    get_available_systems,
)


class TestRuleEngine:
    """Test rule engine core functionality."""

    def test_load_profiles(self):
        """Test that profiles load successfully."""
        engine = RuleEngine()
        assert engine.profiles is not None
        assert len(engine.profiles) > 0

    def test_list_systems(self):
        """Test listing all available systems."""
        engine = RuleEngine()
        systems = engine.list_systems()
        
        # Should have major systems
        assert "casparcg" in systems
        assert "davinci" in systems
        assert "premiere" in systems
        assert "instagram" in systems
        assert "safari" in systems
        assert "twitch" in systems
        
        # Should be sorted
        assert systems == sorted(systems)

    def test_get_system_profile(self):
        """Test retrieving system profile."""
        engine = RuleEngine()
        profile = engine.get_system_profile("casparcg")
        
        assert profile is not None
        assert profile["name"] == "CasparCG Server"
        assert profile["category"] == "live_production"
        assert "codecs" in profile

    def test_get_system_info(self):
        """Test system metadata retrieval."""
        engine = RuleEngine()
        info = engine.get_system_info("davinci")
        
        assert info is not None
        assert info["name"] == "DaVinci Resolve"
        assert info["category"] == "editing"
        assert "variants" in info
        assert "optimal_codecs" in info


class TestCodecChecking:
    """Test codec compatibility checking."""

    def test_optimal_codec(self):
        """Test optimal codec detection."""
        engine = RuleEngine()
        issues = engine.check_compatibility(
            {"codec": "hap", "container": "mov"},
            "casparcg"
        )
        
        assert len(issues) > 0
        compatible_issues = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible_issues) > 0
        assert any("optimal" in i.message.lower() for i in compatible_issues)

    def test_unsupported_codec(self):
        """Test unsupported codec warning."""
        engine = RuleEngine()
        issues = engine.check_compatibility(
            {"codec": "av1", "container": "mp4"},
            "safari"  # Safari doesn't support AV1
        )
        
        assert len(issues) > 0
        # Should have incompatible issue
        incompatible = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible) > 0

    def test_recommended_codec(self):
        """Test recommended codec tier."""
        engine = RuleEngine()
        issues = engine.check_compatibility(
            {"codec": "h264", "container": "mp4"},
            "obs"
        )
        
        assert len(issues) > 0
        assert any(i.level == CompatibilityLevel.COMPATIBLE for i in issues)


class TestConditionalRules:
    """Test conditional rule evaluation."""

    def test_bitrate_condition(self):
        """Test bitrate-based conditional rule."""
        engine = RuleEngine()
        
        # High bitrate should trigger warning
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "bitrate": 250_000_000,  # 250 Mbps
            },
            "vmix"
        )
        
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert len(warnings) > 0
        assert any("bitrate" in i.message.lower() for i in warnings)

    def test_resolution_condition(self):
        """Test resolution-based conditional rule."""
        engine = RuleEngine()
        
        # 4K should trigger specific messages
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "resolution": (3840, 2160),
                "bitrate": 250_000_000,
            },
            "casparcg"
        )
        
        # Should have 4K-related warning
        assert any("4K" in i.message or "4k" in i.message.lower() for i in issues)

    def test_complex_condition(self):
        """Test complex AND condition."""
        engine = RuleEngine()
        
        # HAP codec without MOV container
        issues = engine.check_compatibility(
            {
                "codec": "hap",
                "container": "mp4",  # Wrong container
            },
            "casparcg"
        )
        
        # Should warn about container
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("mov" in i.message.lower() for i in warnings)


class TestVariants:
    """Test system variant support."""

    def test_variant_loading(self):
        """Test variant-specific rules load."""
        engine = RuleEngine()
        
        # Desktop variant
        profile_desktop = engine.get_system_profile("playoutbee", "desktop")
        assert profile_desktop is not None
        
        # Raspberry Pi variant
        profile_pi = engine.get_system_profile("playoutbee", "raspberrypi")
        assert profile_pi is not None
        
        # Pi should have additional rules
        assert "rules" in profile_pi

    def test_variant_specific_rule(self):
        """Test variant-specific rule triggers."""
        engine = RuleEngine()
        
        # High bitrate on Raspberry Pi should warn
        issues_pi = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "bitrate": 60_000_000,  # 60 Mbps
            },
            "playoutbee",
            variant="raspberrypi"
        )
        
        # Should have Pi-specific warning
        warnings = [i for i in issues_pi if i.level == CompatibilityLevel.WARNING]
        assert any("raspberry pi" in i.message.lower() for i in warnings)

    def test_editing_platform_variants(self):
        """Test DaVinci Resolve free vs studio variants."""
        engine = RuleEngine()
        
        video_info = {"codec": "h264", "container": "mp4"}
        
        # Free version should warn about H.264
        issues_free = engine.check_compatibility(video_info, "davinci", "free")
        free_warnings = [i for i in issues_free if i.level == CompatibilityLevel.WARNING]
        assert len(free_warnings) > 0
        
        # Studio version should be compatible with H.264
        issues_studio = engine.check_compatibility(video_info, "davinci", "studio")
        studio_compatible = [i for i in issues_studio if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(studio_compatible) > 0


class TestLimits:
    """Test system limits checking."""

    def test_file_size_limit(self):
        """Test file size limit enforcement."""
        engine = RuleEngine()
        
        # Instagram 100MB limit
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "file_size": 150_000_000,  # 150MB
            },
            "instagram"
        )
        
        incompatible = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible) > 0
        assert any("file size" in i.message.lower() for i in incompatible)

    def test_resolution_limit(self):
        """Test resolution limit checking."""
        engine = RuleEngine()
        
        # Instagram max 1080x1920
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "resolution": (2160, 3840),  # Too high
            },
            "instagram"
        )
        
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("resolution" in i.message.lower() for i in warnings)

    def test_bitrate_range(self):
        """Test optimal bitrate range checking."""
        engine = RuleEngine()
        
        # TikTok optimal range 8-15 Mbps
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "container": "mp4",
                "bitrate": 3_000_000,  # 3 Mbps - too low
            },
            "tiktok"
        )
        
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("bitrate" in i.message.lower() for i in warnings)


class TestBackwardCompatibility:
    """Test backward-compatible API."""

    def test_class_based_api(self):
        """Test existing class-based API still works."""
        checker = CasparCGChecker(version="2.3")
        issues = checker.check({"codec": "hap", "container": "mov"})
        
        assert len(issues) > 0
        assert isinstance(issues[0].level, CompatibilityLevel)

    def test_function_based_api(self):
        """Test new simplified function API."""
        issues = check_compatibility(
            {"codec": "h264", "container": "mp4"},
            "premiere"
        )
        
        assert len(issues) > 0
        assert isinstance(issues[0].level, CompatibilityLevel)

    def test_get_available_systems_api(self):
        """Test system listing API."""
        systems = get_available_systems()
        
        assert isinstance(systems, list)
        assert len(systems) > 0
        assert "casparcg" in systems

    def test_checker_with_variant(self):
        """Test checker class with variant parameter."""
        checker = DaVinciResolveChecker(version="studio", platform="windows")
        issues = checker.check({"codec": "h264", "container": "mp4"})
        
        assert len(issues) > 0

    def test_social_media_checker(self):
        """Test social media checker."""
        checker = InstagramChecker()
        issues = checker.check({
            "codec": "h264",
            "profile": "high",
            "container": "mp4",
        })
        
        # Should warn about non-baseline profile
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        assert any("baseline" in i.message.lower() for i in warnings)


class TestRealWorldScenarios:
    """Test real-world video scenarios."""

    def test_live_production_workflow(self):
        """Test typical live production video."""
        engine = RuleEngine()
        
        # ProRes 422 in MOV - should be excellent for CasparCG
        issues = engine.check_compatibility(
            {
                "codec": "prores",
                "container": "mov",
                "resolution": (1920, 1080),
                "bitrate": 120_000_000,
            },
            "casparcg"
        )
        
        compatible = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible) > 0

    def test_social_media_upload(self):
        """Test social media optimized video."""
        engine = RuleEngine()
        
        # H.264 Baseline for Instagram
        issues = engine.check_compatibility(
            {
                "codec": "h264",
                "profile": "baseline",
                "container": "mp4",
                "resolution": (1080, 1920),
                "bitrate": 12_000_000,
                "file_size": 50_000_000,
            },
            "instagram"
        )
        
        # Should be compatible
        compatible = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible) > 0
        
        # Should have no incompatible issues
        incompatible = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]
        assert len(incompatible) == 0

    def test_4k_editing_workflow(self):
        """Test 4K editing scenario."""
        engine = RuleEngine()
        
        # DNxHR for 4K DaVinci Resolve
        issues = engine.check_compatibility(
            {
                "codec": "dnxhr",
                "container": "mov",
                "resolution": (3840, 2160),
                "bitrate": 150_000_000,
            },
            "davinci",
            "studio"
        )
        
        # Should be optimal
        compatible = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        assert len(compatible) > 0
        assert any("optimal" in i.message.lower() for i in compatible)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
