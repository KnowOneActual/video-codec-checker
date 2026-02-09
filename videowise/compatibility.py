"""Compatibility rules engine for various playback systems and platforms."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CompatibilityLevel(Enum):
    """Compatibility status levels."""
    COMPATIBLE = "compatible"
    WARNING = "warning"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue or warning."""
    level: CompatibilityLevel
    message: str
    reason: Optional[str] = None
    suggestion: Optional[str] = None


class CompatibilityChecker:
    """Base class for compatibility checking."""
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check compatibility and return list of issues.
        
        Args:
            video_info: Dictionary containing video metadata
            
        Returns:
            List of compatibility issues
        """
        raise NotImplementedError


class CasparCGChecker(CompatibilityChecker):
    """Compatibility checker for CasparCG Server."""
    
    # Supported codecs by CasparCG
    SUPPORTED_CODECS = {
        'h264',      # H.264
        'prores',    # Apple ProRes
        'dnxhd',     # Avid DNxHD
        'dnxhr',     # Avid DNxHR
        'mpeg2video', # MPEG-2
        'mjpeg',     # Motion JPEG
    }
    
    # Recommended containers for each codec
    RECOMMENDED_CONTAINERS = {
        'h264': ['mp4', 'mov'],
        'prores': ['mov'],
        'dnxhd': ['mov', 'mxf'],
        'dnxhr': ['mov', 'mxf'],
    }
    
    def __init__(self, version: str = "2.3"):
        """Initialize CasparCG checker.
        
        Args:
            version: CasparCG version (e.g., '2.3', '2.2')
        """
        self.version = version
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check CasparCG compatibility.
        
        Args:
            video_info: Dictionary with keys: codec, profile, container, 
                       resolution, frame_rate, bitrate
            
        Returns:
            List of compatibility issues
        """
        issues = []
        
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        frame_rate = video_info.get('frame_rate')
        
        # Check codec support
        if not codec:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.UNKNOWN,
                message="Unable to determine video codec",
            ))
        elif codec not in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message=f"CasparCG {self.version} does not support {codec.upper()} codec",
                reason=f"CasparCG only supports: {', '.join(sorted(self.SUPPORTED_CODECS))}",
                suggestion="Convert to ProRes, DNxHD, or H.264 in MP4 container"
            ))
            return issues  # No point checking further if codec is incompatible
        
        # Check container format for supported codecs
        if codec in self.RECOMMENDED_CONTAINERS:
            recommended = self.RECOMMENDED_CONTAINERS[codec]
            container_ok = any(rec in container for rec in recommended)
            
            if not container_ok:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} in {container} container may have issues",
                    reason=f"CasparCG works best with {codec.upper()} in {' or '.join(recommended).upper()} container",
                    suggestion=f"Remux to {recommended[0].upper()} container for best compatibility"
                ))
        
        # Check for variable frame rate (VFR)
        if frame_rate and '/' in str(frame_rate):
            # Check if it's not a standard constant frame rate
            # This is a simplified check - in reality you'd parse the fraction
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Ensure video uses constant frame rate (CFR)",
                reason="Variable frame rate (VFR) can cause timing and sync issues in live production",
                suggestion="Convert to constant frame rate matching your production frame rate"
            ))
        
        # If no issues found, return compatible status
        if not issues:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"Video is compatible with CasparCG {self.version}",
            ))
        
        return issues


class VmixChecker(CompatibilityChecker):
    """Compatibility checker for vMix."""
    
    # vMix is more forgiving but has performance considerations
    HIGH_BITRATE_THRESHOLD = 100_000_000  # 100 Mbps
    VERY_HIGH_BITRATE_THRESHOLD = 200_000_000  # 200 Mbps
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check vMix compatibility.
        
        Args:
            video_info: Dictionary with video metadata
            
        Returns:
            List of compatibility issues
        """
        issues = []
        
        bitrate = video_info.get('bitrate')
        codec = video_info.get('codec', '').lower()
        resolution = video_info.get('resolution')
        
        # Check bitrate performance
        if bitrate:
            if bitrate > self.VERY_HIGH_BITRATE_THRESHOLD:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Very high bitrate ({bitrate // 1_000_000}Mbps) may cause dropped frames",
                    reason="vMix may struggle with extremely high bitrate files on some systems",
                    suggestion="Consider transcoding to 100-150Mbps for smoother playback"
                ))
            elif bitrate > self.HIGH_BITRATE_THRESHOLD:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"High bitrate ({bitrate // 1_000_000}Mbps) - monitor for performance issues",
                    reason="High bitrate files require more system resources",
                    suggestion="Test playback before going live"
                ))
        
        # Check for high resolution
        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:  # 4K
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="4K video requires powerful hardware for smooth playback",
                    reason="4K playback is CPU/GPU intensive",
                    suggestion="Ensure your system meets vMix's 4K requirements"
                ))
        
        # vMix supports most codecs, but some are better than others
        if codec in ['prores', 'dnxhd', 'dnxhr']:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is well-supported by vMix",
            ))
        elif codec == 'h264':
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="H.264 is supported by vMix",
                reason="Hardware acceleration available for H.264",
            ))
        
        if not issues:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="Video should be compatible with vMix",
            ))
        
        return issues


def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility for a specific system.
    
    Args:
        video_info: Dictionary containing video metadata
        system: System to check compatibility for ('casparcg', 'vmix', etc.)
        
    Returns:
        List of compatibility issues
    """
    checkers = {
        'casparcg': CasparCGChecker,
        'vmix': VmixChecker,
    }
    
    system_lower = system.lower()
    if system_lower not in checkers:
        return [CompatibilityIssue(
            level=CompatibilityLevel.UNKNOWN,
            message=f"Unknown system: {system}",
            reason=f"Supported systems: {', '.join(checkers.keys())}"
        )]
    
    checker = checkers[system_lower]()
    return checker.check(video_info)
