"""Tests for codec information parsing."""

import pytest
from videowise.analyzer import VideoAnalyzer


def test_get_codec_name_h264(h264_video):
    """Test that we can extract H.264 codec name."""
    analyzer = VideoAnalyzer(str(h264_video))
    codec = analyzer.get_codec_name()
    
    assert codec == 'h264'


def test_get_codec_profile_baseline(h264_video):
    """Test that we can extract codec profile for baseline H.264."""
    analyzer = VideoAnalyzer(str(h264_video))
    profile = analyzer.get_codec_profile()
    
    # Profile should contain 'Baseline' or 'Constrained Baseline'
    assert profile is not None
    assert 'baseline' in profile.lower()


def test_get_codec_profile_high(h264_high_profile_video):
    """Test that we can extract codec profile for high profile H.264."""
    analyzer = VideoAnalyzer(str(h264_high_profile_video))
    profile = analyzer.get_codec_profile()
    
    assert profile is not None
    assert 'high' in profile.lower()


def test_get_container_format_mp4(h264_video):
    """Test that we can identify MP4 container format."""
    analyzer = VideoAnalyzer(str(h264_video))
    container = analyzer.get_container_format()
    
    assert container is not None
    # MP4 format is often reported as 'mov,mp4,m4a,3gp,3g2,mj2'
    assert 'mp4' in container


def test_get_codec_name_vp9(vp9_video):
    """Test that we can extract VP9 codec name."""
    analyzer = VideoAnalyzer(str(vp9_video))
    codec = analyzer.get_codec_name()
    
    assert codec == 'vp9'


def test_get_container_format_webm(vp9_video):
    """Test that we can identify WebM container format."""
    analyzer = VideoAnalyzer(str(vp9_video))
    container = analyzer.get_container_format()
    
    assert container is not None
    assert 'webm' in container or 'matroska' in container


def test_get_resolution(h264_video):
    """Test that we can extract video resolution."""
    analyzer = VideoAnalyzer(str(h264_video))
    resolution = analyzer.get_resolution()
    
    assert resolution == (320, 240)


def test_get_frame_rate(h264_video):
    """Test that we can extract frame rate."""
    analyzer = VideoAnalyzer(str(h264_video))
    frame_rate = analyzer.get_frame_rate()
    
    assert frame_rate is not None
    assert '/' in frame_rate  # Should be in format like '25/1' or '30000/1001'


def test_metadata_caching(h264_video):
    """Test that metadata is cached after first retrieval."""
    analyzer = VideoAnalyzer(str(h264_video))
    
    # First call
    metadata1 = analyzer.get_metadata()
    # Second call should return cached version
    metadata2 = analyzer.get_metadata()
    
    assert metadata1 is metadata2  # Should be the same object


def test_get_video_stream_returns_first_video_stream(h264_video):
    """Test that get_video_stream returns the first video stream."""
    analyzer = VideoAnalyzer(str(h264_video))
    stream = analyzer.get_video_stream()
    
    assert stream is not None
    assert stream.get('codec_type') == 'video'
    assert stream.get('codec_name') == 'h264'
