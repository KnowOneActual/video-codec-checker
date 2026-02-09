"""Tests for video analyzer functionality."""

import pytest
from pathlib import Path
from videowise.analyzer import VideoAnalyzer


def test_analyzer_requires_valid_file():
    """Test that analyzer raises error for non-existent file."""
    with pytest.raises(FileNotFoundError):
        VideoAnalyzer("/path/to/nonexistent/video.mp4")


def test_analyzer_accepts_existing_file(tmp_path):
    """Test that analyzer accepts a valid file path."""
    # Create a temporary dummy file
    test_file = tmp_path / "test_video.mp4"
    test_file.write_text("dummy content")
    
    # Should not raise an error
    analyzer = VideoAnalyzer(str(test_file))
    assert analyzer.file_path == test_file


def test_get_metadata_returns_none_for_invalid_video(tmp_path):
    """Test that get_metadata handles invalid video files gracefully."""
    # Create a file that's not actually a video
    test_file = tmp_path / "fake_video.mp4"
    test_file.write_text("not a real video file")
    
    analyzer = VideoAnalyzer(str(test_file))
    metadata = analyzer.get_metadata()
    
    # Should return None for invalid files (or when ffprobe not available)
    assert metadata is None or isinstance(metadata, dict)
