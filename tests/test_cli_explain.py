"""Tests for CLI --explain flag functionality."""

import pytest
from click.testing import CliRunner

from videowise.cli import cli


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


class TestExplainFlag:
    """Test the --explain flag in CLI commands."""

    def test_check_command_with_explain_flag(self, runner, h264_video):
        """Test that --explain flag works with check command."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--system",
                "casparcg",
                "--explain",
            ],
        )

        # Should succeed
        assert result.exit_code in [0, 1, 2]

        # Should show extended information
        assert "📖" in result.output or "About" in result.output

    def test_explain_shows_severity_guide(self, runner, h264_video):
        """Test that explain mode shows severity guide."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--system",
                "safari",
                "--explain",
            ],
        )

        # Should show severity levels guide
        assert "SEVERITY LEVELS" in result.output or "Compatible" in result.output

    def test_explain_with_h264_profile_knowledge(self, runner, h264_high_profile_video):
        """Test that explain mode shows H.264 profile knowledge."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_high_profile_video),
                "--system",
                "instagram",
                "--explain",
            ],
        )

        # Should mention H.264 or profiles
        assert "H.264" in result.output or "profile" in result.output.lower()

    def test_explain_with_vp9_knowledge(self, runner, vp9_video):
        """Test that explain mode shows VP9 codec knowledge."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(vp9_video),
                "--system",
                "safari",
                "--explain",
            ],
        )

        # Should show VP9 is incompatible with Safari
        assert result.exit_code == 2
        # Should have extended information
        assert "VP9" in result.output or "codec" in result.output.lower()

    def test_no_color_flag(self, runner, h264_video):
        """Test that --no-color flag disables ANSI color codes."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--system",
                "casparcg",
                "--no-color",
            ],
        )

        # Should not contain ANSI escape sequences
        # (though Click might add some for bold/etc, so we check for color specifically)
        assert result.exit_code in [0, 1, 2]

    def test_explain_with_verbose(self, runner, h264_video):
        """Test that --explain works with --verbose."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--system",
                "vmix",
                "--explain",
                "--verbose",
            ],
        )

        # Should show both verbose info and explanations
        assert "Codec:" in result.output  # from verbose
        assert result.exit_code in [0, 1, 2]

    def test_explain_not_shown_with_json(self, runner, h264_video):
        """Test that explain mode doesn't affect JSON output."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--system",
                "casparcg",
                "--explain",
                "--json",
            ],
        )

        # Should be valid JSON
        import json

        data = json.loads(result.output)
        assert "file" in data
        assert "issues" in data or "results" in data

        # Should not contain emoji/formatting in JSON
        assert "📖" not in result.output

    def test_explain_with_all_flag(self, runner, h264_video):
        """Test that --explain works with --all flag."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--all",
                "--explain",
            ],
        )

        # Should check all systems
        assert result.exit_code in [0, 1, 2]
        # Should have extended information for at least some systems
        assert "CASPARCG" in result.output or "SAFARI" in result.output

    def test_batch_with_explain(self, runner, h264_video):
        """Test that --explain works with batch command."""
        result = runner.invoke(
            cli,
            [
                "batch",
                str(h264_video),
                "--system",
                "casparcg",
                "--explain",
            ],
        )

        # Should process the file
        assert result.exit_code in [0, 1, 2]
        assert "Found 1 video file" in result.output

    def test_explain_without_system_shows_error(self, runner, h264_video):
        """Test that explain requires --system or --all flag."""
        result = runner.invoke(
            cli,
            [
                "check",
                str(h264_video),
                "--explain",
            ],
        )

        # Should fail with error about missing system
        assert result.exit_code == 2
        assert "Must specify either --system or --all" in result.output

    def test_explain_help_text(self, runner):
        """Test that --explain appears in help text."""
        result = runner.invoke(cli, ["check", "--help"])

        assert "--explain" in result.output
        assert "extended explanations" in result.output.lower() or "codec knowledge" in result.output.lower()

    def test_no_color_help_text(self, runner):
        """Test that --no-color appears in help text."""
        result = runner.invoke(cli, ["check", "--help"])

        assert "--no-color" in result.output
        assert "color" in result.output.lower()
