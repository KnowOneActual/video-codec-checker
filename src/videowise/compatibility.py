"""Backward-compatible compatibility checker using rule engine.

This module maintains the existing API while internally using the new
rule-based engine. Existing code continues to work without changes.
"""

from typing import Any, Dict, List, Optional, Union, cast

from .rule_engine import RuleEngine
from .types import CompatibilityChecker, CompatibilityIssue, CompatibilityLevel  # noqa: F401


class RuleEngineCompatibilityChecker(CompatibilityChecker):
    """Base class for compatibility checking using rule engine."""

    system_name: str = ""
    variant: Optional[Union[str, List[str]]] = None

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
        return cast(
            List[CompatibilityIssue],
            self._engine.check_compatibility(video_info, self.system_name, self.variant),
        )


# ============================================================================
# LIVE PRODUCTION SYSTEMS
# ============================================================================


class CasparCGChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for CasparCG Server."""

    system_name = "casparcg"

    def __init__(self, version: str = "2.3"):
        """Initialize CasparCG checker.

        Args:
            version: CasparCG Server version
        """
        super().__init__()
        self.version = version


class PlayoutBeeChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for PlayoutBee playout software."""

    system_name = "playoutbee"

    def __init__(self, platform: str = "desktop"):
        """Initialize PlayoutBee checker.

        Args:
            platform: Targeted hardware platform (e.g., 'desktop', 'raspberrypi')
        """
        super().__init__()
        self.variant = platform


class VmixChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for vMix."""

    system_name = "vmix"


class OBSChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for OBS Studio."""

    system_name = "obs"


class QLabChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for QLab."""

    system_name = "qlab"


class ProPresenterChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for ProPresenter."""

    system_name = "propresenter"


# ============================================================================
# EDITING PLATFORMS
# ============================================================================


class DaVinciResolveChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for DaVinci Resolve."""

    system_name = "davinci"

    def __init__(self, version: str = "studio", platform: str = "windows"):
        """Initialize DaVinci Resolve checker.

        Args:
            version: Resolve version ('studio' or 'free')
            platform: Operating system platform
        """
        super().__init__()
        self.variant = [version, platform]
        self.version = version
        self.platform = platform


class AdobePremiereProChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Adobe Premiere Pro."""

    system_name = "premiere"

    def __init__(self, platform: str = "windows"):
        """Initialize Premiere Pro checker.

        Args:
            platform: Operating system platform
        """
        super().__init__()
        self.variant = platform
        self.platform = platform


class FinalCutProChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Final Cut Pro."""

    system_name = "finalcut"

    def __init__(self, platform: str = "mac_apple_silicon"):
        """Initialize Final Cut Pro checker.

        Args:
            platform: Mac platform (e.g., 'mac_apple_silicon')
        """
        super().__init__()
        self.variant = platform


class AvidMediaComposerChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Avid Media Composer."""

    system_name = "avid"


class AfterEffectsChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Adobe After Effects."""

    system_name = "aftereffects"

    def __init__(self, workflow: str = "motion_graphics"):
        """Initialize After Effects checker.

        Args:
            workflow: Animation/compositing workflow type
        """
        super().__init__()
        self.variant = workflow
        self.workflow = workflow


# ============================================================================
# SOCIAL MEDIA PLATFORMS
# ============================================================================


class InstagramChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Instagram."""

    system_name = "instagram"


class TwitterChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Twitter/X."""

    system_name = "twitter"

    def __init__(self, account_type: str = "standard"):
        """Initialize Twitter checker.

        Args:
            account_type: Twitter account type
        """
        super().__init__()
        self.variant = account_type


class YouTubeChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for YouTube."""

    system_name = "youtube"


class TikTokChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for TikTok."""

    system_name = "tiktok"

    def __init__(self, upload_source: str = "mobile"):
        """Initialize TikTok checker.

        Args:
            upload_source: Device used for upload
        """
        super().__init__()
        self.upload_source = upload_source


# ============================================================================
# BROWSERS
# ============================================================================


class SafariChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Safari browser."""

    system_name = "safari"


class ChromeChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Chrome browser."""

    system_name = "chrome"


class FirefoxChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Firefox browser."""

    system_name = "firefox"


# ============================================================================
# STREAMING PLATFORMS
# ============================================================================


class TwitchChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Twitch."""

    system_name = "twitch"


class YouTubeLiveChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for YouTube Live."""

    system_name = "youtube_live"


class ZoomChecker(RuleEngineCompatibilityChecker):
    """Compatibility checker for Zoom."""

    system_name = "zoom"


# ============================================================================
# REGISTRY AND HELPER FUNCTIONS
# ============================================================================


def get_available_systems() -> List[str]:
    """Return list of all available system names."""
    engine = RuleEngine()
    return engine.get_available_systems()


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
