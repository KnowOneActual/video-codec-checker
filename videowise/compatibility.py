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
    
    SUPPORTED_CODECS = {
        'h264', 'prores', 'dnxhd', 'dnxhr', 'mpeg2video', 'mjpeg',
    }
    
    RECOMMENDED_CONTAINERS = {
        'h264': ['mp4', 'mov'],
        'prores': ['mov'],
        'dnxhd': ['mov', 'mxf'],
        'dnxhr': ['mov', 'mxf'],
    }
    
    def __init__(self, version: str = "2.3"):
        self.version = version
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        frame_rate = video_info.get('frame_rate')
        
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
            return issues
        
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
        
        if frame_rate and '/' in str(frame_rate):
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Ensure video uses constant frame rate (CFR)",
                reason="Variable frame rate (VFR) can cause timing and sync issues in live production",
                suggestion="Convert to constant frame rate matching your production frame rate"
            ))
        
        if not issues:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"Video is compatible with CasparCG {self.version}",
            ))
        
        return issues


class VmixChecker(CompatibilityChecker):
    """Compatibility checker for vMix."""
    
    HIGH_BITRATE_THRESHOLD = 100_000_000  # 100 Mbps
    VERY_HIGH_BITRATE_THRESHOLD = 200_000_000  # 200 Mbps
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        bitrate = video_info.get('bitrate')
        codec = video_info.get('codec', '').lower()
        resolution = video_info.get('resolution')
        
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
        
        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="4K video requires powerful hardware for smooth playback",
                    reason="4K playback is CPU/GPU intensive",
                    suggestion="Ensure your system meets vMix's 4K requirements"
                ))
        
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


class OBSChecker(CompatibilityChecker):
    """Compatibility checker for OBS Studio."""
    
    SUPPORTED_CODECS = {
        'h264', 'hevc', 'av1', 'vp8', 'vp9', 'prores', 'dnxhd',
    }
    
    RECOMMENDED_CODECS = ['h264', 'hevc', 'av1']
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        
        if codec not in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"{codec.upper()} may have limited support in OBS Studio",
                reason="OBS works best with H.264, HEVC, and AV1",
                suggestion="Consider converting to H.264 for maximum compatibility"
            ))
        
        if codec in self.RECOMMENDED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is fully supported by OBS Studio",
                reason="Hardware acceleration may be available"
            ))
        
        # Check for MKV/Matroska container (OBS default)
        if 'matroska' in container or 'mkv' in container or 'webm' in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="MKV/Matroska is OBS's default format and supports all codecs",
            ))
        elif 'mp4' in container or 'mov' in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="MP4/MOV containers work well with OBS",
                reason="Good compatibility with video editing software"
            ))
        
        if not issues:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="Video should work with OBS Studio",
            ))
        
        return issues


class QLabChecker(CompatibilityChecker):
    """Compatibility checker for QLab."""
    
    # QLab 5 recommended codecs in order of preference
    RECOMMENDED_CODECS = ['prores_proxy', 'prores_lt', 'prores', 'h264']
    ALPHA_CODECS = ['prores4444']  # For transparency
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        
        # Check for ProRes (best performance)
        if 'prores' in codec:
            if 'proxy' in codec or 'lt' in codec:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} provides best performance in QLab",
                    reason="ProRes Proxy and LT are optimized for playback performance"
                ))
            elif '4444' in codec:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes 4444 supports alpha channel (transparency) in QLab",
                    reason="Required for videos with transparency"
                ))
            else:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is compatible with QLab",
                ))
        elif codec == 'h264':
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="H.264 works but performs poorly when scrubbing or changing speed",
                reason="H.264 is not optimized for variable-speed playback",
                suggestion="Convert to ProRes 422 Proxy or LT for better performance"
            ))
        else:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"{codec.upper()} may not perform well in QLab",
                reason="QLab works best with ProRes codecs",
                suggestion="Convert to ProRes 422 Proxy for optimal performance"
            ))
        
        # Check container
        if 'mov' not in container and 'mp4' not in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="QLab works best with MOV or MP4 containers",
                suggestion="Remux to MOV container"
            ))
        
        return issues


class ProPresenterChecker(CompatibilityChecker):
    """Compatibility checker for ProPresenter."""
    
    SUPPORTED_CODECS = {
        'h264', 'hevc', 'prores', 'prores4444', 'hap',
    }
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        
        # Check if codec contains any of the supported codec names
        codec_supported = any(supported in codec for supported in self.SUPPORTED_CODECS)
        
        if not codec_supported:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message=f"ProPresenter does not support {codec.upper()} codec",
                reason=f"Supported codecs: {', '.join(sorted(self.SUPPORTED_CODECS))}",
                suggestion="Convert to H.264, ProRes, or HAP codec"
            ))
            return issues
        
        if 'hap' in codec:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="HAP codec provides best performance in ProPresenter",
                reason="HAP is GPU-accelerated and designed for real-time playback"
            ))
        elif 'prores' in codec:
            if '4444' in codec:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes 4444 supports alpha channel (transparency)",
                ))
            else:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes is fully supported by ProPresenter",
                ))
        elif codec == 'h264':
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="H.264 is compatible with ProPresenter",
            ))
        
        if 'mov' not in container and 'mp4' not in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="ProPresenter works best with MOV or MP4 containers",
            ))
        
        return issues


class SafariChecker(CompatibilityChecker):
    """Compatibility checker for Safari browser."""
    
    SUPPORTED_CODECS = ['h264', 'hevc']
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        
        if codec not in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message=f"Safari does not support {codec.upper()} codec",
                reason="Safari only supports H.264 and HEVC (H.265)",
                suggestion="Convert to H.264 for maximum browser compatibility"
            ))
            return issues
        
        if 'mp4' not in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Safari works best with MP4 container format",
                suggestion="Remux to MP4 container"
            ))
        
        issues.append(CompatibilityIssue(
            level=CompatibilityLevel.COMPATIBLE,
            message=f"{codec.upper()} is supported by Safari",
        ))
        
        return issues


class ChromeChecker(CompatibilityChecker):
    """Compatibility checker for Chrome browser."""
    
    SUPPORTED_CODECS = ['h264', 'vp8', 'vp9', 'av1']
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        
        if codec in self.SUPPORTED_CODECS:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is supported by Chrome",
            ))
        else:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"{codec.upper()} may not be supported by Chrome",
                reason="Chrome supports H.264, VP8, VP9, and AV1",
                suggestion="Convert to H.264 or VP9 for web compatibility"
            ))
        
        return issues


class InstagramChecker(CompatibilityChecker):
    """Compatibility checker for Instagram."""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for feed posts
    MAX_DURATION = 60  # 60 seconds for feed, 90 for reels
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        profile = video_info.get('profile', '').lower()
        resolution = video_info.get('resolution')
        
        # Instagram prefers H.264 Baseline
        if codec != 'h264':
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"Instagram will re-encode {codec.upper()} to H.264 (quality loss)",
                reason="Instagram only accepts H.264 codec",
                suggestion="Pre-encode to H.264 to maintain quality control"
            ))
        elif profile and 'baseline' not in profile:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"Instagram prefers H.264 Baseline Profile, not {profile}",
                reason="Non-Baseline profiles will be re-encoded (quality loss)",
                suggestion="Convert to H.264 Baseline Profile: ffmpeg -profile:v baseline -level 3.0"
            ))
        else:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="Video codec is optimized for Instagram",
            ))
        
        # Check resolution (1080p recommended)
        if resolution:
            width, height = resolution
            if width > 1080 or height > 1920:
                issues.append(CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Resolution {width}x{height} will be downscaled to 1080p",
                    reason="Instagram maximum resolution is 1080x1920 for vertical video",
                    suggestion="Downscale to 1080p before upload to control quality"
                ))
        
        return issues


class TwitterChecker(CompatibilityChecker):
    """Compatibility checker for Twitter/X."""
    
    MAX_FILE_SIZE_STANDARD = 512 * 1024 * 1024  # 512MB
    MAX_FILE_SIZE_PREMIUM = 8 * 1024 * 1024 * 1024  # 8GB
    MAX_DURATION_STANDARD = 140  # seconds
    
    def __init__(self, account_type: str = "standard"):
        self.account_type = account_type
    
    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        issues = []
        codec = video_info.get('codec', '').lower()
        container = video_info.get('container', '').lower()
        file_size = video_info.get('file_size', 0)
        
        # Check codec (H.264 High Profile recommended)
        if codec != 'h264':
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message=f"Twitter recommends H.264 codec, not {codec.upper()}",
                suggestion="Convert to H.264 High Profile for best quality"
            ))
        else:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message="H.264 codec is supported by Twitter",
            ))
        
        # Check container
        if 'mp4' not in container and 'mov' not in container:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Twitter works best with MP4 or MOV containers",
                suggestion="Remux to MP4 container"
            ))
        
        # Check file size
        max_size = self.MAX_FILE_SIZE_PREMIUM if self.account_type == "premium" else self.MAX_FILE_SIZE_STANDARD
        if file_size > max_size:
            issues.append(CompatibilityIssue(
                level=CompatibilityLevel.INCOMPATIBLE,
                message=f"File size {file_size // (1024*1024)}MB exceeds Twitter limit of {max_size // (1024*1024)}MB",
                reason=f"Twitter {self.account_type} accounts have file size limits",
                suggestion="Compress video or upgrade to Premium account"
            ))
        
        return issues


def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility for a specific system.
    
    Args:
        video_info: Dictionary containing video metadata
        system: System to check compatibility for
        
    Returns:
        List of compatibility issues
    """
    checkers = {
        'casparcg': CasparCGChecker,
        'vmix': VmixChecker,
        'obs': OBSChecker,
        'qlab': QLabChecker,
        'propresenter': ProPresenterChecker,
        'safari': SafariChecker,
        'chrome': ChromeChecker,
        'instagram': InstagramChecker,
        'twitter': TwitterChecker,
    }
    
    system_lower = system.lower()
    if system_lower not in checkers:
        return [CompatibilityIssue(
            level=CompatibilityLevel.UNKNOWN,
            message=f"Unknown system: {system}",
            reason=f"Supported systems: {', '.join(sorted(checkers.keys()))}"
        )]
    
    checker = checkers[system_lower]()
    return checker.check(video_info)
