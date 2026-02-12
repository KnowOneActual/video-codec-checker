"""Utility functions for VideoWise."""

from typing import Any, Dict

from videowise.analyzer import VideoAnalyzer


def get_video_info(analyzer: VideoAnalyzer) -> Dict[str, Any]:
    """Extract video information from analyzer into a dictionary.

    Args:
        analyzer: VideoAnalyzer instance

    Returns:
        Dictionary containing video information
    """
    return {
        "codec": analyzer.get_codec_name(),
        "profile": analyzer.get_codec_profile(),
        "container": analyzer.get_container_format(),
        "resolution": analyzer.get_resolution(),
        "frame_rate": analyzer.get_frame_rate(),
        "bitrate": analyzer.get_bitrate(),
        "file_size": analyzer.get_file_size(),
    }
