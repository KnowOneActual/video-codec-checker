"""Backward-compatible compatibility checker using rule engine.

This module maintains the existing API while internally using the new
rule-based engine. Existing code continues to work without changes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .rule_engine import RuleEngine


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
    """Base class for compatibility checking using rule engine."""

    system_name: str = ""
    variant: Optional[str] = None

    def __init__(self):
        """Initialize checker with rule engine."""
        self._engine = RuleEngine()

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check compatibility and return list of issues.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues
        """
        return self._engine.check_compatibility(video_info, self.system_name, self.variant)


# ============================================================================
# LIVE PRODUCTION SYSTEMS
# ============================================================================


class CasparCGChecker(CompatibilityChecker):
    """Compatibility checker for CasparCG Server."""

    system_name = "casparcg"

    def __init__(self, version: str = "2.3"):
        super().__init__()
        self.version = version


class PlayoutBeeChecker(CompatibilityChecker):
    """Compatibility checker for PlayoutBee playout software."""

    system_name = "playoutbee"

    def __init__(self, platform: str = "desktop"):
        super().__init__()
        self.variant = platform


class VmixChecker(CompatibilityChecker):
    """Compatibility checker for vMix."""

    system_name = "vmix"


class OBSChecker(CompatibilityChecker):
    """Compatibility checker for OBS Studio."""

    system_name = "obs"


class QLabChecker(CompatibilityChecker):
    """Compatibility checker for QLab."""

    system_name = "qlab"


class ProPresenterChecker(CompatibilityChecker):
    """Compatibility checker for ProPresenter."""

    system_name = "propresenter"


# ============================================================================
# EDITING PLATFORMS
# ============================================================================


class DaVinciResolveChecker(CompatibilityChecker):
    """Compatibility checker for DaVinci Resolve."""

    system_name = "davinci"

    def __init__(self, version: str = "studio", platform: str = "windows"):
        super().__init__()
        self.variant = version
        self.platform = platform


class AdobePremiereProChecker(CompatibilityChecker):
    """Compatibility checker for Adobe Premiere Pro."""

    system_name = "premiere"

    def __init__(self, platform: str = "windows"):
        super().__init__()
        self.platform = platform


class FinalCutProChecker(CompatibilityChecker):
    """Compatibility checker for Final Cut Pro."""

    system_name = "finalcut"

    def __init__(self, platform: str = "mac_apple_silicon"):
        super().__init__()
        self.variant = platform


class AvidMediaComposerChecker(CompatibilityChecker):
    """Compatibility checker for Avid Media Composer."""

    system_name = "avid"


class AfterEffectsChecker(CompatibilityChecker):
    """Compatibility checker for Adobe After Effects."""

    system_name = "aftereffects"

    def __init__(self, workflow: str = "motion_graphics"):
        super().__init__()
        self.workflow = workflow


# ============================================================================
# SOCIAL MEDIA PLATFORMS
# ============================================================================


class InstagramChecker(CompatibilityChecker):
    """Compatibility checker for Instagram."""

    system_name = "instagram"


class TwitterChecker(CompatibilityChecker):
    """Compatibility checker for Twitter/X."""

    system_name = "twitter"

    def __init__(self, account_type: str = "standard"):
        super().__init__()
        self.variant = account_type


class YouTubeChecker(CompatibilityChecker):
    """Compatibility checker for YouTube."""

    system_name = "youtube"


class TikTokChecker(CompatibilityChecker):
    """Compatibility checker for TikTok."""

    system_name = "tiktok"

    def __init__(self, upload_source: str = "mobile"):
        super().__init__()
        self.upload_source = upload_source


# ============================================================================
# BROWSERS
# ============================================================================


class SafariChecker(CompatibilityChecker):
    """Compatibility checker for Safari browser."""

    system_name = "safari"


class ChromeChecker(CompatibilityChecker):
    """Compatibility checker for Chrome browser."""

    system_name = "chrome"


class FirefoxChecker(CompatibilityChecker):
    """Compatibility checker for Firefox browser."""

    system_name = "firefox"


# ============================================================================
# STREAMING PLATFORMS
# ============================================================================


class TwitchChecker(CompatibilityChecker):
    """Compatibility checker for Twitch."""

    system_name = "twitch"


class YouTubeLiveChecker(CompatibilityChecker):
    """Compatibility checker for YouTube Live."""

    system_name = "youtube_live"


class ZoomChecker(CompatibilityChecker):
    """Compatibility checker for Zoom."""

    system_name = "zoom"


# ============================================================================
# REGISTRY AND HELPER FUNCTIONS
# ============================================================================


def get_available_systems() -> List[str]:
    """Return list of all available system names."""
    engine = RuleEngine()
    return engine.list_systems()


def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility for a specific system.

    Args:
        video_info: Dictionary containing video metadata
        system: System to check compatibility for

    Returns:
        List of compatibility issues
    """
    engine = RuleEngine()
    return engine.check_compatibility(video_info, system)
