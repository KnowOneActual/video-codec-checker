"""Streaming platform compatibility checkers.

This module provides compatibility checkers for popular streaming platforms:
- Twitch
- YouTube Live
- Kick
- Restream
- Zoom
- Discord
"""

from typing import Any, Dict, List

from .compatibility import (
    CompatibilityChecker,
    CompatibilityIssue,
    CompatibilityLevel,
)


class TwitchChecker(CompatibilityChecker):
    """Compatibility checker for Twitch streaming platform.

    Twitch is the leading live streaming platform for gaming, creative content,
    and IRL streaming. Strict requirements for reliable streaming.
    """

    REQUIRED_CODEC = "h264"
    SUPPORTED_PROFILES = ["Main", "High"]
    REQUIRED_AUDIO = "aac"
    MAX_BITRATE = 9_000_000  # 9 Mbps (transcoding guaranteed above 6 Mbps)
    RECOMMENDED_BITRATE_1080P = 6_000_000  # 6 Mbps for 1080p60
    RECOMMENDED_BITRATE_720P = 4_500_000  # 4.5 Mbps for 720p60
    KEYFRAME_INTERVAL = 2  # seconds

    def __init__(self, quality: str = "1080p"):
        """Initialize Twitch checker.

        Args:
            quality: Target streaming quality ('1080p' or '720p')
        """
        self.quality = quality

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Twitch streaming.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        profile = video_info.get("profile", "")
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")
        frame_rate = video_info.get("frame_rate")

        # Check codec (H.264 ONLY)
        if codec != "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"Twitch requires H.264 codec, not {codec.upper()}",
                    reason="Twitch only accepts H.264 (AVC) video codec",
                    suggestion="Re-encode to H.264 with Main or High profile",
                )
            )
            return issues

        # Check H.264 profile
        if profile:
            if profile in self.SUPPORTED_PROFILES:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"H.264 {profile} Profile is optimal for Twitch",
                        reason="Main and High profiles provide best quality",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"H.264 {profile} Profile may not be optimal",
                        reason="Twitch recommends Main or High profile",
                        suggestion="Use High profile (level 4.1 or higher) for best quality",
                    )
                )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 codec is required by Twitch",
                    reason="Use Main or High profile for optimal streaming",
                )
            )

        # Check resolution
        if resolution:
            width, height = resolution
            if height > 1080:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} exceeds Twitch recommendation",
                        reason="Twitch recommends 1920x1080 maximum (1080p60 for Partners)",
                        suggestion="Scale to 1920x1080 for reliable streaming",
                    )
                )
            elif height == 1080 and width == 1920:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="1080p resolution is optimal for Twitch",
                        reason="Standard HD streaming resolution",
                    )
                )
            elif height == 720 and width == 1280:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="720p resolution is good for Twitch",
                        reason="Lower bandwidth requirements, reliable streaming",
                    )
                )

        # Check bitrate
        if bitrate:
            mbps = bitrate / 1_000_000
            if bitrate > self.MAX_BITRATE:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.INCOMPATIBLE,
                        message=f"Bitrate {mbps:.1f}Mbps exceeds Twitch maximum of 9 Mbps",
                        reason="Twitch hard limit is 9 Mbps; stream will be rejected",
                        suggestion="Lower bitrate to 6 Mbps for 1080p or 4.5 Mbps for 720p",
                    )
                )
            elif bitrate > self.RECOMMENDED_BITRATE_1080P:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps may cause buffering for viewers",
                        reason="Above 6 Mbps can cause issues for non-transcoded streams",
                        suggestion="Use 6 Mbps for 1080p60 (Partners get transcoding)",
                    )
                )
            elif bitrate < 3_000_000:  # 3 Mbps
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps may result in quality loss",
                        reason="Twitch recommends 3-6 Mbps for good quality",
                        suggestion="Increase bitrate to 4.5-6 Mbps for better quality",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"Bitrate {mbps:.1f}Mbps is optimal for Twitch",
                        reason="Within recommended range for reliable streaming",
                    )
                )

        # Check frame rate
        if frame_rate:
            try:
                fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 30
                if fps > 60:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"Frame rate {fps}fps exceeds Twitch standard",
                            reason="Twitch supports up to 60fps (Partner/Affiliate)",
                            suggestion="Cap at 60fps for optimal streaming",
                        )
                    )
            except (ValueError, TypeError):
                pass

        # Check container formats
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is compatible with Twitch",
                    reason="Standard containers for H.264 streaming",
                )
            )
        elif "flv" in container or "ts" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} is supported by Twitch",
                    reason="Streaming-optimized container format",
                )
            )

        # Note about keyframe interval (critical for Twitch)
        issues.append(
            CompatibilityIssue(
                level=CompatibilityLevel.WARNING,
                message="Ensure keyframe interval is set to 2 seconds",
                reason="Twitch requires 2-second keyframe interval for stream stability",
                suggestion="Set keyframe interval: ffmpeg -g (fps * 2)",
            )
        )

        return issues
