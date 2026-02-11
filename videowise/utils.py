"""Utility functions for VideoWise."""

from typing import Dict, Any, Optional
from pathlib import Path


def get_video_info(analyzer) -> Dict[str, Any]:
    """Convert VideoAnalyzer instance to video_info dictionary.
    
    Args:
        analyzer: VideoAnalyzer instance
        
    Returns:
        Dictionary containing video metadata for compatibility checking
    """
    video_info = {
        'codec': analyzer.get_codec_name(),
        'profile': analyzer.get_codec_profile(),
        'container': analyzer.get_container_format(),
        'resolution': analyzer.get_resolution(),
        'bitrate': analyzer.get_bitrate(),
        'frame_rate': analyzer.get_frame_rate(),
    }
    
    # Add file size
    try:
        file_path = Path(analyzer.file_path)
        if file_path.exists():
            video_info['file_size'] = file_path.stat().st_size
    except (OSError, AttributeError):
        video_info['file_size'] = None
    
    return video_info
