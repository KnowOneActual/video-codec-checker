# Add platform parameter to basic ResolumeChecker fallback at the end of the file
# This is a partial update showing only the changed section

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
