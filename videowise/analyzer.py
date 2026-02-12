"""Video file analysis and metadata extraction using FFprobe."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class VideoAnalyzer:
    """Analyzes video files using ffprobe to extract metadata."""

    def __init__(self, file_path: str):
        """Initialize analyzer with a video file path.

        Args:
            file_path: Path to the video file to analyze

        Raises:
            FileNotFoundError: If the video file does not exist
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        self._metadata: Optional[Dict[str, Any]] = None

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Extract video metadata using ffprobe.

        Returns:
            Dictionary containing video metadata, or None if extraction failed
        """
        if self._metadata is not None:
            return self._metadata

        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(self.file_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            self._metadata = json.loads(result.stdout)
            return self._metadata

        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return None

    def get_video_stream(self) -> Optional[Dict[str, Any]]:
        """Get the first video stream from metadata.

        Returns:
            Dictionary containing video stream data, or None if not found
        """
        metadata = self.get_metadata()
        if not metadata:
            return None

        streams = metadata.get("streams", [])
        for stream in streams:
            if stream.get("codec_type") == "video":
                return stream

        return None

    def get_codec_name(self) -> Optional[str]:
        """Get the codec name from the video stream.

        Returns:
            Codec name as string, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None
        return stream.get("codec_name")

    def get_codec_profile(self) -> Optional[str]:
        """Get the codec profile from the video stream.

        Returns:
            Codec profile as string, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None
        return stream.get("profile")

    def get_container_format(self) -> Optional[str]:
        """Get the container format from metadata.

        Returns:
            Container format as string, or None if not found
        """
        metadata = self.get_metadata()
        if not metadata:
            return None

        format_info = metadata.get("format", {})
        return format_info.get("format_name")

    def get_resolution(self) -> Optional[tuple[int, int]]:
        """Get video resolution as (width, height).

        Returns:
            Tuple of (width, height), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        width = stream.get("width")
        height = stream.get("height")

        if width and height:
            return (int(width), int(height))

        return None

    def get_frame_rate(self) -> Optional[str]:
        """Get the frame rate of the video.

        Returns:
            Frame rate as string (e.g., '30/1', '29.97'), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None
        return stream.get("r_frame_rate")

    def get_bitrate(self) -> Optional[int]:
        """Get the video bitrate in bits per second.

        Returns:
            Bitrate as integer, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        bitrate = stream.get("bit_rate")
        if bitrate:
            return int(bitrate)

        # If stream bitrate is not available, try format bitrate
        metadata = self.get_metadata()
        if metadata:
            format_info = metadata.get("format", {})
            bitrate = format_info.get("bit_rate")
            if bitrate:
                return int(bitrate)

        return None

    def get_file_size(self) -> int:
        """Get the file size in bytes.

        Returns:
            File size in bytes
        """
        return self.file_path.stat().st_size
