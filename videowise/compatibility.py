"""Compatibility rules engine for various playback systems and platforms.

This module provides the compatibility checking interface. The primary implementation
uses the rule-based engine (RuleEngine) which loads system definitions from YAML.

Legacy hardcoded checker classes are preserved for backward compatibility and
can still be imported and used directly if needed.
"""

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


# Import editing platform checkers (for backward compatibility)
try:
    from .editing_platforms import (  # noqa: F401
        AdobePremiereProChecker,
        AfterEffectsChecker,
        AvidMediaComposerChecker,
        DaVinciResolveChecker,
        FinalCutProChecker,
    )

    EDITING_PLATFORMS_AVAILABLE = True
except ImportError:
    EDITING_PLATFORMS_AVAILABLE = False

# Import streaming platform checkers (for backward compatibility)
try:
    from .streaming_checkers import (  # noqa: F401
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


# ============================================================================
# LEGACY CHECKER CLASSES (Preserved for Backward Compatibility)
# ============================================================================
# These classes remain functional and are used by existing tests.
# The primary API (check_compatibility function below) uses the rule engine,
# but these classes can still be imported and used directly.
# ============================================================================


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


class PlayoutBeeChecker(CompatibilityChecker):
    """Compatibility checker for PlayoutBee playout software.

    PlayoutBee is a broadcast-grade playout solution for Windows, macOS,
    and Raspberry Pi with integration for ATEM, OBS, vMix, and NDI workflows.
    """

    SUPPORTED_CODECS = {
        "h264",
        "prores",
        "hap",  # Optimal for GPU acceleration
    }

    HAP_VARIANTS = {
        "hap",  # Standard HAP
        "hap_alpha",  # HAP with alpha channel
        "hap_q",  # HAP high quality
        "hap_q_alpha",  # HAP high quality with alpha
    }

    ALPHA_CODECS = {
        "prores4444",
        "hap_alpha",
        "hap_q_alpha",
    }

    def __init__(self, platform: str = "desktop"):
        """Initialize PlayoutBee checker.

        Args:
            platform: 'desktop' (Windows/Mac) or 'raspberrypi' for Pi deployments
        """
        self.platform = platform

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")

        # Check for HAP codec (optimal for PlayoutBee)
        if "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is optimal for PlayoutBee with transparency",
                        reason="GPU-accelerated playback with alpha channel support",
                    )
                )
            elif "hap_q" in codec or "hapq" in codec:
                if self.platform == "raspberrypi":
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message="HAP Q may be demanding on Raspberry Pi",
                            reason="HAP Q has higher data rates than standard HAP",
                            suggestion="Use standard HAP for Raspberry Pi deployments",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message="HAP Q provides high-quality GPU-accelerated playback",
                            reason="Best quality for desktop playout systems",
                        )
                    )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP codec is optimal for PlayoutBee",
                        reason="GPU-accelerated real-time playback with low CPU usage",
                    )
                )

            # HAP requires MOV container
            if "mov" not in container:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="HAP codec requires MOV container",
                        suggestion="Remux to MOV container for HAP codec",
                    )
                )
        # Check for H.264
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is compatible with PlayoutBee",
                    reason="Hardware acceleration available, good compatibility",
                )
            )

            # Warn about high bitrate H.264 on Raspberry Pi
            if self.platform == "raspberrypi" and bitrate and bitrate > 50_000_000:
                mbps = bitrate // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"H.264 at {mbps}Mbps may be demanding on Raspberry Pi",
                        reason="Raspberry Pi has limited decode bandwidth",
                        suggestion="Keep H.264 bitrate under 50 Mbps for Pi, or use HAP codec",
                    )
                )
        # Check for ProRes
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 supports alpha channel workflows",
                        reason="Professional quality with transparency support",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is supported by PlayoutBee",
                        reason="Professional codec with good quality",
                    )
                )

            # ProRes on Raspberry Pi warning
            if self.platform == "raspberrypi":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="ProRes is very demanding on Raspberry Pi",
                        reason="High data rates exceed Pi's capabilities",
                        suggestion="Convert to HAP codec for Raspberry Pi deployments",
                    )
                )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not be optimal for PlayoutBee",
                    reason="PlayoutBee works best with HAP, H.264, or ProRes",
                    suggestion="Convert to HAP for GPU acceleration or H.264 for compatibility",
                )
            )

        # Check container format
        if "mov" in container or "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is supported by PlayoutBee",
                )
            )

        # Check resolution for Raspberry Pi
        if self.platform == "raspberrypi" and resolution:
            width, height = resolution
            if width > 1920 or height > 1080:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} may be too high for Raspberry Pi",
                        reason="Pi works best with 1080p or lower",
                        suggestion="Use 1080p for reliable playback on Raspberry Pi",
                    )
                )

        return issues


class VmixChecker(CompatibilityChecker):
    """Compatibility checker for vMix."""

    HIGH_BITRATE_THRESHOLD = 100_000_000  # 100 Mbps
    VERY_HIGH_BITRATE_THRESHOLD = 200_000_000  # 200 Mbps

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        bitrate = video_info.get("bitrate")
        codec = video_info.get("codec", "").lower()
        resolution = video_info.get("resolution")

        if bitrate:
            if bitrate > self.VERY_HIGH_BITRATE_THRESHOLD:
                mbps = bitrate // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(f"Very high bitrate ({mbps}Mbps) may cause " f"dropped frames"),
                        reason="vMix may struggle with high bitrate on some systems",
                        suggestion="Consider transcoding to 100-150Mbps",
                    )
                )
            elif bitrate > self.HIGH_BITRATE_THRESHOLD:
                mbps = bitrate // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(f"High bitrate ({mbps}Mbps) - monitor for " f"performance issues"),
                        reason="High bitrate files require more resources",
                        suggestion="Test playback before going live",
                    )
                )

        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="4K video requires powerful hardware for smooth playback",
                        reason="4K playback is CPU/GPU intensive",
                        suggestion="Ensure your system meets vMix's 4K requirements",
                    )
                )

        if codec in ["prores", "dnxhd", "dnxhr"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is well-supported by vMix",
                )
            )
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is supported by vMix",
                    reason="Hardware acceleration available for H.264",
                )
            )

        if not issues:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Video should be compatible with vMix",
                )
            )

        return issues


class OBSChecker(CompatibilityChecker):
    """Compatibility checker for OBS Studio."""

    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "av1",
        "vp8",
        "vp9",
        "prores",
        "dnxhd",
    }

    RECOMMENDED_CODECS = ["h264", "hevc", "av1"]

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        if codec not in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may have limited support in OBS",
                    reason="OBS works best with H.264, HEVC, and AV1",
                    suggestion="Consider converting to H.264 for compatibility",
                )
            )

        if codec in self.RECOMMENDED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is fully supported by OBS Studio",
                    reason="Hardware acceleration may be available",
                )
            )

        # Check for MKV/Matroska container (OBS default)
        if "matroska" in container or "mkv" in container or "webm" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MKV/Matroska is OBS's default format",
                )
            )
        elif "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4/MOV containers work well with OBS",
                    reason="Good compatibility with video editing software",
                )
            )

        if not issues:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Video should work with OBS Studio",
                )
            )

        return issues


class QLabChecker(CompatibilityChecker):
    """Compatibility checker for QLab."""

    # QLab 5 recommended codecs in order of preference
    RECOMMENDED_CODECS = ["prores_proxy", "prores_lt", "prores", "h264"]
    ALPHA_CODECS = ["prores4444"]  # For transparency

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check for ProRes (best performance)
        if "prores" in codec:
            if "proxy" in codec or "lt" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} provides best performance in QLab",
                        reason="ProRes Proxy and LT optimize for playback",
                    )
                )
            elif "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 supports alpha channel (transparency)",
                        reason="Required for videos with transparency",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is compatible with QLab",
                    )
                )
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="H.264 performs poorly when scrubbing or changing speed",
                    reason="H.264 is not optimized for variable-speed playback",
                    suggestion="Convert to ProRes 422 Proxy or LT",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not perform well in QLab",
                    reason="QLab works best with ProRes codecs",
                    suggestion="Convert to ProRes 422 Proxy for optimal performance",
                )
            )

        # Check container
        if "mov" not in container and "mp4" not in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="QLab works best with MOV or MP4 containers",
                    suggestion="Remux to MOV container",
                )
            )

        return issues


class ProPresenterChecker(CompatibilityChecker):
    """Compatibility checker for ProPresenter."""

    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "prores4444",
        "hap",
    }

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check if codec contains any of the supported codec names
        codec_supported = any(supported in codec for supported in self.SUPPORTED_CODECS)

        if not codec_supported:
            supported = ", ".join(sorted(self.SUPPORTED_CODECS))
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"ProPresenter does not support {codec.upper()} codec",
                    reason=f"Supported codecs: {supported}",
                    suggestion="Convert to H.264, ProRes, or HAP codec",
                )
            )
            return issues

        if "hap" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="HAP codec provides best performance in ProPresenter",
                    reason="HAP is GPU-accelerated for real-time playback",
                )
            )
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 supports alpha channel",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes is fully supported by ProPresenter",
                    )
                )
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is compatible with ProPresenter",
                )
            )

        if "mov" not in container and "mp4" not in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="ProPresenter works best with MOV or MP4 containers",
                )
            )

        return issues


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
            """Check video compatibility for Wirecast.

            Args:
                video_info: Dictionary containing video metadata

            Returns:
                List of compatibility issues
            """
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic Wirecast compatibility check",
                )
            ]

    class PlaybackProChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic PlaybackPro checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            """Check video compatibility for PlaybackPro.

            Args:
                video_info: Dictionary containing video metadata

            Returns:
                List of compatibility issues
            """
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic PlaybackPro compatibility check",
                )
            ]

    class ResolumeChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic Resolume checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            """Check video compatibility for Resolume.

            Args:
                video_info: Dictionary containing video metadata

            Returns:
                List of compatibility issues
            """
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic Resolume compatibility check",
                )
            ]

    class ProVideoPlayerChecker(CompatibilityChecker):  # type: ignore[no-redef]
        """Basic PVP checker."""

        def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
            """Check video compatibility for ProVideoPlayer.

            Args:
                video_info: Dictionary containing video metadata

            Returns:
                List of compatibility issues
            """
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Basic PVP compatibility check",
                )
            ]


class EasyWorshipChecker(CompatibilityChecker):
    """Compatibility checker for EasyWorship church presentation software.

    EasyWorship is popular church presentation software (Windows only).
    EasyWorship 7+ has improved codec support over earlier versions.
    """

    # EasyWorship 7+ built-in support (no codec packs needed)
    NATIVE_CODECS = ["h264"]

    # Also works with Windows Media codecs
    WINDOWS_CODECS = ["wmv", "mpeg2video"]

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check for native support (H.264 in MP4/MOV)
        if codec == "h264":
            if "mp4" in container or "mov" in container or "m4v" in container:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 in MP4/MOV has native support in EasyWorship 7+",
                        reason="No additional codecs required",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 is supported by EasyWorship",
                        reason="H.264 works in most containers",
                    )
                )
        # Check for Windows Media codecs
        elif codec in self.WINDOWS_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported on Windows",
                    reason="Windows Media codecs built into Windows OS",
                )
            )
        # Other codecs may require additional codec packs
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may require additional codecs",
                    reason="EasyWorship 7+ natively supports H.264 in MP4/MOV",
                    suggestion="Convert to H.264 in MP4 for guaranteed compatibility",
                )
            )

        # Check container formats
        if "mp4" in container or "mov" in container or "m4v" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container has native support",
                    reason="MP4, MOV, and M4V work without additional software",
                )
            )
        elif "wmv" in container or "avi" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} is supported on Windows",
                    reason="Windows Media formats built into Windows",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{container.upper()} may need additional codec support",
                    suggestion="Use MP4 container for best compatibility",
                )
            )

        return issues


# Media Players and VJ Software


class VLCChecker(CompatibilityChecker):
    """Compatibility checker for VLC media player.

    VLC is a universal free media player (Windows/Mac/Linux) that plays
    virtually everything through FFmpeg libraries. The standard for testing.
    """

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")

        # VLC plays virtually everything
        issues.append(
            CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is supported by VLC media player",
                reason="VLC uses FFmpeg libraries for universal codec support",
            )
        )

        # Check for hardware decoding opportunities
        if codec in ["h264", "hevc", "vp9", "av1"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} may benefit from hardware acceleration",
                    reason="Enable hardware decoding in VLC preferences for better performance",
                )
            )

        # Check for very high bitrate or resolution
        if bitrate and bitrate > 300_000_000:  # 300 Mbps
            mbps = bitrate // 1_000_000
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Very high bitrate ({mbps}Mbps) may cause stuttering",
                    reason="Extreme bitrates can exceed disk I/O capabilities",
                    suggestion="Ensure fast storage (NVMe SSD) for smooth playback",
                )
            )

        if resolution:
            width, height = resolution
            if width >= 7680 or height >= 4320:  # 8K
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="8K video requires powerful hardware",
                        reason="8K playback needs modern CPU/GPU and fast storage",
                        suggestion="Enable hardware decoding and use VLC 3.0+",
                    )
                )

        # Container compatibility (VLC plays everything)
        if container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is fully supported",
                    reason="VLC supports all major container formats",
                )
            )

        return issues


class MittiChecker(CompatibilityChecker):
    """Compatibility checker for Mitti video playback software.

    Mitti is professional playback software for Mac, used extensively in
    corporate events, theatre, and exhibitions. Known for extreme reliability.
    """

    RECOMMENDED_CODECS = ["prores", "hap"]  # Transcodes everything to these
    APPLE_SILICON_OPTIMAL = ["prores"]  # Hardware accelerated on M1/M2/M3

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")

        # Check for recommended codecs
        if "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is optimal for Mitti",
                    reason="Hardware accelerated on Apple Silicon Macs (M1/M2/M3)",
                )
            )
        elif "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP Alpha is optimal for Mitti with transparency",
                        reason="GPU-accelerated playback with alpha channel",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP is optimal for Mitti",
                        reason="GPU-accelerated, especially for 4K and multi-output",
                    )
                )

            # HAP requires MOV
            if "mov" not in container:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="HAP codec requires MOV container",
                        suggestion="Remux to MOV container",
                    )
                )
        # Other codecs: Mitti can transcode
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} should be transcoded for Mitti",
                    reason="Mitti recommends ProRes or HAP for reliable playback",
                    suggestion=(
                        "Use Mitti's built-in transcoding to ProRes (Apple Silicon) "
                        "or HAP (multi-output)"
                    ),
                )
            )

        # Check container (MOV preferred)
        if "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MOV container is preferred by Mitti",
                    reason="QuickTime MOV is Mac's native format",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="MP4 works but MOV is preferred for Mitti",
                    suggestion="Use MOV container for best compatibility",
                )
            )

        # Check resolution for performance
        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:  # 4K
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="4K video: use HAP for multi-output, ProRes for single output",
                        reason=(
                            "4K ProRes great on Apple Silicon; 4K HAP better for "
                            "HDMI/DisplayPort multi-output"
                        ),
                        suggestion="HAP for GPU path (external displays), ProRes for SDI",
                    )
                )

        # Check bitrate
        if bitrate and bitrate > 250_000_000:  # 250 Mbps
            mbps = bitrate // 1_000_000
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"High bitrate ({mbps}Mbps) may stress playback",
                    reason="Very high bitrate can cause dropped frames",
                    suggestion="Use ProRes 422 or HAP with moderate bitrate",
                )
            )

        return issues


class MilluminChecker(CompatibilityChecker):
    """Compatibility checker for Millumin video mapping software.

    Millumin is professional software for Mac used in video mapping,
    projection, theatre, dance, museums, and interactive installations.
    """

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")

        # Millumin supports all QuickTime formats
        issues.append(
            CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is supported by Millumin",
                reason="Millumin uses QuickTime and AVFoundation for codec support",
            )
        )

        # Check for recommended codecs
        if "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes is excellent for Millumin",
                    reason="Native Mac codec with hardware acceleration on Apple Silicon",
                )
            )
        elif "hap" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="HAP is optimal for Millumin projection mapping",
                    reason="GPU-accelerated, ideal for multi-projector setups",
                )
            )
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="H.264 works but ProRes/HAP recommended for projection",
                    reason="H.264 is CPU-based, can limit real-time performance",
                    suggestion="Use ProRes or HAP for better projection mapping performance",
                )
            )

        # Check container (MOV preferred)
        if "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MOV is the preferred container for Millumin",
                    reason="QuickTime MOV native to macOS",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 is supported by Millumin",
                    reason="MP4 works well for standard playback",
                )
            )

        # Check resolution for projection
        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:  # 4K
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="4K video requires powerful Mac for smooth projection",
                        reason="4K projection mapping is GPU-intensive",
                        suggestion="Use HAP codec for best 4K projection performance",
                    )
                )

        return issues


# Browser Compatibility


class SafariChecker(CompatibilityChecker):
    """Compatibility checker for Safari browser."""

    SUPPORTED_CODECS = ["h264", "hevc"]

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        if codec not in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"Safari does not support {codec.upper()} codec",
                    reason="Safari only supports H.264 and HEVC (H.265)",
                    suggestion="Convert to H.264 for maximum browser compatibility",
                )
            )
            return issues

        if "mp4" not in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Safari works best with MP4 container format",
                    suggestion="Remux to MP4 container",
                )
            )

        issues.append(
            CompatibilityIssue(
                level=CompatibilityLevel.COMPATIBLE,
                message=f"{codec.upper()} is supported by Safari",
            )
        )

        return issues


class ChromeChecker(CompatibilityChecker):
    """Compatibility checker for Chrome browser."""

    SUPPORTED_CODECS = ["h264", "vp8", "vp9", "av1"]

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()

        if codec in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by Chrome",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not be supported by Chrome",
                    reason="Chrome supports H.264, VP8, VP9, and AV1",
                    suggestion="Convert to H.264 or VP9 for web compatibility",
                )
            )

        return issues


class FirefoxChecker(CompatibilityChecker):
    """Compatibility checker for Firefox browser."""

    SUPPORTED_CODECS = ["h264", "vp8", "vp9", "av1"]
    PARTIALLY_SUPPORTED = ["hevc"]  # Limited to Windows 10+ with extensions

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        if codec in self.SUPPORTED_CODECS:
            # Check for optimal container pairing
            if codec in ["vp8", "vp9"] and "webm" in container:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} in WebM is natively supported by Firefox",
                        reason="WebM is Firefox's preferred format for VP8/VP9",
                    )
                )
            elif codec == "h264" and "mp4" in container:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 in MP4 is fully supported by Firefox",
                        reason="Universal browser compatibility",
                    )
                )
            elif codec == "av1":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="AV1 is supported by Firefox",
                        reason="Modern codec with good efficiency",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is supported by Firefox",
                    )
                )
        elif codec in self.PARTIALLY_SUPPORTED:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} has limited support in Firefox",
                    reason="HEVC requires Windows 10+ with HEVC Video Extensions",
                    suggestion="Convert to H.264 or VP9 for broader compatibility",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"Firefox does not support {codec.upper()} codec",
                    reason="Firefox supports H.264, VP8, VP9, and AV1",
                    suggestion="Convert to H.264 (MP4) or VP9 (WebM) for Firefox",
                )
            )

        return issues


# Social Media Platforms


class InstagramChecker(CompatibilityChecker):
    """Compatibility checker for Instagram."""

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for feed posts
    MAX_DURATION = 60  # 60 seconds for feed, 90 for reels

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        profile = video_info.get("profile", "").lower()
        resolution = video_info.get("resolution")

        # Instagram prefers H.264 Baseline
        if codec != "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=(
                        f"Instagram will re-encode {codec.upper()} to H.264 " f"(quality loss)"
                    ),
                    reason="Instagram only accepts H.264 codec",
                    suggestion="Pre-encode to H.264 to maintain quality control",
                )
            )
        elif profile and "baseline" not in profile:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Instagram prefers H.264 Baseline, not {profile}",
                    reason="Non-Baseline profiles will be re-encoded (quality loss)",
                    suggestion="Convert to Baseline: ffmpeg -profile:v baseline",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Video codec is optimized for Instagram",
                )
            )

        # Check resolution (1080p recommended)
        if resolution:
            width, height = resolution
            if width > 1080 or height > 1920:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} will be downscaled",
                        reason="Instagram max is 1080x1920 for vertical video",
                        suggestion="Downscale to 1080p before upload",
                    )
                )

        return issues


class TwitterChecker(CompatibilityChecker):
    """Compatibility checker for Twitter/X."""

    MAX_FILE_SIZE_STANDARD = 512 * 1024 * 1024  # 512MB
    MAX_FILE_SIZE_PREMIUM = 8 * 1024 * 1024 * 1024  # 8GB
    MAX_DURATION_STANDARD = 140  # seconds

    def __init__(self, account_type: str = "standard"):
        """Initialize Twitter/X checker.

        Args:
            account_type: Account type
        """
        self.account_type = account_type

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        file_size = video_info.get("file_size", 0)

        # Check codec (H.264 High Profile recommended)
        if codec != "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Twitter recommends H.264, not {codec.upper()}",
                    suggestion="Convert to H.264 High Profile for best quality",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 codec is supported by Twitter",
                )
            )

        # Check container
        if "mp4" not in container and "mov" not in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Twitter works best with MP4 or MOV containers",
                    suggestion="Remux to MP4 container",
                )
            )

        # Check file size
        is_premium = self.account_type == "premium"
        max_size = self.MAX_FILE_SIZE_PREMIUM if is_premium else self.MAX_FILE_SIZE_STANDARD
        if file_size > max_size:
            size_mb = file_size // (1024 * 1024)
            limit_mb = max_size // (1024 * 1024)
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_mb}MB exceeds Twitter limit of {limit_mb}MB",
                    reason=f"Twitter {self.account_type} accounts have size limits",
                    suggestion="Compress video or upgrade to Premium",
                )
            )

        return issues


class YouTubeChecker(CompatibilityChecker):
    """Compatibility checker for YouTube uploads."""

    RECOMMENDED_CODEC = "h264"
    RECOMMENDED_PROFILE = "high"  # High Profile with CABAC
    RECOMMENDED_CONTAINER = "mp4"
    MAX_FILE_SIZE = 256 * 1024 * 1024 * 1024  # 256GB
    MAX_DURATION = 12 * 3600  # 12 hours in seconds

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        profile = video_info.get("profile", "").lower()
        container = video_info.get("container", "").lower()
        file_size = video_info.get("file_size", 0)

        # Check codec (H.264 recommended for uploads)
        if codec != self.RECOMMENDED_CODEC:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"YouTube recommends H.264, not {codec.upper()} for uploads",
                    reason="YouTube re-encodes all uploads to multiple formats",
                    suggestion="Upload as H.264 for best quality control and processing speed",
                )
            )
        else:
            # Check H.264 profile
            if profile and "high" in profile:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 High Profile is optimal for YouTube",
                        reason="Best quality for YouTube's re-encoding process",
                    )
                )
            elif profile:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"H.264 {profile.title()} Profile detected",
                        reason="YouTube recommends High Profile for best quality",
                        suggestion="Use High Profile with CABAC for optimal results",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 codec is supported by YouTube",
                    )
                )

        # Check container (MP4 preferred)
        if "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 is YouTube's preferred container format",
                    reason="Fastest processing and best compatibility",
                )
            )
        elif "mov" in container or "avi" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{container.upper()} is accepted but MP4 is preferred",
                    suggestion="Use MP4 for faster upload processing",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="YouTube works best with MP4 container",
                    suggestion="Remux to MP4 for optimal compatibility",
                )
            )

        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            size_gb = file_size // (1024 * 1024 * 1024)
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_gb}GB exceeds YouTube's 256GB limit",
                    reason="YouTube has a maximum file size of 256GB",
                    suggestion="Compress video or split into multiple parts",
                )
            )

        return issues


class TikTokChecker(CompatibilityChecker):
    """Compatibility checker for TikTok uploads."""

    RECOMMENDED_CODEC = "h264"
    RECOMMENDED_PROFILE = "high"
    MAX_FILE_SIZE_MOBILE = 287 * 1024 * 1024  # 287MB for mobile uploads
    MAX_FILE_SIZE_DESKTOP = 10 * 1024 * 1024 * 1024  # 10GB for desktop
    MAX_DURATION = 10 * 60  # 10 minutes
    OPTIMAL_BITRATE_MIN = 8_000_000  # 8 Mbps
    OPTIMAL_BITRATE_MAX = 15_000_000  # 15 Mbps
    LOW_QUALITY_THRESHOLD = 5_000_000  # 5 Mbps triggers quality flag

    def __init__(self, upload_source: str = "mobile"):
        """Initialize TikTok checker.

        Args:
            upload_source: 'mobile' or 'desktop' to determine file size limit
        """
        self.upload_source = upload_source

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")
        file_size = video_info.get("file_size", 0)

        # Check codec (H.264 recommended, HEVC causes issues)
        if codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is the optimal codec for TikTok",
                    reason="Best compatibility across all devices",
                )
            )
        elif codec == "hevc":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="HEVC may cause playback issues on some devices",
                    reason="15-20% of US iOS devices have HEVC compatibility issues",
                    suggestion="Convert to H.264 for universal compatibility",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"TikTok recommends H.264, not {codec.upper()}",
                    reason="TikTok re-encodes all uploads",
                    suggestion="Upload as H.264 to maintain quality control",
                )
            )

        # Check container
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is supported by TikTok",
                    reason="Standard container formats for mobile video",
                )
            )
        elif "webm" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="WebM is supported but MP4 is preferred for TikTok",
                    suggestion="Convert to MP4 for better compatibility",
                )
            )

        # Check resolution (1080x1920 recommended for 9:16 aspect ratio)
        if resolution:
            width, height = resolution
            if width == 1080 and height == 1920:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="1080x1920 is optimal for TikTok",
                        reason="Perfect 9:16 aspect ratio for vertical video",
                    )
                )
            elif width > 1080 or height > 1920:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} will be downscaled",
                        reason="TikTok displays videos at 1080p maximum",
                        suggestion="Export at 1080x1920 to avoid wasted bitrate",
                    )
                )

        # Check bitrate
        if bitrate:
            mbps = bitrate // 1_000_000
            if bitrate < self.LOW_QUALITY_THRESHOLD:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Low bitrate ({mbps}Mbps) may trigger quality downgrade",
                        reason="TikTok flags videos below 5 Mbps as low quality",
                        suggestion="Use 8-15 Mbps for optimal quality",
                    )
                )
            elif bitrate > 20_000_000:  # 20 Mbps
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"High bitrate ({mbps}Mbps) will be compressed anyway",
                        reason="TikTok flattens bitrates above 20 Mbps",
                        suggestion="Use 8-15 Mbps to optimize file size",
                    )
                )

        # Check file size based on upload source
        max_size = (
            self.MAX_FILE_SIZE_DESKTOP
            if self.upload_source == "desktop"
            else self.MAX_FILE_SIZE_MOBILE
        )
        if file_size > max_size:
            size_mb = file_size // (1024 * 1024)
            limit_mb = max_size // (1024 * 1024) if max_size < 1024**3 else "10GB"
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_mb}MB exceeds TikTok {self.upload_source} limit",
                    reason=f"TikTok {self.upload_source} uploads limited to {limit_mb}",
                    suggestion=(
                        "Compress video or use desktop upload for larger files"
                        if self.upload_source == "mobile"
                        else "Compress video to reduce file size"
                    ),
                )
            )

        return issues


class VimeoChecker(CompatibilityChecker):
    """Compatibility checker for Vimeo uploads."""

    RECOMMENDED_CODEC = "h264"
    RECOMMENDED_PROFILE = "high"
    ALSO_ACCEPTS = ["prores"]  # Accepted but not recommended

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")

        # Check codec
        if codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is the recommended codec for Vimeo uploads",
                    reason="Fast upload and optimal platform processing",
                )
            )
        elif "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="ProRes is accepted but not recommended for uploads",
                    reason="ProRes files are very large and slow to upload",
                    suggestion="Use H.264 for faster uploads; save ProRes for archival",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Vimeo recommends H.264, not {codec.upper()}",
                    reason="Vimeo re-encodes all uploads for streaming",
                    suggestion="Upload as H.264 for best results",
                )
            )

        # Check container
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is compatible with Vimeo",
                )
            )

        # Check bitrate based on resolution
        if resolution and bitrate:
            width, height = resolution
            mbps = bitrate // 1_000_000

            if width >= 3840 and height >= 2160:  # 4K
                if bitrate < 40_000_000 or bitrate > 50_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"4K bitrate ({mbps}Mbps) outside recommended range",
                            reason="Vimeo recommends 40-50 Mbps for 4K video",
                            suggestion="Adjust bitrate to 40-50 Mbps for optimal quality",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"4K bitrate ({mbps}Mbps) is optimal for Vimeo",
                        )
                    )
            elif width >= 1920 and height >= 1080:  # 1080p
                if bitrate < 10_000_000 or bitrate > 20_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"1080p bitrate ({mbps}Mbps) outside recommended range",
                            reason="Vimeo recommends 10-20 Mbps for 1080p video",
                            suggestion="Adjust bitrate to 10-20 Mbps for optimal quality",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"1080p bitrate ({mbps}Mbps) is optimal for Vimeo",
                        )
                    )
            elif width >= 1280 and height >= 720:  # 720p
                if bitrate < 5_000_000 or bitrate > 10_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"720p bitrate ({mbps}Mbps) outside recommended range",
                            reason="Vimeo recommends 5-10 Mbps for 720p video",
                            suggestion="Adjust bitrate to 5-10 Mbps for optimal quality",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"720p bitrate ({mbps}Mbps) is optimal for Vimeo",
                        )
                    )

        return issues


class FacebookChecker(CompatibilityChecker):
    """Compatibility checker for Facebook video uploads."""

    RECOMMENDED_CODEC = "h264"
    NEWER_CODECS = ["hevc", "vp9", "av1"]  # Supported in Reels
    MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB
    MAX_DURATION = 240 * 60  # 240 minutes

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        file_size = video_info.get("file_size", 0)
        resolution = video_info.get("resolution")

        # Check codec
        if codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is the recommended codec for Facebook",
                    reason="Universal compatibility across Feed, Stories, and Ads",
                )
            )
        elif codec in self.NEWER_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported for Facebook Reels",
                    reason="Newer codecs accepted but H.264 recommended for Feed",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Facebook recommends H.264, not {codec.upper()}",
                    reason="Facebook will re-encode non-standard codecs",
                    suggestion="Convert to H.264 for best compatibility",
                )
            )

        # Check container
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} is preferred by Facebook",
                    reason="MP4 and MOV offer best compatibility",
                )
            )
        elif "avi" in container or "wmv" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{container.upper()} is supported but not recommended",
                    suggestion="Use MP4 or MOV for better compatibility",
                )
            )

        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            size_gb = file_size / (1024 * 1024 * 1024)
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_gb:.1f}GB exceeds Facebook's 4GB limit",
                    reason="Facebook has a maximum file size of 4GB",
                    suggestion="Compress video or reduce quality to meet size limit",
                )
            )

        # Check resolution recommendations
        if resolution:
            width, height = resolution
            if width >= 1280 and height >= 720:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"Resolution {width}x{height} is suitable for Facebook",
                        reason="720p or higher provides good quality",
                    )
                )

        return issues


# ============================================================================
# PRIMARY API - Uses Rule Engine (loads from YAML)
# ============================================================================


def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility for a specific system.

    This is the primary API function that uses the rule-based engine.
    All 31 systems are defined in system_profiles.yaml.

    Args:
        video_info: Dictionary containing video metadata
        system: System to check compatibility for

    Returns:
        List of compatibility issues

    Example:
        >>> video_info = {
        ...     "codec": "h264",
        ...     "profile": "high",
        ...     "container": "mp4",
        ...     "resolution": (1920, 1080),
        ...     "bitrate": 10_000_000,
        ... }
        >>> issues = check_compatibility(video_info, "youtube")
        >>> for issue in issues:
        ...     print(f"{issue.level.value}: {issue.message}")
    """
    from .rule_engine import RuleEngine

    engine = RuleEngine()
    return engine.check_compatibility(video_info, system)


def get_available_systems() -> List[str]:
    """Return list of all available system names.

    Loads system names from system_profiles.yaml.

    Returns:
        Sorted list of system names that can be checked

    Example:
        >>> systems = get_available_systems()
        >>> print(f"Found {len(systems)} systems")
        >>> print(systems[:5])  # First 5 systems
    """
    from .rule_engine import RuleEngine

    engine = RuleEngine()
    return engine.get_available_systems()
