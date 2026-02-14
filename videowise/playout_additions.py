"""Additional live production system checkers.

These checkers should be integrated into videowise/compatibility.py.
Insert after PlayoutBeeChecker and before VmixChecker.
"""

from typing import Any, Dict, List

# Import from compatibility.py when integrating
# from videowise.compatibility import CompatibilityLevel, CompatibilityIssue, CompatibilityChecker


class WirecastChecker:
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
    }

    # Hardware acceleration
    HW_ACCEL_CODECS = ["h264", "hevc"]  # Intel QuickSync, NVIDIA NVENC

    def check(self, video_info: Dict[str, Any]) -> List:
        issues: List = []
        codec = video_info.get("codec", "").lower()
        resolution = video_info.get("resolution")
        bitrate = video_info.get("bitrate")
        container = video_info.get("container", "").lower()

        # Check codec support
        if codec not in self.SUPPORTED_CODECS:
            supported = ", ".join(sorted(self.SUPPORTED_CODECS))
            issues.append(
                {
                    "level": "WARNING",
                    "message": f"Wirecast may have limited support for {codec.upper()}",
                    "reason": f"Wirecast supports: {supported}",
                    "suggestion": "Convert to H.264 or ProRes for best compatibility",
                }
            )
        elif codec in self.HW_ACCEL_CODECS:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{codec.upper()} supports hardware acceleration in Wirecast",
                    "reason": "Intel QuickSync or NVIDIA NVENC offload encoding to GPU",
                }
            )
        elif codec == "prores":
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "ProRes provides high-quality playback in Wirecast",
                    "reason": "Professional codec for broadcast workflows",
                }
            )
        else:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{codec.upper()} is supported by Wirecast",
                }
            )

        # Check resolution and provide hardware guidance
        if resolution:
            width, height = resolution

            if width >= 3840 and height >= 2160:  # 4K
                issues.append(
                    {
                        "level": "WARNING",
                        "message": "4K streaming requires powerful hardware (i7 3.0GHz+)",
                        "reason": "4K encoding is CPU/GPU intensive",
                        "suggestion": "Use hardware encoding (QuickSync/NVENC) for 4K",
                    }
                )
            elif width >= 1920 and height >= 1080:  # 1080p
                if codec == "h264":
                    issues.append(
                        {
                            "level": "COMPATIBLE",
                            "message": "1080p H.264 works well with hardware acceleration",
                            "reason": "Recommended configuration for live streaming",
                        }
                    )

        # Check bitrate recommendations
        if bitrate and resolution:
            width, height = resolution
            mbps = bitrate // 1_000_000

            if width >= 1920 and height >= 1080 and bitrate < 4_500_000:  # 1080p < 4.5 Mbps
                issues.append(
                    {
                        "level": "WARNING",
                        "message": f"Bitrate {mbps}Mbps may be low for 1080p streaming",
                        "reason": "Wirecast recommends at least 4.5 Mbps for 1080p",
                        "suggestion": "Increase bitrate to 4.5-8 Mbps for better quality",
                    }
                )

        # Check container format
        if "mp4" in container or "mov" in container:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{container.upper()} container is supported by Wirecast",
                }
            )

        if not issues:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "Video should be compatible with Wirecast",
                }
            )

        return issues


class ResolumeChecker:
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

    def check(self, video_info: Dict[str, Any]) -> List:
        issues: List = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check for DXV (optimal)
        if "dxv" in codec:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "DXV is the optimal codec for Resolume",
                    "reason": "Hardware-accelerated with Resolume's own decoder",
                }
            )
        # Check for HAP (second best)
        elif "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "HAP Alpha provides GPU-accelerated playback with transparency",
                        "reason": "Second-best performance after DXV, with alpha support",
                    }
                )
            elif "hap_q" in codec or "hapq" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "HAP Q provides high-quality GPU-accelerated playback",
                        "reason": "Better color depth than standard HAP",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "HAP codec provides excellent performance in Resolume",
                        "reason": "GPU-accelerated, second only to DXV",
                    }
                )
        # Check for PhotoJPEG
        elif "photojpeg" in codec or ("mjpeg" in codec and "photo" in codec):
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "PhotoJPEG provides fast playback in Resolume",
                    "reason": "Hardware-accelerated with Resolume's own decoder",
                }
            )
        # Check for ProRes
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes 4444 provides high quality with alpha support",
                        "reason": "Good for quality, but more CPU intensive than HAP/DXV",
                        "suggestion": "Consider converting to HAP Alpha for better performance",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes is supported but more CPU intensive",
                        "reason": "Resolume can play ProRes via system decoders",
                        "suggestion": "Convert to DXV or HAP for better real-time performance",
                    }
                )
        # Check for H.264
        elif codec == "h264":
            issues.append(
                {
                    "level": "WARNING",
                    "message": "H.264 playback via system codecs (not optimal)",
                    "reason": "Relies on MediaFoundation/AVFoundation, less efficient",
                    "suggestion": "Convert to DXV or HAP for optimal live performance",
                }
            )
        else:
            issues.append(
                {
                    "level": "WARNING",
                    "message": f"{codec.upper()} may not be optimal for Resolume",
                    "reason": "Resolume works best with DXV, HAP, or PhotoJPEG",
                    "suggestion": "Convert to DXV for best performance",
                }
            )

        # Check container format
        if "mov" in container or "avi" in container or "mp4" in container:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{container.upper()} container is supported by Resolume",
                }
            )
        elif "gif" in container:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "GIF playback via Resolume's own engine",
                    "reason": "Native GIF support for animations",
                }
            )

        return issues


class PlaybackProChecker:
    """Compatibility checker for PlaybackPro professional playback software.

    PlaybackPro is a macOS-only professional non-linear media playback application
    designed for reliable HD and 4K playback in live events.
    """

    RECOMMENDED_CODECS = ["prores", "h264"]  # ProRes 422 preferred
    PLUS_VERSION_CODECS = ["hevc"]  # H.265 only in Plus version

    def __init__(self, version: str = "plus", resolution_target: str = "hd"):
        """Initialize PlaybackPro checker.

        Args:
            version: 'standard' or 'plus' (Plus supports H.265/HEVC)
            resolution_target: 'hd' (1080p) or '4k' for bitrate recommendations
        """
        self.version = version
        self.resolution_target = resolution_target

    def check(self, video_info: Dict[str, Any]) -> List:
        issues: List = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        bitrate = video_info.get("bitrate")
        resolution = video_info.get("resolution")

        # Check codec support
        if "prores" in codec:
            if "422" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes 422 is the recommended codec for PlaybackPro",
                        "reason": "Optimal for reliable playback in live events",
                    }
                )
            elif "4444" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes 4444 supports alpha channel",
                        "reason": "Professional quality with transparency support",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes is well-supported by PlaybackPro",
                    }
                )
        elif codec == "h264":
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "H.264 is supported by PlaybackPro",
                    "reason": "Good compatibility with variable bitrate encoding",
                }
            )
        elif codec == "hevc" or codec == "h265":
            if self.version == "plus":
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "H.265/HEVC is supported in PlaybackPro Plus",
                        "reason": "Efficient codec for high-resolution playback",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "INCOMPATIBLE",
                        "message": "H.265/HEVC requires PlaybackPro Plus",
                        "reason": "Standard version does not support HEVC",
                        "suggestion": "Upgrade to Plus or convert to ProRes/H.264",
                    }
                )
        else:
            issues.append(
                {
                    "level": "WARNING",
                    "message": f"PlaybackPro recommends ProRes or H.264, not {codec.upper()}",
                    "suggestion": "Convert to ProRes 422 for best reliability",
                }
            )

        # Check bitrate based on resolution
        if bitrate and resolution:
            width, height = resolution
            mbps = bitrate // 1_000_000

            if width >= 3840 and height >= 2160:  # 4K
                if bitrate < 30_000_000:  # Less than 30 Mbps
                    issues.append(
                        {
                            "level": "WARNING",
                            "message": f"4K bitrate ({mbps}Mbps) may be too low",
                            "reason": "PlaybackPro recommends 30-40 Mbps for 4K",
                            "suggestion": "Increase bitrate to 30-40 Mbps for 4K playback",
                        }
                    )
                elif bitrate >= 30_000_000 and bitrate <= 40_000_000:
                    issues.append(
                        {
                            "level": "COMPATIBLE",
                            "message": f"4K bitrate ({mbps}Mbps) is optimal for PlaybackPro",
                        }
                    )
            elif width >= 1920 and height >= 1080:  # 1080p/HD
                if bitrate < 15_000_000:  # Less than 15 Mbps
                    issues.append(
                        {
                            "level": "WARNING",
                            "message": f"HD bitrate ({mbps}Mbps) may be too low",
                            "reason": "PlaybackPro recommends 15-30 Mbps for HD",
                            "suggestion": "Increase bitrate to 15-30 Mbps for HD playback",
                        }
                    )
                elif bitrate >= 15_000_000 and bitrate <= 30_000_000:
                    issues.append(
                        {
                            "level": "COMPATIBLE",
                            "message": f"HD bitrate ({mbps}Mbps) is optimal for PlaybackPro",
                        }
                    )

        # Check container
        if "mov" in container or "mp4" in container:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{container.upper()} container is recommended for PlaybackPro",
                }
            )
        else:
            issues.append(
                {
                    "level": "WARNING",
                    "message": "PlaybackPro works best with MOV or MP4 containers",
                    "suggestion": "Remux to MOV container",
                }
            )

        # Storage recommendation
        if resolution:
            width, height = resolution
            if width >= 3840 and height >= 2160:  # 4K
                issues.append(
                    {
                        "level": "WARNING",
                        "message": "4K playback requires SSD storage",
                        "reason": "HDDs may not provide sufficient read speed for 4K",
                        "suggestion": "Use internal SSD or Thunderbolt SSD for reliable 4K playback",
                    }
                )

        return issues


class ProVideoPlayerChecker:
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

    def check(self, video_info: Dict[str, Any]) -> List:
        issues: List = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check for DXV (optimal for PVP)
        if "dxv" in codec:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "DXV codec works perfectly with PVP timecode features",
                    "reason": "GPU-accelerated with excellent timecode sync",
                }
            )
        # Check for HAP
        elif "hap" in codec:
            if "alpha" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "HAP Alpha provides GPU-accelerated playback with transparency",
                        "reason": "Ideal for overlays and multi-layer compositions",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "HAP codec provides excellent performance in PVP",
                        "reason": "GPU-accelerated for smooth multi-layer playback",
                    }
                )
        # Check for ProRes
        elif "prores" in codec:
            if "4444" in codec:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes 4444 supports alpha channel for transparency",
                        "reason": "Professional quality for multi-screen setups",
                    }
                )
            else:
                issues.append(
                    {
                        "level": "COMPATIBLE",
                        "message": "ProRes is fully supported by PVP",
                        "reason": "Professional codec for broadcast workflows",
                    }
                )
        # Check for H.264/H.265
        elif codec == "h264" or codec == "hevc":
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{codec.upper()} is supported by PVP",
                    "reason": "Hardware acceleration available",
                    "suggestion": "Consider DXV or HAP for better multi-layer performance",
                }
            )
        else:
            issues.append(
                {
                    "level": "WARNING",
                    "message": f"PVP may have limited support for {codec.upper()}",
                    "reason": "PVP works best with DXV, HAP, ProRes, or H.264",
                    "suggestion": "Convert to DXV for optimal timecode and multi-screen performance",
                }
            )

        # Check container
        if "mov" in container or "mp4" in container:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": f"{container.upper()} container is supported by PVP",
                }
            )

        # Note about timecode support
        if "dxv" in codec or "hap" in codec:
            issues.append(
                {
                    "level": "COMPATIBLE",
                    "message": "Timecode following and triggering fully supported",
                    "reason": "GPU codecs work excellently with PVP's timecode features",
                }
            )

        return issues


# Add these to the system registry in compatibility.py:
# "wirecast": WirecastChecker,
# "resolume": ResolumeChecker,
# "playbackpro": PlaybackProChecker,
# "provideoplayer": ProVideoPlayerChecker,
