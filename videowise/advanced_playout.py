"""Advanced live production system compatibility checkers.

Professional playout and media server software with detailed codec and
performance analysis.
"""

from typing import Any, Dict, List

from .compatibility import CompatibilityChecker, CompatibilityIssue, CompatibilityLevel


class WirecastChecker(CompatibilityChecker):
    """Compatibility checker for Wirecast live streaming software.

    Wirecast is a professional live video streaming production tool for Windows
    and macOS with hardware encoding support.
    """

    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "mpeg2video",
        "mjpeg",  # Add MJPEG support
    }

    # Hardware acceleration
    HW_ACCEL_CODECS = ["h264", "hevc"]  # Intel QuickSync, NVIDIA NVENC

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")
        container = video_info.get("container", "").lower()

        # Check codec support
        if codec not in self.SUPPORTED_CODECS:
            supported = ", ".join(sorted(self.SUPPORTED_CODECS))
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Wirecast may not be supported for {codec.upper()}",
                    reason=f"Wirecast supports: {supported}",
                    suggestion="Convert to H.264 or ProRes for best compatibility",
                )
            )
        elif codec in self.HW_ACCEL_CODECS:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is recommended for Wirecast",
                    reason=(
                        "Hardware acceleration via Intel QuickSync or "
                        "NVIDIA NVENC"
                    ),
                )
            )
        elif codec == "prores":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes provides high-quality playback in Wirecast",
                    reason="Professional codec for broadcast workflows",
                )
            )
        elif codec == "mjpeg":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MJPEG is supported by Wirecast",
                    reason="Intraframe codec with good compatibility",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by Wirecast",
                )
            )

        # Check resolution and provide hardware guidance
        if resolution:
            width, height = resolution

            if width >= 3840 and height >= 2160:  # 4K
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(
                            "4K streaming requires powerful hardware (i7 3.0GHz+)"
                        ),
                        reason="4K encoding is CPU/GPU intensive",
                        suggestion="Use hardware encoding (QuickSync/NVENC) for 4K",
                    )
                )
            elif width >= 1920 and height >= 1080:  # 1080p
                if codec == "h264":
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=(
                                "1080p H.264 works well with hardware acceleration"
                            ),
                            reason="Recommended configuration for live streaming",
                        )
                    )

        # Check bitrate recommendations
        if bitrate:
            mbps = bitrate // 1_000_000

            # High bitrate warning (>100 Mbps for any resolution)
            if bitrate > 100_000_000:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(
                            f"Very high bitrate ({mbps}Mbps) may stress "
                            "system resources"
                        ),
                        reason=(
                            "High bitrates require fast storage and "
                            "powerful hardware"
                        ),
                        suggestion=(
                            "Use SSD storage and ensure adequate CPU/GPU capacity"
                        ),
                    )
                )
            elif resolution:
                width, height = resolution
                # 1080p < 4.5 Mbps
                if (
                    width >= 1920
                    and height >= 1080
                    and bitrate < 4_500_000
                ):
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=(
                                f"Bitrate {mbps}Mbps may be low for 1080p streaming"
                            ),
                            reason=(
                                "Wirecast recommends at least 4.5 Mbps for 1080p"
                            ),
                            suggestion=(
                                "Increase bitrate to 4.5-8 Mbps for better quality"
                            ),
                        )
                    )

        # Check container format
        if "mp4" in container or "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is supported by Wirecast",
                )
            )
        elif "wmv" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=(
                        "WMV container may have limited support, MP4/MOV preferred"
                    ),
                    suggestion="Use MP4 or MOV for better compatibility",
                )
            )

        if not issues:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Video should be compatible with Wirecast",
                )
            )

        return issues


class ResolumeChecker(CompatibilityChecker):
    """Compatibility checker for Resolume VJ/media server software.

    Resolume is a professional tool for live video performances and media servers,
    optimized for real-time playback with multiple layers.
    """

    OPTIMAL_CODEC = "dxv"  # Proprietary, GPU-accelerated
    GPU_CODECS = ["dxv", "hap", "photojpeg"]  # Hardware accelerated
    SUPPORTED_CODECS = {
        "dxv",
        "hap",
        "prores",
        "photojpeg",
        "h264",
        "mjpeg",
    }

    def __init__(self, platform: str = "windows"):
        """Initialize Resolume checker.

        Args:
            platform: 'windows' or 'mac' for platform-specific recommendations
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

        # Check for DXV (optimal)
        if "dxv" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DXV is the optimal codec for Resolume",
                    reason="Hardware-accelerated with Resolume's own GPU decoder",
                )
            )
            # Add 4K layer warning even for DXV
            if resolution:
                width, height = resolution
                if width >= 3840 and height >= 2160:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message="4K requires careful layer management",
                            reason=(
                                "Multiple 4K layers can stress even "
                                "GPU-accelerated playback"
                            ),
                            suggestion=(
                                "Limit layer count or use lower resolution for layers"
                            ),
                        )
                    )
        # Check for HAP (second best)
        elif "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "HAP Alpha is optimal for Resolume with transparency"
                        ),
                        reason=(
                            "GPU-accelerated, second-best after DXV with "
                            "alpha support"
                        ),
                    )
                )
            elif "hap_q" in codec or "hapq" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "HAP Q is optimal for high-quality Resolume playback"
                        ),
                        reason=(
                            "GPU-accelerated with better color depth than "
                            "standard HAP"
                        ),
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP codec is optimal for Resolume",
                        reason="GPU-accelerated, second only to DXV",
                    )
                )
            # Add 4K layer warning for HAP too
            if resolution:
                width, height = resolution
                if width >= 3840 and height >= 2160:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=(
                                "4K requires careful layer management even with HAP"
                            ),
                            reason="Multiple 4K layers can stress system resources",
                            suggestion=(
                                "Limit layer count or use lower resolution for layers"
                            ),
                        )
                    )
        # Check for PhotoJPEG
        elif "photojpeg" in codec or ("mjpeg" in codec and "photo" in codec):
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="PhotoJPEG provides fast playback in Resolume",
                    reason="Hardware-accelerated with Resolume's own decoder",
                )
            )
        # Check for ProRes
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "ProRes 4444 provides high quality with alpha support"
                        ),
                        reason=(
                            "Good for quality, but more CPU intensive than HAP/DXV"
                        ),
                        suggestion=(
                            "Consider converting to HAP Alpha for better performance"
                        ),
                    )
                )
            else:
                # ProRes is always CPU intensive in Resolume (even on Mac)
                platform_suffix = " on Mac" if self.platform == "mac" else " on Windows"
                no_hw_reason = " in Resolume" if self.platform == "mac" else " on Windows"
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="ProRes is CPU-based" + platform_suffix,
                        reason="No hardware acceleration" + no_hw_reason,
                        suggestion="Convert to DXV or HAP for better performance",
                    )
                )
        # Check for H.264
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=(
                        "H.264 is CPU playback via system codecs (not optimal)"
                    ),
                    reason="Relies on MediaFoundation/AVFoundation, less efficient",
                    suggestion="Convert to DXV or HAP for optimal live performance",
                )
            )
        elif codec == "hevc":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="HEVC not recommended for Resolume",
                    reason="High CPU overhead for decoding",
                    suggestion="Convert to DXV or HAP for better performance",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not be optimal for Resolume",
                    reason="Resolume works best with DXV, HAP, or PhotoJPEG",
                    suggestion="Convert to DXV for best performance",
                )
            )

        # Check for 4K multi-layer warning (for non-GPU codecs)
        if resolution:
            width, height = resolution
            if (
                width >= 3840
                and height >= 2160
                and "dxv" not in codec
                and "hap" not in codec
            ):
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=(
                            "4K playback without GPU codec may struggle with layers"
                        ),
                        reason="Multiple 4K layers require GPU-accelerated codecs",
                        suggestion="Use DXV or HAP for multi-layer 4K performance",
                    )
                )

        # Check bitrate for performance
        if bitrate and bitrate > 200_000_000:  # 200 Mbps
            mbps = bitrate // 1_000_000
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"Very high bitrate ({mbps}Mbps) may stress disk I/O",
                    reason="High data rates can cause stuttering during playback",
                    suggestion="Use SSD storage for high-bitrate media",
                )
            )

        # Check container format
        if "mov" in container or "avi" in container or "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.UPPER()} container is supported by Resolume",
                )
            )
        elif "gif" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="GIF playback via Resolume's own engine",
                    reason="Native GIF support for animations",
                )
            )

        return issues


class PlaybackProChecker(CompatibilityChecker):
    """Compatibility checker for PlaybackPro professional playback software.

    PlaybackPro is a macOS-only professional non-linear media playback
    application designed for reliable HD and 4K playback in live events.
    """

    RECOMMENDED_CODECS = ["prores", "h264"]  # ProRes 422 preferred
    PLUS_VERSION_CODECS = ["hevc"]  # H.265 only in Plus version

    def __init__(self, version: str = "plus"):
        """Initialize PlaybackPro checker.

        Args:
            version: 'standard' or 'plus' (Plus supports H.265/HEVC)
        """
        self.version = version

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
        bitrate = video_info.get("bitrate")
        resolution = video_info.get("resolution")

        # Check codec support
        if "prores" in codec:
            if "422" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "ProRes 422 is the recommended codec for PlaybackPro"
                        ),
                        reason="Optimal for reliable playback in live events",
                    )
                )
            elif "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 supports alpha channel",
                        reason="Professional quality with transparency support",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes is well-supported by PlaybackPro",
                    )
                )
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is supported by PlaybackPro",
                    reason="Good compatibility with variable bitrate encoding",
                )
            )
        elif codec == "hevc" or codec == "h265":
            if self.version == "plus":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="H.265/HEVC is supported in PlaybackPro Plus",
                        reason="Efficient codec for high-resolution playback",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.INCOMPATIBLE,
                        message="H.265/HEVC requires PlaybackPro Plus",
                        reason="Standard version does not support HEVC",
                        suggestion="Upgrade to Plus or convert to ProRes/H.264",
                    )
                )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may not be optimal for PlaybackPro",
                    suggestion="Convert to ProRes 422 for best reliability",
                )
            )

        # Check bitrate based on resolution
        if bitrate and resolution:
            width, height = resolution
            mbps = bitrate // 1_000_000

            if width >= 3840 and height >= 2160:  # 4K
                if bitrate < 30_000_000:  # Less than 30 Mbps
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=(
                                f"4K bitrate ({mbps}Mbps) is outside "
                                "recommended range"
                            ),
                            reason="PlaybackPro recommends 30-40 Mbps for 4K",
                            suggestion=(
                                "Increase bitrate to 30-40 Mbps for 4K playback"
                            ),
                        )
                    )
                elif bitrate >= 30_000_000 and bitrate <= 40_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"4K bitrate ({mbps}Mbps) is optimal",
                        )
                    )
            elif width >= 1920 and height >= 1080:  # 1080p/HD
                if bitrate < 15_000_000:  # Less than 15 Mbps
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=(
                                f"HD bitrate ({mbps}Mbps) is outside "
                                "recommended range"
                            ),
                            reason="PlaybackPro recommends 15-30 Mbps for HD",
                            suggestion=(
                                "Increase bitrate to 15-30 Mbps for HD playback"
                            ),
                        )
                    )
                elif bitrate >= 15_000_000 and bitrate <= 30_000_000:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=(
                                f"HD bitrate ({mbps}Mbps) is suitable within "
                                "recommended range"
                            ),
                        )
                    )

        # Check container - MOV is REQUIRED
        if "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MOV container is required for PlaybackPro",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message="PlaybackPro requires MOV container",
                    reason="PlaybackPro requires MOV, not MP4",
                    suggestion="Remux to MOV container",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message="PlaybackPro requires MOV container",
                    reason="PlaybackPro only supports MOV container",
                    suggestion="Remux to MOV container",
                )
            )

        return issues


class ProVideoPlayerChecker(CompatibilityChecker):
    """Compatibility checker for ProVideoPlayer (PVP) by Renewed Vision.

    PVP is a professional multi-screen media server application designed for
    live events, churches, and concerts with timecode sync capabilities.
    """

    SUPPORTED_CODECS = {
        "dxv",  # Optimal with timecode
        "hap",
        "prores",
        "h264",
        "hevc",
    }

    GPU_CODECS = ["dxv", "hap"]  # Hardware accelerated

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

        # Check for DXV (optimal for PVP)
        if "dxv" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DXV codec works perfectly with PVP timecode features",
                    reason="GPU-accelerated with excellent timecode sync",
                )
            )
        # Check for HAP
        elif "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "HAP Alpha provides GPU-accelerated playback with "
                            "transparency for overlays"
                        ),
                        reason="Ideal for overlays and multi-layer compositions",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="HAP codec provides excellent performance in PVP",
                        reason="GPU-accelerated for smooth multi-layer playback",
                    )
                )
        # Check for ProRes
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            "ProRes 4444 supports alpha channel for transparency"
                        ),
                        reason="Professional quality for multi-screen setups",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes is fully supported by PVP",
                        reason="Professional codec for broadcast workflows",
                    )
                )
        # Check for H.264/H.265
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="H.264 is supported by PVP",
                    reason="Hardware acceleration available",
                    suggestion=(
                        "Consider DXV or HAP for better multi-layer performance"
                    ),
                )
            )
        elif codec == "hevc":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="HEVC is supported by PVP",
                    reason="Hardware acceleration available",
                    suggestion=(
                        "Consider DXV or HAP for better multi-layer performance"
                    ),
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"PVP may have limited support for {codec.UPPER()}",
                    reason="PVP works best with DXV, HAP, ProRes, or H.264",
                    suggestion=(
                        "Convert to DXV for optimal timecode and "
                        "multi-screen performance"
                    ),
                )
            )

        # Check container
        if "mov" in container or "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.UPPER()} container is supported by PVP",
                )
            )

        # Note about timecode support
        if "dxv" in codec or "hap" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Timecode following and triggering fully supported",
                    reason=(
                        "GPU codecs work excellently with PVP's timecode features"
                    ),
                )
            )

        return issues
