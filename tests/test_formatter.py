"""Tests for the ExplanationFormatter."""

import pytest

from videowise.compatibility import CompatibilityIssue, CompatibilityLevel
from videowise.formatter import ExplanationFormatter, get_severity_info


class TestExplanationFormatter:
    """Test the ExplanationFormatter class."""

    def test_format_compatible_issue(self):
        """Test formatting a compatible issue."""
        formatter = ExplanationFormatter(use_color=False)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.COMPATIBLE,
            message="Video is compatible",
        )

        output = formatter.format_issue(issue)

        assert "✅" in output
        assert "Video is compatible" in output

    def test_format_warning_issue(self):
        """Test formatting a warning issue."""
        formatter = ExplanationFormatter(use_color=False)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="High bitrate may cause issues",
            reason="Bitrate exceeds 100Mbps",
            suggestion="Consider ProRes Proxy for lower bitrate",
        )

        output = formatter.format_issue(issue)

        assert "⚠️" in output
        assert "High bitrate may cause issues" in output
        assert "Reason: Bitrate exceeds 100Mbps" in output
        assert "Suggestion: Consider ProRes Proxy" in output

    def test_format_incompatible_issue(self):
        """Test formatting an incompatible issue."""
        formatter = ExplanationFormatter(use_color=False)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.INCOMPATIBLE,
            message="VP9 codec not supported",
            reason="Safari only supports H.264 and HEVC",
            suggestion="Convert to H.264",
        )

        output = formatter.format_issue(issue)

        assert "❌" in output
        assert "VP9 codec not supported" in output
        assert "Reason: Safari only supports H.264 and HEVC" in output
        assert "Suggestion: Convert to H.264" in output

    def test_color_output(self):
        """Test that color codes are included when use_color=True."""
        formatter = ExplanationFormatter(use_color=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="Test warning",
        )

        output = formatter.format_issue(issue)

        # Should contain ANSI color codes
        assert "\033[" in output  # ANSI escape sequence

    def test_plain_text_output(self):
        """Test that color codes are excluded when use_color=False."""
        formatter = ExplanationFormatter(use_color=False)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="Test warning",
        )

        output = formatter.format_issue(issue)

        # Should NOT contain ANSI color codes
        assert "\033[" not in output

    def test_explain_mode_basic(self):
        """Test that explain mode adds extended information."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="Test warning",
        )

        output = formatter.format_issue(issue)

        # Should include severity explanation
        assert "📖 About Warning:" in output
        assert "may have issues" in output

    def test_explain_mode_h264_profile_knowledge(self):
        """Test codec knowledge for H.264 profiles."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="H.264 High Profile may have compatibility issues",
        )

        output = formatter.format_issue(issue, system="instagram")

        # Should include H.264 profile knowledge
        assert "💡 Additional Context:" in output
        assert "H.264 profiles" in output or "Baseline" in output

    def test_explain_mode_vp9_knowledge(self):
        """Test codec knowledge for VP9."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.INCOMPATIBLE,
            message="VP9 codec not supported",
        )

        output = formatter.format_issue(issue, system="safari")

        # Should include VP9 knowledge
        assert "💡 Additional Context:" in output
        assert "VP9" in output
        assert "H.264" in output or "HEVC" in output

    def test_explain_mode_prores_proxy_knowledge(self):
        """Test codec knowledge for ProRes Proxy."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.COMPATIBLE,
            message="ProRes Proxy is optimal for QLab",
        )

        output = formatter.format_issue(issue, system="qlab")

        # Should include ProRes Proxy knowledge
        assert "💡 Additional Context:" in output
        assert "ProRes Proxy" in output or "optimized for editing" in output

    def test_explain_mode_prores_4444_knowledge(self):
        """Test codec knowledge for ProRes 4444."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.COMPATIBLE,
            message="ProRes 4444 supports alpha channels",
        )

        output = formatter.format_issue(issue, system="propresenter")

        # Should include ProRes 4444 knowledge
        assert "💡 Additional Context:" in output
        assert "4444" in output
        assert "alpha" in output or "transparency" in output

    def test_explain_mode_hap_knowledge(self):
        """Test codec knowledge for HAP."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.COMPATIBLE,
            message="HAP codec provides best performance",
        )

        output = formatter.format_issue(issue, system="propresenter")

        # Should include HAP knowledge
        assert "💡 Additional Context:" in output
        assert "HAP" in output
        assert "GPU" in output or "graphics card" in output

    def test_explain_mode_bitrate_knowledge(self):
        """Test codec knowledge for high bitrate."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="Bitrate of 200Mbps may cause performance issues",
        )

        output = formatter.format_issue(issue, system="vmix")

        # Should include bitrate knowledge
        assert "💡 Additional Context:" in output
        assert "bitrate" in output.lower()
        assert "SSD" in output or "ProRes Proxy" in output

    def test_explain_mode_vfr_knowledge(self):
        """Test codec knowledge for variable frame rate."""
        formatter = ExplanationFormatter(use_color=False, explain_mode=True)
        issue = CompatibilityIssue(
            level=CompatibilityLevel.WARNING,
            message="Variable frame rate will cause timing issues",
        )

        output = formatter.format_issue(issue, system="casparcg")

        # Should include VFR knowledge
        assert "💡 Additional Context:" in output
        assert "Variable Frame Rate" in output or "VFR" in output
        assert "Constant Frame Rate" in output or "CFR" in output

    def test_format_severity_guide(self):
        """Test severity guide generation."""
        formatter = ExplanationFormatter(use_color=False)
        guide = formatter.format_severity_guide()

        # Should include all three severity levels
        assert "COMPATIBLE" in guide
        assert "WARNING" in guide
        assert "INCOMPATIBLE" in guide

        # Should include descriptions
        assert "will work without issues" in guide
        assert "may have issues" in guide
        assert "will NOT work" in guide

    def test_format_system_summary_no_issues(self):
        """Test system summary with no issues."""
        formatter = ExplanationFormatter(use_color=False)
        summary = formatter.format_system_summary("casparcg", [])

        assert "CASPARCG" in summary
        assert "No compatibility issues found" in summary

    def test_format_system_summary_with_issues(self):
        """Test system summary with multiple issues."""
        formatter = ExplanationFormatter(use_color=False)
        issues = [
            CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="H.264 is supported",
            ),
            CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="High bitrate warning",
            ),
        ]

        summary = formatter.format_system_summary("vmix", issues)

        assert "VMIX" in summary
        assert "H.264 is supported" in summary
        assert "High bitrate warning" in summary

    def test_format_system_summary_orders_by_severity(self):
        """Test that system summary shows worst issues first."""
        formatter = ExplanationFormatter(use_color=False)
        issues = [
            CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="Compatible issue",
            ),
            CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message="Incompatible issue",
            ),
            CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Warning issue",
            ),
        ]

        summary = formatter.format_system_summary("test", issues)

        # Find positions of each issue in output
        incompatible_pos = summary.find("Incompatible issue")
        warning_pos = summary.find("Warning issue")
        compatible_pos = summary.find("Compatible issue")

        # Incompatible should come first, then warning, then compatible
        assert incompatible_pos < warning_pos < compatible_pos


class TestGetSeverityInfo:
    """Test the get_severity_info helper function."""

    def test_get_compatible_info(self):
        """Test getting info for COMPATIBLE level."""
        info = get_severity_info(CompatibilityLevel.COMPATIBLE)

        assert info["icon"] == "✅"
        assert info["name"] == "Compatible"
        assert "work without issues" in info["description"]

    def test_get_warning_info(self):
        """Test getting info for WARNING level."""
        info = get_severity_info(CompatibilityLevel.WARNING)

        assert info["icon"] == "⚠️"
        assert info["name"] == "Warning"
        assert "may have issues" in info["description"]

    def test_get_incompatible_info(self):
        """Test getting info for INCOMPATIBLE level."""
        info = get_severity_info(CompatibilityLevel.INCOMPATIBLE)

        assert info["icon"] == "❌"
        assert info["name"] == "Incompatible"
        assert "will NOT work" in info["description"]

    def test_info_is_copy(self):
        """Test that returned info is a copy, not reference."""
        info1 = get_severity_info(CompatibilityLevel.COMPATIBLE)
        info2 = get_severity_info(CompatibilityLevel.COMPATIBLE)

        # Modify one
        info1["icon"] = "MODIFIED"

        # Other should be unchanged
        assert info2["icon"] == "✅"
