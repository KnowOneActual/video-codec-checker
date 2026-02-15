"""Tests for batch processing functionality."""

import json

import pytest
from click.testing import CliRunner

from videowise.cli import cli, find_video_files


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_video_dir(tmp_path, h264_video, vp9_video):
    """Create a temporary directory with test videos."""
    video_dir = tmp_path / "videos"
    video_dir.mkdir()

    # Copy test videos to temp directory
    import shutil

    video1 = video_dir / "test1.mp4"
    video2 = video_dir / "test2.mp4"
    shutil.copy(h264_video, video1)
    shutil.copy(vp9_video, video2)

    return video_dir


@pytest.fixture
def nested_video_dir(tmp_path, h264_video):
    """Create a nested directory structure with videos."""
    root = tmp_path / "media"
    root.mkdir()

    # Create subdirectories
    sub1 = root / "folder1"
    sub2 = root / "folder2"
    sub1.mkdir()
    sub2.mkdir()

    # Copy videos to different levels
    import shutil

    shutil.copy(h264_video, root / "root_video.mp4")
    shutil.copy(h264_video, sub1 / "sub1_video.mp4")
    shutil.copy(h264_video, sub2 / "sub2_video.mp4")

    return root


# ============================================================================
# Tests for find_video_files helper function
# ============================================================================


def test_find_video_files_single_file(h264_video):
    """Test finding a single video file."""
    files = find_video_files([str(h264_video)])
    assert len(files) == 1
    assert files[0] == h264_video


def test_find_video_files_multiple_files(h264_video, vp9_video):
    """Test finding multiple video files."""
    files = find_video_files([str(h264_video), str(vp9_video)])
    assert len(files) == 2
    assert h264_video in files
    assert vp9_video in files


def test_find_video_files_directory_non_recursive(temp_video_dir):
    """Test finding videos in a directory without recursion."""
    files = find_video_files([str(temp_video_dir)], recursive=False)
    assert len(files) == 2


def test_find_video_files_directory_recursive(nested_video_dir):
    """Test finding videos in nested directories with recursion."""
    files = find_video_files([str(nested_video_dir)], recursive=True)
    assert len(files) == 3  # root + 2 subdirectories


def test_find_video_files_extension_filter(tmp_path, h264_video):
    """Test filtering by file extension."""
    import shutil

    # Create files with different extensions
    shutil.copy(h264_video, tmp_path / "video.mp4")
    shutil.copy(h264_video, tmp_path / "video.mov")
    shutil.copy(h264_video, tmp_path / "video.avi")

    # Only find .mp4 files
    files = find_video_files([str(tmp_path)], extensions=[".mp4"])
    assert len(files) == 1
    assert files[0].suffix == ".mp4"


def test_find_video_files_nonexistent_path():
    """Test handling of nonexistent paths."""
    files = find_video_files(["/nonexistent/path"])
    assert len(files) == 0


def test_find_video_files_empty_directory(tmp_path):
    """Test handling of empty directories."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    files = find_video_files([str(empty_dir)])
    assert len(files) == 0


# ============================================================================
# Tests for batch command
# ============================================================================


def test_batch_command_help(runner):
    """Test batch command help text."""
    result = runner.invoke(cli, ["batch", "--help"])
    assert result.exit_code == 0
    assert "Check multiple files or directories" in result.output
    assert "--recursive" in result.output
    assert "--extensions" in result.output


def test_batch_missing_system_flag(runner, h264_video):
    """Test that batch requires --system or --all flag."""
    result = runner.invoke(cli, ["batch", str(h264_video)])
    assert result.exit_code == 2
    assert "Must specify either --system or --all" in result.output


def test_batch_conflicting_flags(runner, h264_video):
    """Test that batch rejects both --system and --all."""
    result = runner.invoke(cli, ["batch", str(h264_video), "--system", "casparcg", "--all"])
    assert result.exit_code == 2
    assert "Cannot use both" in result.output


def test_batch_single_file(runner, h264_video):
    """Test batch command with a single file."""
    result = runner.invoke(cli, ["batch", str(h264_video), "--system", "casparcg"])
    assert result.exit_code in [0, 1, 2]
    # Single file batch no longer shows "Found X files" message
    assert "BATCH SUMMARY" in result.output


def test_batch_multiple_files(runner, h264_video, vp9_video):
    """Test batch command with multiple files."""
    result = runner.invoke(cli, ["batch", str(h264_video), str(vp9_video), "--system", "safari"])
    assert result.exit_code in [0, 1, 2]
    assert "Found 2 video file" in result.output
    assert "BATCH SUMMARY" in result.output


def test_batch_directory_non_recursive(runner, temp_video_dir):
    """Test batch command on a directory without recursion."""
    result = runner.invoke(cli, ["batch", str(temp_video_dir), "--system", "casparcg"])
    assert result.exit_code in [0, 1, 2]
    assert "Found 2 video file" in result.output


def test_batch_directory_recursive(runner, nested_video_dir):
    """Test batch command on nested directories with recursion."""
    result = runner.invoke(cli, ["batch", str(nested_video_dir), "--recursive", "--all"])
    assert result.exit_code in [0, 1, 2]
    assert "Found 3 video file" in result.output
    assert "BATCH SUMMARY" in result.output


def test_batch_with_all_flag(runner, h264_video):
    """Test batch command with --all flag."""
    result = runner.invoke(cli, ["batch", str(h264_video), "--all"])
    assert result.exit_code in [0, 1, 2]
    # Single file batch no longer shows "Found X files" message
    # Should check multiple systems
    systems_checked = result.output.split("Systems checked:")[1].split("\n")[0]
    assert "," in systems_checked  # Multiple systems


def test_batch_json_output(runner, h264_video, vp9_video):
    """Test batch command with JSON output."""
    result = runner.invoke(
        cli, ["batch", str(h264_video), str(vp9_video), "--system", "casparcg", "--json"]
    )
    assert result.exit_code in [0, 1, 2]

    # Verify JSON structure
    output = json.loads(result.output)
    assert "total_files" in output
    assert "processed_files" in output
    assert "systems_checked" in output
    assert "results" in output
    assert "errors" in output

    assert output["total_files"] == 2
    assert output["processed_files"] == 2
    assert len(output["results"]) == 2


def test_batch_json_all_systems(runner, h264_video):
    """Test batch command JSON output with --all flag."""
    result = runner.invoke(cli, ["batch", str(h264_video), "--all", "--json"])
    assert result.exit_code in [0, 1, 2]

    output = json.loads(result.output)
    assert len(output["systems_checked"]) > 1


def test_batch_verbose_mode(runner, temp_video_dir):
    """Test batch command with verbose output."""
    result = runner.invoke(cli, ["batch", str(temp_video_dir), "--system", "casparcg", "-v"])
    assert result.exit_code in [0, 1, 2]
    # Verbose should show individual file processing
    assert "Processing:" in result.output or "test1.mp4" in result.output


def test_batch_extension_filter(runner, tmp_path, h264_video):
    """Test batch command with extension filtering."""
    import shutil

    # Create files with different extensions
    shutil.copy(h264_video, tmp_path / "video.mp4")
    shutil.copy(h264_video, tmp_path / "video.mov")

    result = runner.invoke(
        cli, ["batch", str(tmp_path), "--extensions", ".mp4", "--system", "casparcg"]
    )
    assert result.exit_code in [0, 1, 2]
    # Single file batch no longer shows "Found X files" message
    assert "BATCH SUMMARY" in result.output


def test_batch_no_files_found(runner, tmp_path):
    """Test batch command when no video files are found."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    result = runner.invoke(cli, ["batch", str(empty_dir), "--system", "casparcg"])
    assert result.exit_code == 2
    assert "No video files found" in result.output


def test_batch_summary_statistics(runner, h264_video, vp9_video):
    """Test that batch summary shows correct statistics."""
    result = runner.invoke(cli, ["batch", str(h264_video), str(vp9_video), "--all"])
    assert result.exit_code in [0, 1, 2]

    # Summary should show counts
    assert "Total files processed:" in result.output
    assert "Systems checked:" in result.output

    # Should have status categories
    has_status = (
        "Fully compatible" in result.output
        or "Warnings" in result.output
        or "Incompatible" in result.output
    )
    assert has_status


def test_batch_mixed_valid_invalid_files(runner, tmp_path, h264_video):
    """Test batch processing with mix of valid and invalid files."""
    import shutil

    # Create a valid video
    shutil.copy(h264_video, tmp_path / "valid.mp4")

    # Create an invalid "video" (text file with .mp4 extension)
    invalid = tmp_path / "invalid.mp4"
    invalid.write_text("This is not a video file")

    result = runner.invoke(cli, ["batch", str(tmp_path), "--system", "casparcg"])

    # Should continue processing despite error
    assert "Found 2 video file" in result.output
    assert "BATCH SUMMARY" in result.output


def test_batch_exit_code_worst_case(runner, h264_video, vp9_video):
    """Test that batch returns worst-case exit code."""
    # VP9 is incompatible with Safari (exit code 2)
    result = runner.invoke(cli, ["batch", str(h264_video), str(vp9_video), "--system", "safari"])

    # Should return exit code 2 because VP9 is incompatible
    assert result.exit_code == 2


def test_batch_compatible_files_exit_code(runner, h264_video):
    """Test batch exit code when all files are compatible."""
    # H.264 should work fine with Chrome
    result = runner.invoke(cli, ["batch", str(h264_video), "--system", "chrome"])

    # Should return 0 or 1 (not incompatible)
    assert result.exit_code in [0, 1]
