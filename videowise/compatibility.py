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


# ============================================================================
# LEGACY CHECKER CLASSES (Preserved for Backward Compatibility)
# ============================================================================
# These classes are no longer used by the CLI or primary API, but are kept
# for any external code that may import them directly.
# They remain functional and pass all existing tests.
# ============================================================================

# Import editing platform checkers
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

# Import streaming platform checkers
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
    from .advanced_playout import PlaybackProChecker as AdvancedPlaybackProChecker  # noqa: F401
    from .advanced_playout import ProVideoPlayerChecker as AdvancedPVPChecker  # noqa: F401
    from .advanced_playout import ResolumeChecker as AdvancedResolumeChecker  # noqa: F401
    from .advanced_playout import WirecastChecker as AdvancedWirecastChecker  # noqa: F401

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


# NOTE: Additional legacy checker classes (VmixChecker, OBSChecker, etc.) are
# preserved in the original compatibility.py file. They are functional but no
# longer used by default. The rule engine in system_profiles.yaml now handles
# all 31 systems through declarative rules.

# For a complete list of legacy checker classes, see the git history or the
# original compatibility.py file before the Phase 3 migration.
