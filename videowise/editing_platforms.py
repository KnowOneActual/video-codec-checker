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
                        message=f"{codec.UPPER()} is optimal for Resolve editing",
                        reason="Intraframe codec with low CPU overhead for timeline playback",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} provides excellent editing performance",
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
                            message=f"{codec.UPPER()} is excellent for proxy workflows",
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
                            message=f"{codec.UPPER()} is optimal for Resolve{hw_msg}",
                            reason="Native support on Apple Silicon with M-series chips",
                        )
                    )
            else:  # Windows
                if "proxy" in codec or "lt" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.UPPER()} is excellent for proxy workflows",
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
                            message=f"{codec.UPPER()} is optimal for Resolve",
                            reason="Professional codec with good quality",
                        )
                    )
        # Check for H.264/H.265 (requires Studio for GPU decode)
        elif codec in ["h264", "hevc"]:
            if self.version == "studio":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} has GPU decode in Resolve Studio",
                        reason="Hardware acceleration available with Studio license",
                        suggestion="Consider generating optimized media for complex timelines",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{codec.UPPER()} will use CPU decode in Resolve Free",
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
                    message=f"{codec.UPPER()} may have limited support in Resolve",
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
                    message=f"{container.UPPER()} container is well-supported by Resolve",
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


class AdobePremiereProChecker(CompatibilityChecker):
    """Compatibility checker for Adobe Premiere Pro.

    Premiere Pro is industry-standard NLE with broad codec support.
    Hardware acceleration varies by GPU (Intel QuickSync, NVIDIA NVENC, AMD VCE).
    """

    OPTIMAL_CODECS = ["dnxhd", "dnxhr", "prores"]
    HARDWARE_ACCELERATED = ["h264", "hevc"]  # With compatible GPU
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "mjpeg",
        "av1",
        "vp9",
    }

    def __init__(self, platform: str = "windows"):
        """Initialize Premiere Pro checker.

        Args:
            platform: 'windows' or 'mac' for platform-specific advice
        """
        self.platform = platform

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Adobe Premiere Pro.

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

        # Check for optimal intraframe codecs
        if "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.UPPER()} provides excellent scrubbing performance",
                    reason="Intraframe codec enables smooth timeline playback",
                )
            )
        elif "prores" in codec:
            if self.platform == "mac":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} is native on macOS with hardware acceleration",
                        reason="Apple Silicon Macs have ProRes encode/decode in hardware",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{codec.UPPER()} on Windows requires activation/payment",
                        reason="ProRes decode on Windows requires license from Adobe",
                        suggestion="Use DNxHR on Windows for similar workflow",
                    )
                )
        # Check for H.264/H.265 (hardware accelerated)
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.UPPER()} has hardware acceleration support",
                    reason="GPU decode available with Intel/NVIDIA/AMD",
                    suggestion="Enable hardware decoding in Project Settings > General",
                )
            )

            # Warn about scrubbing performance
            if bitrate and bitrate > 50_000_000:  # 50 Mbps
                mbps = bitrate // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"High bitrate {codec.UPPER()} ({mbps}Mbps) may stutter when scrubbing",
                        reason="Interframe codecs don't scrub as smoothly as intraframe",
                        suggestion="Consider transcoding to DNxHR for editing",
                    )
                )
        # Check for AV1
        elif codec == "av1":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="AV1 support is limited in Premiere Pro",
                    reason="AV1 decode is CPU-intensive without GPU support",
                    suggestion="Transcode to H.264 or DNxHR for better performance",
                )
            )
        # Check for VP9
        elif codec == "vp9":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="VP9 has limited hardware acceleration in Premiere",
                    reason="VP9 is primarily CPU-decoded",
                    suggestion="Transcode to H.264 or DNxHR for timeline performance",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.UPPER()} may have limited support in Premiere",
                    reason="Premiere works best with intraframe or GPU-accelerated codecs",
                    suggestion="Transcode to DNxHR or H.264 for best compatibility",
                )
            )

        # Check resolution for performance
        if resolution:
            width, height = resolution
            if width >= 3840 or height >= 2160:  # 4K+
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="4K+ footage: use Ingest Settings to create proxies",
                        reason="Proxies enable smooth playback on moderate hardware",
                        suggestion="File > Project Settings > Ingest Settings > Ingest",
                    )
                )
            if (width >= 7680 or height >= 4320) and codec not in self.OPTIMAL_CODECS:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="8K footage requires intraframe codec for smooth playback",
                        reason="8K H.264/H.265 is extremely demanding to decode",
                        suggestion="Transcode to DNxHR 444 or ProRes 422 HQ",
                    )
                )

        # Check container format
        if "mov" in container or "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.UPPER()} container is well-supported by Premiere",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container is fully supported by Premiere",
                    reason="Universal container for H.264/H.265",
                )
            )

        # Note about Dynamic Link with After Effects
        if "prores" in codec or "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Intraframe codecs work perfectly with Dynamic Link to After Effects",
                    reason="No re-encoding needed when sending to AE",
                )
            )

        return issues


class FinalCutProChecker(CompatibilityChecker):
    """Compatibility checker for Final Cut Pro (Mac only).

    Final Cut Pro is Apple's professional video editor with native
    ProRes support and hardware acceleration on Apple Silicon.
    """

    NATIVE_CODECS = ["prores"]  # Hardware accelerated on Apple Silicon
    OPTIMIZED_FORMATS = ["prores_proxy", "prores_lt", "h264"]  # For Optimized Media
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "av1",
    }

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Final Cut Pro.

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

        # Check for ProRes (native codec)
        if "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.UPPER()} is the native codec for Final Cut Pro",
                    reason="Hardware acceleration on Apple Silicon (M1/M2/M3/M4)",
                )
            )

            if "proxy" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes Proxy is ideal for laptop editing",
                        reason="Low bitrate enables smooth playback on MacBook Air/Pro",
                    )
                )
            elif "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 supports alpha channel workflows",
                        reason="Essential for compositing with transparency",
                    )
                )
        # Check for H.264/H.265
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.UPPER()} will trigger 'Create Optimized Media' prompt",
                    reason="FCP transcodes H.264/H.265 to ProRes for smooth editing",
                    suggestion="Allow FCP to create optimized media, or pre-transcode to ProRes",
                )
            )

            # Additional warning for high bitrate
            if bitrate and bitrate > 100_000_000:  # 100 Mbps
                mbps = bitrate // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"High bitrate {codec.UPPER()} ({mbps}Mbps) will definitely need optimization",
                        reason="Interframe codecs at high bitrate cause stuttering in FCP",
                        suggestion="Transcode to ProRes 422 before importing",
                    )
                )
        # Check for DNxHD/DNxHR
        elif "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.UPPER()} is supported by Final Cut Pro",
                    reason="Avid codecs work in FCP but ProRes is more optimized",
                    suggestion="Consider transcoding to ProRes for best performance",
                )
            )
        # Check for AV1
        elif codec == "av1":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="AV1 support is limited in Final Cut Pro",
                    reason="AV1 decode is CPU-intensive on Apple Silicon",
                    suggestion="Transcode to ProRes 422 for smooth timeline playback",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.UPPER()} may require optimization in Final Cut Pro",
                    reason="FCP works best with ProRes codecs",
                    suggestion="Transcode to ProRes 422 or let FCP create optimized media",
                )
            )

        # Check resolution for proxy recommendations
        if resolution:
            width, height = resolution
            if width >= 3840 or height >= 2160:  # 4K+
                if "prores" not in codec or "proxy" not in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message="4K+ footage: enable Proxy Media workflow",
                            reason="Proxy media enables smooth editing on MacBook Air/Pro",
                            suggestion="File > Transcode Media > Create proxy media (ProRes Proxy)",
                        )
                    )

        # Check container format (MOV preferred)
        if "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MOV (QuickTime) is the native container for Final Cut Pro",
                    reason="Seamless integration with macOS and ProRes",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container is supported by Final Cut Pro",
                    reason="Good for H.264/H.265 footage from cameras",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Final Cut Pro works best with MOV or MP4 containers",
                    suggestion="Remux to MOV for best compatibility",
                )
            )

        return issues


class AvidMediaComposerChecker(CompatibilityChecker):
    """Compatibility checker for Avid Media Composer.

    Media Composer is the industry standard for film and broadcast editing.
    Very strict about codec and frame rate conformity within projects.
    """

    NATIVE_CODECS = ["dnxhd", "dnxhr"]  # Avid's proprietary codecs
    REQUIRED_CONTAINER = "mxf"  # Avid prefers MXF (Material Exchange Format)
    SUPPORTED_CODECS = {
        "dnxhd",
        "dnxhr",
        "h264",  # Via AMA
        "prores",  # Via AMA or plugin
    }

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Avid Media Composer.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        frame_rate = video_info.get("frame_rate")

        # Check for DNxHD/DNxHR (native codecs)
        if "dnxhd" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHD is Avid's native codec for HD resolution",
                    reason="Best performance and collaboration in Avid workflows",
                )
            )
        elif "dnxhr" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHR is Avid's native codec for all resolutions",
                    reason="Supports HD, UHD, 4K, and higher resolutions",
                )
            )

            # Check DNxHR quality level
            if "lb" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="DNxHR LB is suitable for proxy workflows",
                        reason="Low bandwidth variant for offline editing",
                    )
                )
            elif "sq" in codec or "hq" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} is ideal for online editing",
                        reason="Standard/High Quality for broadcast delivery",
                    )
                )
            elif "hqx" in codec or "444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} is for high-end finishing",
                        reason="10-bit 4:4:4 for VFX and color grading",
                    )
                )
        # Check for H.264 (AMA only)
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="H.264 requires AMA (Avid Media Access) linking",
                    reason="AMA links to files without import; not ideal for collaboration",
                    suggestion="Transcode to DNxHR SQ during import for better performance",
                )
            )
        # Check for ProRes
        elif "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="ProRes requires AMA or plugin in Avid",
                    reason="ProRes not natively supported; links via AMA",
                    suggestion="Transcode to DNxHR on import for Avid collaboration",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"{codec.UPPER()} is not supported by Avid Media Composer",
                    reason="Avid requires DNxHD/DNxHR for native editing",
                    suggestion="Transcode to DNxHR SQ or HQ before importing",
                )
            )

        # Check container format (MXF required for native workflows)
        if "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MXF is Avid's required container for native media",
                    reason="Material Exchange Format is broadcast standard",
                )
            )
        elif "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="MOV container requires AMA linking in Avid",
                    reason="MOV files are linked, not imported natively",
                    suggestion="Wrap DNxHR in MXF container for native Avid workflow",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Avid works best with MXF container for DNxHD/DNxHR",
                    suggestion="Wrap in MXF: ffmpeg -i input -c copy output.mxf",
                )
            )

        # Check frame rate conformity
        if frame_rate:
            try:
                fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 24
                if fps not in [23.976, 24, 25, 29.97, 30, 50, 59.94, 60]:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"Non-standard frame rate ({fps}fps) may cause issues",
                            reason="Avid projects lock to specific frame rates",
                            suggestion="Conform to 23.976, 24, 25, 29.97, or 59.94fps",
                        )
                    )
            except (ValueError, TypeError):
                pass

        # Check resolution with DNxHD (HD only)
        if resolution and "dnxhd" in codec:
            width, height = resolution
            if width > 1920 or height > 1080:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="DNxHD only supports HD resolution (1920x1080 max)",
                        reason="DNxHD is limited to 1080p and below",
                        suggestion="Use DNxHR for 4K or higher resolutions",
                    )
                )

        return issues


class AfterEffectsChecker(CompatibilityChecker):
    """Compatibility checker for Adobe After Effects.

    After Effects is industry-standard compositing and motion graphics software.
    Prefers image sequences and intraframe codecs for timeline performance.
    """

    OPTIMAL_CODECS = ["prores", "dnxhd", "dnxhr"]  # Intraframe
    ALPHA_CODECS = ["prores4444", "png_sequence"]  # Transparency support
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "animation",  # QuickTime Animation codec
        "png",  # Image sequence
    }

    def __init__(self, workflow: str = "motion_graphics"):
        """Initialize After Effects checker.

        Args:
            workflow: 'motion_graphics' or 'vfx' for workflow-specific advice
        """
        self.workflow = workflow

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility for Adobe After Effects.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues found
        """
        issues: List[CompatibilityIssue] = []
        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution")
        frame_rate = video_info.get("frame_rate")

        # Check for optimal codecs
        if "prores" in codec:
            if "4444" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 4444 is ideal for After Effects with alpha channel",
                        reason="Best quality for motion graphics with transparency",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.UPPER()} provides excellent RAM preview performance",
                        reason="Intraframe codec enables fast scrubbing in timeline",
                    )
                )
        elif "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.UPPER()} works well in After Effects",
                    reason="Intraframe codec for smooth playback",
                )
            )
        # Check for H.264/H.265
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.UPPER()} will be slow for RAM previews and scrubbing",
                    reason="Interframe codecs require decoding entire GOPs",
                    suggestion="Transcode to ProRes 422 or image sequence for better performance",
                )
            )

            # Additional warning for high resolution
            if resolution:
                width, height = resolution
                if width >= 3840 or height >= 2160:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"4K {codec.UPPER()} will be extremely slow in After Effects",
                            reason="High resolution + interframe codec = poor scrubbing",
                            suggestion="Convert to 4K ProRes 422 or PNG sequence",
                        )
                    )
        # Check for image sequences (optimal for VFX)
        elif "png" in codec or "tiff" in codec or "exr" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Image sequences are ideal for After Effects",
                    reason="Frame-accurate scrubbing and no GOP issues",
                )
            )
        # Check for Animation codec
        elif "animation" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="QuickTime Animation codec supports alpha channel",
                    reason="Good for alpha channel workflows, but large file sizes",
                    suggestion="Consider ProRes 4444 for smaller files with alpha",
                )
            )
        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.UPPER()} may have limited support in After Effects",
                    reason="AE works best with intraframe codecs or image sequences",
                    suggestion="Transcode to ProRes 422 or convert to PNG sequence",
                )
            )

        # Check for alpha channel workflow
        if self.workflow == "motion_graphics":
            if codec not in ["prores4444", "animation", "png"]:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="Motion graphics workflow: consider alpha channel codec",
                        reason="ProRes 4444 or PNG sequence needed for transparency",
                        suggestion="Render with alpha: ProRes 4444 or PNG sequence",
                    )
                )

        # Check frame rate for RAM preview
        if frame_rate:
            try:
                fps = float(frame_rate) if isinstance(frame_rate, (int, float)) else 30
                if fps > 60:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"High frame rate ({fps}fps) increases RAM preview times",
                            reason="More frames = longer render times for effects",
                            suggestion="Consider working at 30fps and conforming later",
                        )
                    )
            except (ValueError, TypeError):
                pass

        # Check resolution for performance
        if resolution:
            width, height = resolution
            if width >= 3840 or height >= 2160:  # 4K+
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="4K+ comps: enable Multi-Frame Rendering for better performance",
                        reason="Multi-core rendering speeds up previews and renders",
                        suggestion="Edit > Preferences > Memory & Performance > Enable",
                    )
                )

        # Check container format
        if "mov" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MOV (QuickTime) is well-supported in After Effects",
                    reason="Native container for ProRes and Animation codecs",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container is supported for H.264/H.265",
                    reason="Standard delivery format",
                )
            )

        return issues
