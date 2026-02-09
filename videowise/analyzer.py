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

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Extract video metadata using ffprobe.
        
        Returns:
            Dictionary containing video metadata, or None if extraction fails
        """
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
            
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
            return None
