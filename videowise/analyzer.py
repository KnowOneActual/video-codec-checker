"""Core video analysis functionality."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class VideoAnalyzer:
    """Analyzes video files to extract codec and format information."""

    def __init__(self, file_path: str):
        """Initialize analyzer with a video file path.
        
        Args:
            file_path: Path to the video file to analyze
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")
        self._metadata = None

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Extract video metadata using ffprobe.
        
        Returns:
            Dictionary containing video metadata, or None if extraction fails
        """
        if self._metadata is not None:
            return self._metadata
            
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(self.file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self._metadata = json.loads(result.stdout)
            return self._metadata
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
            return None

    def get_video_stream(self) -> Optional[Dict[str, Any]]:
        """Get the first video stream from metadata.
        
        Returns:
            Dictionary containing video stream info, or None if not found
        """
        metadata = self.get_metadata()
        if not metadata or 'streams' not in metadata:
            return None
        
        for stream in metadata['streams']:
            if stream.get('codec_type') == 'video':
                return stream
        
        return None

    def get_codec_name(self) -> Optional[str]:
        """Get the video codec name.
        
        Returns:
            Codec name (e.g., 'h264', 'vp9', 'prores'), or None if not found
        """
        stream = self.get_video_stream()
        return stream.get('codec_name') if stream else None

    def get_codec_profile(self) -> Optional[str]:
        """Get the video codec profile.
        
        Returns:
            Codec profile (e.g., 'Baseline', 'High', 'Main'), or None if not found
        """
        stream = self.get_video_stream()
        return stream.get('profile') if stream else None

    def get_container_format(self) -> Optional[str]:
        """Get the container format.
        
        Returns:
            Container format name (e.g., 'mov,mp4,m4a,3gp,3g2,mj2'), or None if not found
        """
        metadata = self.get_metadata()
        if not metadata or 'format' not in metadata:
            return None
        
        return metadata['format'].get('format_name')

    def get_resolution(self) -> Optional[tuple[int, int]]:
        """Get video resolution.
        
        Returns:
            Tuple of (width, height), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None
        
        width = stream.get('width')
        height = stream.get('height')
        
        if width and height:
            return (width, height)
        
        return None

    def get_frame_rate(self) -> Optional[str]:
        """Get video frame rate.
        
        Returns:
            Frame rate as string (e.g., '30/1', '24000/1001'), or None if not found
        """
        stream = self.get_video_stream()
        return stream.get('r_frame_rate') if stream else None

    def get_bitrate(self) -> Optional[int]:
        """Get video bitrate in bits per second.
        
        Returns:
            Bitrate in bps, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None
        
        bitrate = stream.get('bit_rate')
        return int(bitrate) if bitrate else None
