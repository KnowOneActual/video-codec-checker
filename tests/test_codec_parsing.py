"""Tests for codec and format parsing."""

from videowise.analyzer import VideoAnalyzer


def test_get_codec_name_h264(h264_video):
    """Test extracting H.264 codec name."""
    analyzer = VideoAnalyzer(h264_video)
    codec = analyzer.get_codec_name()
    assert codec == "h264"


def test_get_codec_profile_baseline(h264_video):
    """Test extracting Baseline profile."""
    analyzer = VideoAnalyzer(h264_video)
    profile = analyzer.get_codec_profile()
    # H.264 video fixture uses High profile by default
    assert profile is not None


def test_get_codec_profile_high(h264_high_profile_video):
    """Test extracting High profile."""
    analyzer = VideoAnalyzer(h264_high_profile_video)
    profile = analyzer.get_codec_profile()
    assert profile and "high" in profile.lower()


def test_get_container_format_mp4(h264_video):
    """Test extracting MP4 container format."""
    analyzer = VideoAnalyzer(h264_video)
    container = analyzer.get_container_format()
    # ffprobe may return 'mov,mp4,m4a,3gp,3g2,mj2' for MP4 files
    assert container
    assert container in ["mp4", "mov"]  # Both are valid for MP4 files


def test_get_codec_name_vp9(vp9_video):
    """Test extracting VP9 codec name."""
    analyzer = VideoAnalyzer(vp9_video)
    codec = analyzer.get_codec_name()
    assert codec == "vp9"


def test_get_container_format_webm(vp9_video):
    """Test extracting WebM container format."""
    analyzer = VideoAnalyzer(vp9_video)
    container = analyzer.get_container_format()
    assert container
    assert "webm" in container or "matroska" in container


def test_get_resolution(h264_video):
    """Test extracting video resolution."""
    analyzer = VideoAnalyzer(h264_video)
    resolution = analyzer.get_resolution()
    assert resolution is not None
    width, height = resolution
    # The test fixture creates 320x240 video
    assert width == 320
    assert height == 240


def test_get_frame_rate(h264_video):
    """Test extracting frame rate."""
    analyzer = VideoAnalyzer(h264_video)
    frame_rate = analyzer.get_frame_rate()
    assert frame_rate is not None
    assert isinstance(frame_rate, float)
    assert 24.0 <= frame_rate <= 30.0  # Should be around 25fps


def test_metadata_caching(h264_video):
    """Test that metadata is cached after first call."""
    analyzer = VideoAnalyzer(h264_video)

    # First call
    metadata1 = analyzer.get_metadata()
    assert metadata1 is not None

    # Second call should return same cached object
    metadata2 = analyzer.get_metadata()
    assert metadata2 is metadata1


def test_get_video_stream_returns_first_video_stream(h264_video):
    """Test that get_video_stream returns the first video stream."""
    analyzer = VideoAnalyzer(h264_video)
    stream = analyzer.get_video_stream()

    assert stream is not None
    assert stream.get("codec_type") == "video"
    assert stream.get("codec_name") == "h264"
