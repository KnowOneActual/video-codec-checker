"""Video file analyzer using ffprobe."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class VideoAnalyzer:
    """Analyzes video files and extracts codec/format information."""

    def __init__(self, file_path: str) -> None:
        """Initialize analyzer with a video file path.

        Args:
            file_path: Path to the video file to analyze

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        self._metadata: Optional[Dict[str, Any]] = None

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Extract video metadata using ffprobe.

        Returns:
            Dictionary containing video metadata, or None if extraction fails
        """
        if self._metadata is not None:
            return self._metadata

        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    str(self.file_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            self._metadata = json.loads(result.stdout)
            return self._metadata  # type: ignore[no-any-return]

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
                return stream  # type: ignore[no-any-return]

        return None

    def get_codec_name(self) -> Optional[str]:
        """Extract the video codec name.

        Returns:
            Codec name (e.g., 'h264', 'prores'), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        return stream.get("codec_name")

    def get_codec_profile(self) -> Optional[str]:
        """Extract the codec profile if available.

        Returns:
            Profile name (e.g., 'High', 'Baseline'), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        return stream.get("profile")  # type: ignore[no-any-return]

    def get_container_format(self) -> Optional[str]:
        """Extract the container format.

        Returns:
            Format name (e.g., 'mp4', 'mov'), or None if not found
        """
        metadata = self.get_metadata()
        if not metadata:
            return None

        format_data = metadata.get("format", {})
        format_name = format_data.get("format_name", "")

        # Return first format if multiple are listed
        if "," in format_name:
            return format_name.split(",")[0]  # type: ignore[no-any-return]

        return format_name if format_name else None

    def get_resolution(self) -> Optional[Tuple[int, int]]:
        """Extract video resolution (width, height).

        Returns:
            Tuple of (width, height), or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        width = stream.get("width")
        height = stream.get("height")

        if width is not None and height is not None:
            return (int(width), int(height))

        return None

    def get_frame_rate(self) -> Optional[float]:
        """Extract frame rate in fps.

        Returns:
            Frame rate as float, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        # Try avg_frame_rate first (more accurate)
        fps_str = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
        if not fps_str:
            return None

        try:
            # Handle fraction format (e.g., "25/1", "30000/1001")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                return float(num) / float(den)
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return None

    def get_bitrate(self) -> Optional[int]:
        """Extract video bitrate in bits per second.

        Returns:
            Bitrate as integer, or None if not found
        """
        stream = self.get_video_stream()
        if not stream:
            return None

        bitrate_str = stream.get("bit_rate")
        if bitrate_str:
            try:
                return int(bitrate_str)
            except ValueError:
                return None

        # Fallback to format bitrate
        metadata = self.get_metadata()
        if not metadata:
            return None

        format_data = metadata.get("format", {})
        bitrate_str = format_data.get("bit_rate")
        if bitrate_str:
            try:
                return int(bitrate_str)
            except ValueError:
                return None

        return None

    def get_file_size(self) -> int:
        """Get file size in bytes.

        Returns:
            File size in bytes
        """
        return os.path.getsize(self.file_path)
