"""Tests for CLI functionality."""

import json

import pytest
from click.testing import CliRunner

from videowise.cli import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_cli_version(runner):
    """Test --version flag."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()
    assert "0.1.0" in result.output


def test_cli_help(runner):
    """Test --help flag."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Video Codec Compatibility Checker" in result.output


def test_check_command_help(runner):
    """Test check command --help."""
    result = runner.invoke(cli, ["check", "--help"])
    assert result.exit_code == 0
    assert "Check video compatibility with a specific system" in result.output
    assert "--system" in result.output
    assert "--all" in result.output


def test_check_missing_file(runner):
    """Test check command with non-existent file."""
    result = runner.invoke(cli, ["check", "nonexistent.mp4", "--system", "casparcg"])
    assert result.exit_code != 0


def test_check_missing_system(runner, h264_video):
    """Test check command without --system or --all flag."""
    result = runner.invoke(cli, ["check", str(h264_video)])
    assert result.exit_code != 0
    assert "system" in result.output.lower() or "all" in result.output.lower()


def test_check_h264_casparcg_compatible(runner, h264_video):
    """Test check command with compatible H.264 file for CasparCG."""
    result = runner.invoke(cli, ["check", str(h264_video), "--system", "casparcg"])
    # Should exit with 0 (compatible) or 1 (warning) but not 2 (incompatible)
    assert result.exit_code in [0, 1]
    assert "CasparCG" in result.output or "casparcg" in result.output.lower()


def test_check_json_output(runner, h264_video):
    """Test check command with JSON output."""
    result = runner.invoke(cli, ["check", str(h264_video), "--system", "safari", "--json"])
    assert result.exit_code in [0, 1, 2]

    # Verify JSON structure
    output = json.loads(result.output)
    assert "file" in output
    assert "system" in output
    assert "issues" in output
    assert isinstance(output["issues"], list)


def test_check_verbose_output(runner, h264_video):
    """Test check command with verbose flag."""
    result = runner.invoke(cli, ["check", str(h264_video), "--system", "instagram", "-v"])
    assert result.exit_code in [0, 1, 2]
    # Verbose should show more details
    assert len(result.output) > 0


def test_check_vp9_safari_incompatible(runner, vp9_video):
    """Test check command with incompatible VP9 file for Safari."""
    result = runner.invoke(cli, ["check", str(vp9_video), "--system", "safari"])
    # VP9 should be incompatible with Safari - exit code 2
    assert result.exit_code == 2
    assert "does not support" in result.output.lower() or "incompatible" in result.output.lower()


def test_check_h264_high_profile_instagram(runner, h264_high_profile_video):
    """Test check command with H.264 High Profile for Instagram."""
    result = runner.invoke(cli, ["check", str(h264_high_profile_video), "--system", "instagram"])
    # Should have warnings about profile
    assert result.exit_code in [0, 1]


# ============================================================================
# Tests for --all flag functionality
# ============================================================================


def test_check_all_flag_basic(runner, h264_video):
    """Test check command with --all flag."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all"])
    assert result.exit_code in [0, 1, 2]
    
    # Should show multiple systems
    output_lower = result.output.lower()
    assert "casparcg" in output_lower
    assert "safari" in output_lower
    assert "instagram" in output_lower
    
    # Should show summary section
    assert "summary" in output_lower


def test_check_all_flag_with_verbose(runner, h264_video):
    """Test --all flag with verbose output."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all", "-v"])
    assert result.exit_code in [0, 1, 2]
    
    # Verbose should show codec details
    assert "codec" in result.output.lower() or "h264" in result.output.lower()
    
    # Should still show summary
    assert "summary" in result.output.lower()


def test_check_all_flag_json_output(runner, h264_video):
    """Test --all flag with JSON output."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all", "--json"])
    assert result.exit_code in [0, 1, 2]
    
    # Verify JSON structure for multiple systems
    output = json.loads(result.output)
    assert "file" in output
    assert "systems_checked" in output
    assert "results" in output
    assert isinstance(output["systems_checked"], list)
    assert isinstance(output["results"], list)
    
    # Should have results for multiple systems
    assert len(output["systems_checked"]) > 1
    assert len(output["results"]) > 1
    
    # Each result should have proper structure
    for result_item in output["results"]:
        assert "system" in result_item
        assert "issues" in result_item
        assert isinstance(result_item["issues"], list)


def test_check_all_and_system_conflict(runner, h264_video):
    """Test that using both --all and --system raises an error."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all", "--system", "safari"])
    assert result.exit_code == 2
    assert "cannot" in result.output.lower() or "error" in result.output.lower()


def test_check_all_vp9_shows_incompatibilities(runner, vp9_video):
    """Test --all flag with VP9 video shows Safari incompatibility."""
    result = runner.invoke(cli, ["check", str(vp9_video), "--all"])
    
    # VP9 should be incompatible with Safari
    assert result.exit_code == 2  # At least one incompatible system
    
    output_lower = result.output.lower()
    # Should show Safari as incompatible
    assert "safari" in output_lower
    assert "incompatible" in output_lower or "does not support" in output_lower


def test_check_all_summary_categories(runner, h264_video):
    """Test that --all flag produces proper summary with categories."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all"])
    assert result.exit_code in [0, 1, 2]
    
    output_lower = result.output.lower()
    
    # Summary should exist
    assert "summary" in output_lower
    
    # Should have at least one category (compatible, warning, or incompatible)
    has_category = (
        "compatible" in output_lower
        or "warning" in output_lower
        or "incompatible" in output_lower
    )
    assert has_category


def test_check_all_exit_code_worst_case(runner, vp9_video):
    """Test that --all flag returns worst-case exit code."""
    # VP9 is incompatible with Safari (exit code 2)
    result = runner.invoke(cli, ["check", str(vp9_video), "--all"])
    
    # Should return 2 (incompatible) because Safari doesn't support VP9
    assert result.exit_code == 2


def test_check_all_systems_count(runner, h264_video):
    """Test that --all flag checks all available systems."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all", "--json"])
    output = json.loads(result.output)
    
    # Should check at least 9 systems (as documented in README)
    # CasparCG, vMix, OBS, QLab, ProPresenter, Safari, Chrome, Instagram, Twitter
    assert len(output["systems_checked"]) >= 9


def test_check_all_individual_system_results(runner, h264_video):
    """Test that --all flag provides individual results for each system."""
    result = runner.invoke(cli, ["check", str(h264_video), "--all"])
    output = result.output
    
    # Each system should have its own section with separator
    assert output.count("="*60) >= 2  # At least summary and one system section
    
    # Should show results for known systems
    systems = ["casparcg", "vmix", "obs", "safari", "instagram"]
    for system in systems:
        assert system in output.lower()
