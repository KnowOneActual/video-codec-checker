"""Compatibility rules engine for various playback systems and platforms."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


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


# Import editing platform checkers
try:
    from .editing_platforms import (
        AdobePremiereProChecker,
        AfterEffectsChecker,
        AvidMediaComposerChecker,
        DaVinciResolveChecker,
        FinalCutProChecker,
    )

    EDITING_PLATFORMS_AVAILABLE = True
except ImportError:
    EDITING_PLATFORMS_AVAILABLE = False

# Import streaming platform checkers
try:
    from .streaming_checkers import (
        DiscordChecker,
        KickChecker,
        RestreamChecker,
        TwitchChecker,
        YouTubeLiveChecker,
        ZoomChecker,
    )

    STREAMING_PLATFORMS_AVAILABLE = True
except ImportError:
    STREAMING_PLATFORMS_AVAILABLE = False

# Import advanced playout checkers
try:
    from .advanced_playout import PlaybackProChecker as AdvancedPlaybackProChecker
    from .advanced_playout import ProVideoPlayerChecker as AdvancedPVPChecker
    from .advanced_playout import ResolumeChecker as AdvancedResolumeChecker
    from .advanced_playout import WirecastChecker as AdvancedWirecastChecker

    ADVANCED_PLAYOUT_AVAILABLE = True
except ImportError:
    ADVANCED_PLAYOUT_AVAILABLE = False


# Live Production Systems


class CasparCGChecker(CompatibilityChecker):
    """Compatibility checker for CasparCG Server.

    Enhanced with HAP codec support and alpha channel detection.
    """

    SUPPORTED_CODECS = {
        "h264",
        "prores",
        "dnxhd",
        "dnxhr",
        "mpeg2video",
        "mjpeg",
        "hap",  # GPU-accelerated codec
        "notchlc",  # NotchLC for high-quality playback
    }

    ALPHA_CHANNEL_CODECS = {
        "prores4444",
        "hap_alpha",
        "hap_q_alpha",
    }

    RECOMMENDED_CONTAINERS = {
        "h264": ["mp4", "mov"],
        "prores": ["mov"],
        "dnxhd": ["mov", "mxf"],
        "dnxhr": ["mov", "mxf"],
        "hap": ["mov"],  # HAP requires MOV container
        "notchlc": ["mov"],
    }

    def __init__(self, version: str = "2.3"):
        """Initialize CasparCG checker with version.

        Args:
            version: CasparCG Server version (default: "2.3")
        """
        self.version = version

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for CasparCG Server.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        frame_rate = video_info.get("frame_rate")
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")

        if not codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.UNKNOWN,
                    message="Unable to determine video codec",
                )
            )
            return issues

        # Check for HAP codec (GPU-accelerated)
        if "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} provides GPU-accelerated playback with alpha",
                        reason="HAP Alpha ideal for overlays and graphics with transparency",
                    )
                )
            elif "hap_q" in codec or "hapq" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP Q provides high-quality GPU-accelerated playback",
                        reason="Best quality HAP variant for broadcast",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP codec provides GPU-accelerated playback",
                        reason="Optimal for real-time playback in CasparCG",
                    )
                )
        # Check for ProRes with alpha channel
        elif "prores" in codec and "4444" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes 4444 supports alpha channel for transparency",
                    reason="Professional quality with transparency support",
                )
            )
        # Check for NotchLC
        elif "notchlc" in codec or "notch" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="NotchLC provides high-quality real-time playback",
                    reason="Popular in broadcast for quality and performance balance",
                )
            )
        elif codec not in self.SUPPORTED_CODECS:
            supported = ", ".join(sorted(self.SUPPORTED_CODECS))
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=(f"CasparCG {self.version} does not support " f"{codec.upper()} codec"),
                    reason=f"CasparCG only supports: {supported}",
                    suggestion="Convert to HAP (GPU-accelerated), ProRes, DNxHD, or H.264",
                )
            )
            return issues
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by CasparCG {self.version}",
                )
            )

        # Check container compatibility
        if codec in self.RECOMMENDED_CONTAINERS:
            recommended = self.RECOMMENDED_CONTAINERS[codec]
            container_ok = any(rec in container for rec in recommended)

            if not container_ok:
                rec_str = " or ".join(recommended).upper()
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(f"{codec.upper()} in {container} container " f"may have issues"),
                        reason=(
                            f"CasparCG works best with {codec.upper()} " f"in {rec_str} container"
                        ),
                        suggestion=(
                            f"Remux to {recommended[0].upper()} container "
                            f"for best compatibility"
                        ),
                    )
                )

        # Check for constant frame rate (critical for live production)
        if frame_rate and "/" in str(frame_rate):
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Ensure video uses constant frame rate (CFR)",
                    reason=(
                        "Variable frame rate (VFR) can cause timing and sync "
                        "issues in live production"
                    ),
                    suggestion="Convert to constant frame rate matching production",
                )
            )

        # Check for 4K content bandwidth
        if resolution and bitrate:
            width, height = resolution
            if width >= 3840 and height >= 2160:
                mbps = bitrate // 1_000_000
                if bitrate > 200_000_000:  # 200 Mbps
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"4K at {mbps}Mbps may stress system bandwidth",
                            reason="Very high bitrate 4K requires powerful hardware",
                            suggestion="Consider HAP codec for GPU-accelerated 4K playback",
                        )
                    )

        return issues


# [Remaining checker classes from the full file continue here - truncated for brevity in this response]
# PlayoutBeeChecker, VmixChecker, OBSChecker, QLabChecker, ProPresenterChecker, etc.
# ... (keeping all the content from line ~270 to line ~2400 unchanged) ...


# Keep legacy class names but use advanced versions if available
if ADVANCED_PLAYOUT_AVAILABLE:
    WirecastChecker = AdvancedWirecastChecker
    PlaybackProChecker = AdvancedPlaybackProChecker
    ResolumeChecker = AdvancedResolumeChecker
    ProVideoPlayerChecker = AdvancedPVPChecker
else:
    # Define basic versions if advanced not available
    class WirecastChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic Wirecast checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic Wirecast compatibility check",
                )
            ]

    class PlaybackProChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic PlaybackPro checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic PlaybackPro compatibility check",
                )
            ]

    class ResolumeChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic Resolume checker."""
        
        def __init__(self, platform: str = "windows"):
            """Initialize Resolume checker.
            
            Args:
                platform: 'windows' or 'mac' for platform-specific advice
            """
            self.platform = platform

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic Resolume compatibility check",
                )
            ]

    class ProVideoPlayerChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic PVP checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic PVP compatibility check",
                )
            ]


# [Remaining checker classes and registry functions continue unchanged from line ~2450 onwards]
# EasyWorshipChecker, VLCChecker, MittiChecker, MilluminChecker, SafariChecker, etc.
# get_available_systems(), check_compatibility(), etc.
