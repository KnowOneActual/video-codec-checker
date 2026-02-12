"""Tests for CLI functionality."""

import pytest
from click.testing import CliRunner
from videowise.cli import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_cli_version(runner):
    """Test --version flag."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'videowise' in result.output.lower()
    assert '0.1.0' in result.output


def test_cli_help(runner):
    """Test --help flag."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'VideoWise' in result.output


def test_check_command_help(runner):
    """Test check command --help."""
    result = runner.invoke(cli, ['check', '--help'])
    assert result.exit_code == 0
    assert 'Check video file compatibility' in result.output
    assert '--system' in result.output


def test_check_missing_file(runner):
    """Test check command with non-existent file."""
    result = runner.invoke(cli, ['check', 'nonexistent.mp4', '--system', 'casparcg'])
    assert result.exit_code != 0


def test_check_missing_system(runner, h264_video):
    """Test check command without --system flag."""
    result = runner.invoke(cli, ['check', str(h264_video)])
    assert result.exit_code != 0
    assert 'system' in result.output.lower() or 'missing' in result.output.lower()


def test_check_h264_casparcg_compatible(runner, h264_video):
    """Test check command with compatible H.264 file for CasparCG."""
    result = runner.invoke(cli, ['check', str(h264_video), '--system', 'casparcg'])
    # Should exit with 0 (compatible) or 1 (warning) but not 2 (incompatible)
    assert result.exit_code in [0, 1]
    assert 'CasparCG' in result.output or 'casparcg' in result.output.lower()


def test_check_json_output(runner, h264_video):
    """Test check command with JSON output."""
    result = runner.invoke(cli, ['check', str(h264_video), '--system', 'safari', '--json'])
    assert result.exit_code in [0, 1, 2]
    
    # Verify JSON structure
    import json
    output = json.loads(result.output)
    assert 'file' in output
    assert 'system' in output
    assert 'issues' in output
    assert isinstance(output['issues'], list)


def test_check_verbose_output(runner, h264_video):
    """Test check command with verbose flag."""
    result = runner.invoke(cli, ['check', str(h264_video), '--system', 'instagram', '-v'])
    assert result.exit_code in [0, 1, 2]
    # Verbose should show more details
    assert len(result.output) > 0


def test_check_vp9_safari_incompatible(runner, vp9_video):
    """Test check command with incompatible VP9 file for Safari."""
    result = runner.invoke(cli, ['check', str(vp9_video), '--system', 'safari'])
    # VP9 should be incompatible with Safari
    assert result.exit_code == 2
    assert 'does not support' in result.output.lower() or 'incompatible' in result.output.lower()


def test_check_h264_high_profile_instagram(runner, h264_high_profile_video):
    """Test check command with H.264 High Profile for Instagram."""
    result = runner.invoke(cli, ['check', str(h264_high_profile_video), '--system', 'instagram'])
    # Should have warnings about profile
    assert result.exit_code in [0, 1]
