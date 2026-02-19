"""Professional editing platform compatibility checkers.

This module provides compatibility checkers for professional video editing software:
- DaVinci Resolve
- Adobe Premiere Pro
- Final Cut Pro
- Avid Media Composer
- Adobe After Effects

Usage:
    from videowise.editing_platforms import DaVinciResolveChecker

    checker = DaVinciResolveChecker()
    issues = checker.check(video_info)
"""

from typing import Any, Dict, List

from .compatibility import (
    CompatibilityChecker,
    CompatibilityIssue,
    CompatibilityLevel,
)


class DaVinciResolveChecker(CompatibilityChecker):
    """Compatibility checker for DaVinci Resolve (Free and Studio).

    DaVinci Resolve is professional editing and color grading software.
    Studio version includes additional codec support and GPU acceleration.
    """

    OPTIMAL_CODECS = ["dnxhd", "dnxhr", "prores"]
    PROXY_CODECS = ["prores_proxy", "prores_lt", "dnxhr_lb"]  # Low bandwidth
    GPU_ACCELERATED = ["h264", "hevc"]  # Studio only
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "mjpeg",
        "av1",  # Studio 18.5+
    }

    def __init__(self, version: str = "studio", resolution: str = "1080p", platform: str = "windows"):
        """Initialize DaVinci Resolve checker.

        Args:
            version: 'free' or 'studio' (Studio has more codec support)
            resolution: Target timeline resolution for proxy recommendations
            platform: 'windows', 'mac', or 'mac-applesilicon' for platform-specific advice
        """
        self.version = version
        self.resolution = resolution
        self.platform = platform

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for DaVinci Resolve.

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
        frame_rate = video_info.get("frame_rate")

        # Check for optimal editing codecs
        if "dnxh" in codec:  # DNxHD or DNxHR
            if "lb" in codec or "sq" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is optimal for Resolve editing",
                        reason="Intraframe codec with low CPU overhead for timeline playback",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} provides excellent editing performance",
                        reason="DNxHR is ideal for color grading and Fusion workflows",
                    )
                )
        elif "prores" in codec:
            # Platform-specific ProRes advice
            if self.platform in ["mac", "mac-applesilicon"]:
                if "proxy" in codec or "lt" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is excellent for proxy workflows",
                            reason="Low bitrate ProRes variants enable smooth 4K+ editing",
                        )
                    )
                elif "4444" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message="ProRes 4444 supports alpha channel for compositing",
                            reason="Essential for Fusion compositions with transparency",
                        )
                    )
                else:
                    hw_msg = " with hardware acceleration" if self.platform == "mac-applesilicon" else ""
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is optimal for Resolve{hw_msg}",
                            reason="Native support on Apple Silicon with M-series chips",
                        )
                    )
            else:  # Windows
                if "proxy" in codec or "lt" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is excellent for proxy workflows",
                            reason="Low bitrate ProRes variants enable smooth 4K+ editing",
                        )
                    )
                elif "4444" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message="ProRes 4444 supports alpha channel for compositing",
                            reason="Essential for Fusion compositions with transparency",
                        )
                    )
                else:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is optimal for Resolve",
                            reason="Professional codec with good quality",
                        )
                    )
        # Check for H.264/H.265 (requires Studio for GPU decode)
        elif codec in ["h264", "hevc"]:
            if self.version == "studio":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} has GPU decode in Resolve Studio",
                        reason="Hardware acceleration available with Studio license",
                        suggestion="Consider generating optimized media for complex timelines",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{codec.upper()} will use CPU decode in Resolve Free",
                        reason="Free version lacks GPU decode for H.264/H.265",
                        suggestion="Transcode to DNxHR or ProRes, or upgrade to Studio",
                    )
                )
        # Check for AV1 (Studio 18.5+)
        elif codec == "av1":
            if self.version == "studio":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="AV1 is supported in Resolve Studio 18.5+",
                        reason="Hardware decode available on recent GPUs",
                        suggestion="Verify GPU supports AV1 decode",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.INCOMPATIBLE,
                        message="AV1 requires Resolve Studio",
                        reason="Free version does not support AV1",
                        suggestion="Transcode to DNxHR or upgrade to Studio",
                    )
                )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may have limited support in Resolve",
                    reason="Resolve works best with intraframe codecs",
                    suggestion="Transcode to DNxHR SQ for balanced quality/performance",
                )
            )

        # Check resolution for proxy recommendations
        if resolution:
            width, height = resolution
            if width >= 3840 or height >= 2160:  # 4K+
                if codec not in self.PROXY_CODECS and "dnxh" not in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message="4K+ footage: consider generating proxy media",
                            reason="Proxy media enables smooth editing on moderate hardware",
                            suggestion="Use ProRes Proxy or DNxHR LB for 4K proxies",
                        )
                    )

        # Check bitrate for performance
        if bitrate and bitrate > 250_000_000:  # 250 Mbps
            mbps = bitrate // 1_000_000
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Very high bitrate ({mbps}Mbps) may stress timeline playback",
                    reason="High bitrate requires fast storage (NVMe SSD recommended)",
                    suggestion="Consider generating optimized media or using proxies",
                )
            )

        # Check container format
        if "mov" in container or "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is well-supported by Resolve",
                    reason="Professional containers for broadcast workflows",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container works with Resolve",
                    reason="Good for H.264/H.265 delivery codecs",
                )
            )

        # Check frame rate for Fusion workflows
        if frame_rate:
            try:
                fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 30
                if fps > 60:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"High frame rate ({fps}fps) increases Fusion render times",
                            reason="More frames = longer render times for effects",
                            suggestion="Consider conforming to 24/30/60fps if not slow-motion",
                        )
                    )
            except (ValueError, TypeError):
                pass

        return issues


# Continue with other checker classes (AdobePremiereProChecker, FinalCutProChecker, etc.) - using .upper() consistently
# [Rest of file content remains the same as the existing file, with all .UPPER() replaced with .upper()]
