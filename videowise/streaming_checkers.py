"""Streaming platform compatibility checkers.

This module provides compatibility checkers for popular streaming platforms:
- Twitch
- YouTube Live
- Kick
- Restream
- Zoom
- Discord

Usage:
    from videowise.streaming_checkers import TwitchChecker

    checker = TwitchChecker()
    issues = checker.check(video_info)
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


class YouTubeLiveChecker(CompatibilityChecker):
    """Compatibility checker for YouTube Live streaming.

    YouTube Live supports more codecs than Twitch but has specific requirements
    for live streaming vs regular uploads.
    """

    SUPPORTED_CODECS = ["h264", "hevc"]
    RECOMMENDED_CODEC = "h264"
    MAX_BITRATE_4K = 85_000_000  # 85 Mbps for 4K60
    MAX_BITRATE_1080P = 12_000_000  # 12 Mbps for 1080p60
    RECOMMENDED_BITRATE_1080P60 = 9_000_000  # 9 Mbps
    RECOMMENDED_BITRATE_1080P30 = 6_000_000  # 6 Mbps

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for YouTube Live.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")
        frame_rate = video_info.get("frame_rate")
        container = video_info.get("container", "").lower()

        # Check codec
        if codec not in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"YouTube Live recommends H.264 or HEVC, not {codec.upper()}",
                    reason="Other codecs may not be supported for live streaming",
                    suggestion="Use H.264 for best compatibility",
                )
            )
        else:
            if codec == "h264":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.264 is the recommended codec for YouTube Live",
                        reason="Universal support and hardware acceleration",
                    )
                )
            elif codec == "hevc":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HEVC is supported for YouTube Live",
                        reason="Better compression, good for 4K streaming",
                    )
                )

        # Check bitrate based on resolution and frame rate
        if bitrate and resolution:
            width, height = resolution
            mbps = bitrate / 1_000_000

            # Try to determine frame rate
            is_60fps = False
            if frame_rate:
                try:
                    fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 30
                    is_60fps = fps >= 50
                except (ValueError, TypeError):
                    pass

            if width >= 3840 and height >= 2160:  # 4K
                max_bitrate = self.MAX_BITRATE_4K if is_60fps else 51_000_000
                max_mbps = max_bitrate // 1_000_000
                if bitrate > max_bitrate:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"4K bitrate {mbps:.1f}Mbps exceeds YouTube recommendation",
                            reason=f"YouTube recommends up to {max_mbps} Mbps for 4K",
                            suggestion="Lower bitrate for reliable streaming",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"4K bitrate {mbps:.1f}Mbps is suitable for YouTube Live",
                        )
                    )
            elif width >= 1920 and height >= 1080:  # 1080p
                recommended = (
                    self.RECOMMENDED_BITRATE_1080P60
                    if is_60fps
                    else self.RECOMMENDED_BITRATE_1080P30
                )
                recommended_mbps = recommended / 1_000_000

                if bitrate > self.MAX_BITRATE_1080P:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"1080p bitrate {mbps:.1f}Mbps exceeds recommendation",
                            reason="YouTube recommends up to 12 Mbps for 1080p60",
                            suggestion=f"Use {recommended_mbps} Mbps for optimal balance",
                        )
                    )
                elif bitrate < 4_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"1080p bitrate {mbps:.1f}Mbps may be too low",
                            reason="May result in quality degradation",
                            suggestion=f"Increase to {recommended_mbps} Mbps",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"1080p bitrate {mbps:.1f}Mbps is optimal for YouTube Live",
                        )
                    )

        # Check container
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is compatible with YouTube Live",
                )
            )
        elif "flv" in container or "ts" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} is supported for streaming",
                )
            )

        return issues


class KickChecker(CompatibilityChecker):
    """Compatibility checker for Kick streaming platform.

    Kick is a newer streaming platform competing with Twitch.
    Similar requirements to Twitch with some differences.
    """

    REQUIRED_CODEC = "h264"
    MAX_BITRATE = 10_000_000  # 10 Mbps
    RECOMMENDED_BITRATE = 8_000_000  # 8 Mbps for 1080p60

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Kick streaming.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        bitrate = video_info.get("bitrate")
        resolution = video_info.get("resolution")

        # Check codec
        if codec != "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"Kick requires H.264 codec, not {codec.upper()}",
                    reason="Kick only accepts H.264 for live streaming",
                    suggestion="Re-encode to H.264",
                )
            )
            return issues
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 codec is required by Kick",
                )
            )

        # Check bitrate
        if bitrate:
            mbps = bitrate / 1_000_000
            if bitrate > self.MAX_BITRATE:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps exceeds Kick recommendation",
                        reason="Kick recommends up to 10 Mbps",
                        suggestion="Lower bitrate to 8 Mbps for reliable streaming",
                    )
                )
            elif bitrate < 3_000_000:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps may be too low",
                        suggestion="Use 6-8 Mbps for good quality",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"Bitrate {mbps:.1f}Mbps is suitable for Kick",
                    )
                )

        # Check resolution
        if resolution:
            width, height = resolution
            if height > 1080:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} exceeds standard",
                        reason="Kick optimizes for 1080p streaming",
                        suggestion="Use 1920x1080 for best compatibility",
                    )
                )

        return issues


class RestreamChecker(CompatibilityChecker):
    """Compatibility checker for Restream multi-streaming service.

    Restream allows streaming to multiple platforms simultaneously.
    Requirements based on most restrictive platform (usually Twitch).
    """

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Restream.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        bitrate = video_info.get("bitrate")

        # Restream recommends H.264 for multi-platform compatibility
        if codec != "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Restream works best with H.264, not {codec.upper()}",
                    reason="H.264 ensures compatibility across all platforms",
                    suggestion="Use H.264 for multi-platform streaming",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is optimal for Restream multi-platform streaming",
                    reason="Works across Twitch, YouTube, Facebook, and others",
                )
            )

        # Check bitrate (conservative for multi-streaming)
        if bitrate:
            mbps = bitrate / 1_000_000
            if bitrate > 6_000_000:  # 6 Mbps
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps may be high for multi-streaming",
                        reason="Restream recommends conservative bitrates for reliability",
                        suggestion="Use 4.5-6 Mbps for best multi-platform reliability",
                    )
                )
            elif bitrate < 3_000_000:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps may compromise quality",
                        suggestion="Use 4.5-6 Mbps for good quality across platforms",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"Bitrate {mbps:.1f}Mbps is suitable for Restream",
                        reason="Good balance for multi-platform streaming",
                    )
                )

        return issues


class ZoomChecker(CompatibilityChecker):
    """Compatibility checker for Zoom video conferencing.

    Zoom has specific requirements for video playback and screen sharing.
    """

    SUPPORTED_CODECS = ["h264", "hevc"]
    RECOMMENDED_BITRATE = 2_000_000  # 2 Mbps for 1080p

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Zoom.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        bitrate = video_info.get("bitrate")
        resolution = video_info.get("resolution")
        frame_rate = video_info.get("frame_rate")

        # Check codec
        if codec in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by Zoom",
                    reason="Hardware acceleration available for smooth playback",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may have issues in Zoom",
                    reason="Zoom works best with H.264 or HEVC",
                    suggestion="Convert to H.264 for best Zoom compatibility",
                )
            )

        # Check resolution
        if resolution:
            width, height = resolution
            if height > 1080:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} will be downscaled by Zoom",
                        reason="Zoom caps video at 1080p for most plans",
                        suggestion="Use 1920x1080 to match Zoom's capabilities",
                    )
                )

        # Check bitrate
        if bitrate:
            mbps = bitrate / 1_000_000
            if bitrate > 4_000_000:  # 4 Mbps
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps is high for Zoom screen sharing",
                        reason="Zoom compresses video for conferencing bandwidth",
                        suggestion="Use 2-3 Mbps for optimal Zoom playback",
                    )
                )

        # Check frame rate
        if frame_rate:
            try:
                fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 30
                if fps > 30:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"Frame rate {fps}fps exceeds Zoom standard",
                            reason="Zoom typically caps at 30fps for video sharing",
                            suggestion="Use 30fps for Zoom compatibility",
                        )
                    )
            except (ValueError, TypeError):
                pass

        return issues


class DiscordChecker(CompatibilityChecker):
    """Compatibility checker for Discord Go Live and video sharing.

    Discord has specific limitations for screen sharing and video uploads.
    """

    SUPPORTED_CODECS = ["h264", "vp8", "vp9"]
    MAX_FILE_SIZE_FREE = 8 * 1024 * 1024  # 8MB
    MAX_FILE_SIZE_NITRO = 100 * 1024 * 1024  # 100MB
    MAX_BITRATE_GOLIVE = 8_000_000  # 8 Mbps for Go Live

    def __init__(self, user_type: str = "free"):
        """Initialize Discord checker.

        Args:
            user_type: 'free' or 'nitro' for file size limits
        """
        self.user_type = user_type

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Discord.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        bitrate = video_info.get("bitrate")
        file_size = video_info.get("file_size", 0)
        resolution = video_info.get("resolution")

        # Check codec
        if codec in self.SUPPORTED_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by Discord",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not play in Discord",
                    reason="Discord supports H.264, VP8, and VP9",
                    suggestion="Convert to H.264 for best compatibility",
                )
            )

        # Check file size for uploads
        max_size = (
            self.MAX_FILE_SIZE_NITRO if self.user_type == "nitro" else self.MAX_FILE_SIZE_FREE
        )
        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            limit_mb = max_size / (1024 * 1024)
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_mb:.1f}MB exceeds Discord {self.user_type} limit",
                    reason=f"Discord {self.user_type} accounts limited to {limit_mb}MB",
                    suggestion=(
                        "Compress video or upgrade to Nitro"
                        if self.user_type == "free"
                        else "Compress video"
                    ),
                )
            )

        # Check Go Live streaming bitrate
        if bitrate:
            mbps = bitrate / 1_000_000
            if bitrate > self.MAX_BITRATE_GOLIVE:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate {mbps:.1f}Mbps exceeds Discord Go Live limit",
                        reason="Discord Go Live caps at 8 Mbps for Source quality",
                        suggestion="Use 6-8 Mbps for Discord streaming",
                    )
                )

        # Check resolution for Go Live
        if resolution:
            width, height = resolution
            if height > 1080 and self.user_type != "nitro":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {width}x{height} requires Discord Nitro",
                        reason="1080p60 Go Live requires Nitro subscription",
                        suggestion="Use 720p for free accounts or upgrade to Nitro",
                    )
                )

        return issues
