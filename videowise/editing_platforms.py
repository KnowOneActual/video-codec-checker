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
    RAW_FORMATS = ["braw", "r3d", "arriraw"]  # Camera RAW formats
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "mjpeg",
        "av1",  # Studio 18.5+
        "braw",  # Blackmagic RAW
    }

    def __init__(self, version: str = "studio", platform: str = "windows"):
        """Initialize DaVinci Resolve checker.

        Args:
            version: 'free' or 'studio' (Studio has more codec support)
            platform: 'windows', 'mac_intel', or 'mac_apple_silicon' for platform-specific advice
        """
        self.version = version
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
        bit_depth = video_info.get("bit_depth")

        # Check for BRAW (Blackmagic RAW)
        if "braw" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="BRAW (Blackmagic RAW) is natively supported in DaVinci Resolve",
                    reason="RAW format with excellent color grading flexibility",
                )
            )
            return issues  # BRAW is complete, no other checks needed

        # Check for optimal editing codecs - DNxHD/DNxHR
        if "dnxhd" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHD is optimal for HD editing in DaVinci Resolve",
                    reason="Intraframe codec with low CPU overhead for timeline playback",
                )
            )
        elif "dnxhr" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHR is optimal for 4K and higher resolution editing",
                    reason="Scalable intraframe codec ideal for color grading workflows",
                )
            )

        # Check for ProRes with platform-specific advice
        elif "prores" in codec:
            if self.platform == "mac_apple_silicon":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} benefits from hardware acceleration on Apple Silicon",
                        reason="M-series chips have dedicated ProRes encode/decode hardware",
                    )
                )
            elif self.platform == "mac_intel":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is well-supported on Intel Mac",
                        reason="Native ProRes support on macOS for editing workflows",
                    )
                )
            else:  # Windows
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} is well-supported in DaVinci Resolve",
                        reason="Professional codec for editing and grading",
                    )
                )

            # Check for 10-bit ProRes variants
            if "422hq" in codec or "4444" in codec:
                if bit_depth == 10 or "422hq" in codec or "4444" in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message="10-bit color depth provides excellent grading headroom",
                            reason="Essential for professional color correction in Resolve",
                        )
                    )

        # Check for H.264/H.265
        elif codec in ["h264", "hevc"]:
            if self.version == "studio":
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{codec.upper()} has GPU hardware decode in Resolve Studio",
                        reason="Hardware acceleration available with Studio license",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{codec.upper()} requires CPU decode in Resolve Free (consider re-encoding)",
                        reason="Free version lacks GPU decode, causing timeline stuttering",
                        suggestion="Transcode to DNxHR or ProRes, or upgrade to Studio",
                    )
                )

            # Additional H.264/H.265 warning for heavy editing
            if resolution:
                width, height = resolution
                if width >= 1920 and height >= 1080:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"{codec.upper()} may require transcoding for intensive editing/grading",
                            reason="Long-GOP compression makes frame-accurate work slower",
                            suggestion="Consider generating optimized media (DNxHR/ProRes)",
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

        # Check container format
        if "mov" in container or "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is well-supported by Resolve",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container works well with Resolve",
                )
            )

        return issues


class AdobePremiereProChecker(CompatibilityChecker):
    """Compatibility checker for Adobe Premiere Pro.

    Premiere Pro is industry-standard NLE with broad codec support.
    Hardware acceleration varies by GPU (Intel QuickSync, NVIDIA NVENC, AMD VCE).
    """

    OPTIMAL_CODECS = ["dnxhd", "dnxhr", "prores"]
    HARDWARE_ACCELERATED = ["h264", "hevc"]  # With compatible GPU
    RAW_FORMATS = ["r3d", "arriraw", "braw"]  # Camera RAW
    CAMERA_CODECS = ["xavc", "xdcam"]  # Sony formats
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "mjpeg",
        "av1",
        "vp9",
        "r3d",
        "xavc",
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
        frame_rate = video_info.get("frame_rate")
        profile = video_info.get("profile", "").lower()
        level = video_info.get("level", "")

        # Check for RED RAW (R3D)
        if "r3d" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="RED RAW (R3D) is natively supported in Premiere Pro",
                    reason="Full RAW workflow with color controls in Lumetri",
                )
            )
            return issues  # RAW is complete, return early

        # Check for XAVC (Sony)
        if "xavc" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="XAVC is natively supported in Premiere Pro",
                    reason="Sony camera format with excellent quality",
                )
            )

        # Check for optimal intraframe codecs
        if "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is native in Premiere Pro for smooth editing",
                    reason="Intraframe codec enables frame-accurate scrubbing",
                )
            )
        elif "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is native in Premiere Pro",
                    reason="Professional codec with broad compatibility",
                )
            )

        # Check for H.264/H.265 with Mercury Playback Engine
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} benefits from Mercury Playback Engine GPU acceleration",
                    reason="Hardware decode available with compatible GPU",
                    suggestion="Enable GPU acceleration in Project Settings",
                )
            )

            # Check H.264 level for 4K
            if codec == "h264" and resolution:
                width, height = resolution
                if (width >= 3840 or height >= 2160) and level:
                    if "5.1" in str(level) or "5.2" in str(level):
                        issues.append(
                            CompatibilityIssue(
                                level=CompatibilityLevel.COMPATIBLE,
                                message=f"H.264 Level {level} is appropriate for 4K delivery",
                                reason="Level 5.1+ required for UHD resolution",
                            )
                        )

            # High bitrate warning for 4K
            if bitrate and resolution:
                width, height = resolution
                if (width >= 3840 or height >= 2160) and bitrate > 100_000_000:
                    mbps = bitrate // 1_000_000
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message=f"High bitrate 4K {codec.upper()} ({mbps}Mbps) may impact timeline performance",
                            reason="Very high bitrate can cause stuttering during playback",
                            suggestion="Consider creating proxies or using intraframe codec",
                        )
                    )

        # Check for Variable Frame Rate (VFR)
        if frame_rate and isinstance(frame_rate, str) and "variable" in frame_rate.lower():
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="Variable Frame Rate (VFR) can cause sync issues in Premiere",
                    reason="VFR footage may drift out of sync on timeline",
                    suggestion="Conform to CFR (Constant Frame Rate) before editing",
                )
            )

        # Check for 8K resolution - proxy workflow
        if resolution:
            width, height = resolution
            if width >= 7680 or height >= 4320:  # 8K
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message="8K footage requires proxy workflow for smooth editing",
                        reason="Full-res 8K playback is extremely demanding",
                        suggestion="Create proxies via Ingest Settings or Proxy menu",
                    )
                )

        # Check container format
        if "mov" in container or "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{container.upper()} container is well-supported by Premiere",
                )
            )
        elif "mp4" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MP4 container is fully supported",
                )
            )

        # Note about Dynamic Link with After Effects
        if "prores" in codec or "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Intraframe codec works seamlessly with Dynamic Link to After Effects",
                    reason="No transcoding needed when round-tripping to AE",
                )
            )

        return issues


class FinalCutProChecker(CompatibilityChecker):
    """Compatibility checker for Final Cut Pro (Mac only).

    Final Cut Pro is Apple's professional video editor with native
    ProRes support and hardware acceleration on Apple Silicon.
    """

    NATIVE_CODECS = ["prores"]  # Hardware accelerated on Apple Silicon
    OPTIMIZED_FORMATS = ["prores_proxy", "prores_lt"]  # For Optimized Media
    RAW_FORMATS = ["prores_raw"]  # ProRes RAW
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "prores_raw",
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

        # Check for ProRes RAW
        if "prores_raw" in codec or ("prores" in codec and "raw" in codec):
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes RAW is natively supported in Final Cut Pro",
                    reason="Full RAW workflow with Apple Silicon hardware acceleration",
                )
            )
            return issues  # RAW is complete

        # Check for ProRes (native codec)
        if "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is the native codec for Final Cut Pro",
                    reason="Hardware acceleration on Apple Silicon provides excellent performance",
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
            elif "422" in codec:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="ProRes 422 is optimal for the Magnetic Timeline",
                        reason="Balanced quality and performance for editing",
                    )
                )

        # Check for H.264/H.265 - triggers Optimized Media
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} benefits from hardware decode on Apple Silicon",
                    reason="M-series chips have dedicated video decode engines",
                )
            )

            # Optimized Media workflow for HEVC
            if codec == "hevc" or (bitrate and bitrate > 50_000_000):
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{codec.upper()} will prompt for Optimized Media workflow",
                        reason="FCP transcodes to ProRes for smoother timeline performance",
                        suggestion="Allow FCP to create optimized media or pre-transcode",
                    )
                )

            # Background rendering for complex footage
            if resolution:
                width, height = resolution
                if (width >= 3840 or height >= 2160) or (bitrate and bitrate > 80_000_000):
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.WARNING,
                            message="Enable Background Rendering for smooth playback of complex footage",
                            reason="4K or high-bitrate footage benefits from pre-rendering",
                            suggestion="Final Cut Pro > Preferences > Playback > Background render",
                        )
                    )

        # Check for DNxHD/DNxHR
        elif "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} is supported by Final Cut Pro",
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
                    message=f"{codec.upper()} may require optimization in Final Cut Pro",
                    reason="FCP works best with ProRes codecs",
                    suggestion="Transcode to ProRes 422 or let FCP create optimized media",
                )
            )

        # Check container format (MOV/QuickTime preferred)
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
                    message="MP4 container is supported",
                    reason="Good for H.264/H.265 footage from cameras",
                )
            )

        return issues


class AvidMediaComposerChecker(CompatibilityChecker):
    """Compatibility checker for Avid Media Composer.

    Media Composer is the industry standard for film and broadcast editing.
    Very strict about codec and container format conformity.
    """

    NATIVE_CODECS = ["dnxhd", "dnxhr"]  # Avid's proprietary codecs
    REQUIRED_CONTAINER = "mxf"  # Avid prefers MXF (Material Exchange Format)
    SUPPORTED_CODECS = {
        "dnxhd",
        "dnxhr",
        "h264",  # Via AMA
        "prores",  # Via AMA or plugin
        "xavc",  # Via AMA
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
        audio_codec = video_info.get("audio_codec", "").lower()
        mxf_structure = video_info.get("mxf_structure", "").lower()

        # Check for DNxHD/DNxHR (native codecs)
        if "dnxhd" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHD is Avid's native codec and optimal for HD editing",
                    reason="Best performance and collaboration in Avid workflows",
                )
            )
        elif "dnxhr" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="DNxHR is Avid's native codec for all resolutions including 4K",
                    reason="Scalable codec for HD, UHD, 4K, and higher resolutions",
                )
            )

        # Check for ProRes (collaboration with Final Cut)
        elif "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes is compatible via AMA for collaboration with Final Cut Pro",
                    reason="AMA linking allows ProRes import for cross-platform workflows",
                    suggestion="For best performance, transcode to DNxHR on import",
                )
            )

        # Check for H.264 (AMA only)
        elif codec == "h264":
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="H.264 requires AMA (Avid Media Access) linking and transcoding",
                    reason="AMA links to files without import; transcode for collaboration",
                    suggestion="Transcode to DNxHR SQ during import for better performance",
                )
            )

        # Check for third-party codecs requiring codec pack
        elif "xavc" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="XAVC requires Avid codec pack or AMA for Sony camera workflows",
                    reason="Third-party format supported via AMA linking",
                    suggestion="Consider transcoding to DNxHR for native performance",
                )
            )

        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"{codec.upper()} is not supported by Avid Media Composer",
                    reason="Avid requires DNxHD/DNxHR for native editing",
                    suggestion="Transcode to DNxHR SQ or HQ before importing",
                )
            )

        # Check container format (MXF strongly preferred)
        if "mxf" in container:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="MXF is Avid's native container for broadcast workflows",
                    reason="Material Exchange Format is industry standard",
                )
            )

            # Check MXF structure (OP1a preferred)
            if mxf_structure and "op1a" in mxf_structure:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="OP1a MXF structure is optimal for Avid MediaCentral collaboration",
                        reason="Operational Pattern 1a ensures maximum compatibility",
                    )
                )

        elif "mov" in container and "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="DNxHD/DNxHR in MOV container: MXF is preferred for Avid workflows",
                    reason="MOV with DNxHD works but MXF ensures full Avid compatibility",
                    suggestion="Rewrap to MXF: ffmpeg -i input.mov -c copy output.mxf",
                )
            )

        # Check audio codec for broadcast compliance
        if audio_codec and "pcm" in audio_codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="PCM audio is broadcast-compliant and recommended for Avid",
                    reason="Uncompressed audio ensures maximum quality and compatibility",
                )
            )

        return issues


class AfterEffectsChecker(CompatibilityChecker):
    """Compatibility checker for Adobe After Effects.

    After Effects is industry-standard compositing and motion graphics software.
    Prefers image sequences and intraframe codecs for timeline performance.
    """

    OPTIMAL_CODECS = ["prores", "dnxhd", "dnxhr"]  # Intraframe
    ALPHA_CODECS = ["prores4444", "qtrle", "png"]  # Transparency support
    LOSSLESS_CODECS = ["qtrle"]  # QuickTime Animation (lossless)
    SUPPORTED_CODECS = {
        "h264",
        "hevc",
        "prores",
        "dnxhd",
        "dnxhr",
        "qtrle",  # QuickTime Animation codec
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

        # Check for ProRes 4444 (alpha channel)
        if "prores4444" in codec or ("prores" in codec and "4444" in codec):
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="ProRes 4444 is ideal for After Effects with alpha channel support",
                    reason="Best quality for motion graphics with transparency",
                )
            )

        # Check for QuickTime Animation codec (lossless alpha)
        elif "qtrle" in codec or "animation" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Animation codec provides lossless output with alpha channel",
                    reason="QuickTime Animation is lossless with full alpha support",
                    suggestion="Consider ProRes 4444 for smaller file sizes with alpha",
                )
            )

        # Check for ProRes (general)
        elif "prores" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} provides excellent RAM preview performance",
                    reason="Intraframe codec enables fast scrubbing in timeline",
                )
            )

        # Check for DNxHD/DNxHR
        elif "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"{codec.upper()} works well in After Effects",
                    reason="Intraframe codec for smooth playback",
                )
            )

        # Check for PNG/image sequences (optimal for VFX)
        elif "png" in codec or "tiff" in codec or "exr" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Image sequences are ideal for After Effects motion graphics",
                    reason="Frame-accurate scrubbing and no GOP issues",
                )
            )

        # Check for H.264/H.265 (not recommended)
        elif codec in ["h264", "hevc"]:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} should be avoided for intermediate renders in After Effects",
                    reason="Interframe codecs cause slow RAM previews and scrubbing",
                    suggestion="Use ProRes 422, PNG sequence, or Animation codec instead",
                )
            )

            # Recommend PNG sequence for motion graphics
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message="For motion graphics work, PNG sequence is recommended over video files",
                    reason="Sequences provide frame-accurate editing and alpha support",
                    suggestion="Render as PNG sequence for maximum flexibility",
                )
            )

            # Check for alpha channel preservation
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} does not support alpha channel (transparency)",
                    reason="H.264/H.265 cannot preserve transparency for overlays",
                    suggestion="Use ProRes 4444, Animation codec, or PNG sequence for alpha",
                )
            )

        else:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may have limited support in After Effects",
                    reason="AE works best with intraframe codecs or image sequences",
                    suggestion="Transcode to ProRes 422 or convert to PNG sequence",
                )
            )

        # Note about Dynamic Link with Premiere Pro
        if "prores" in codec or "dnxh" in codec:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message="Intraframe codec works seamlessly with Dynamic Link to Premiere Pro",
                    reason="No transcoding needed when using Dynamic Link",
                )
            )

        # Check for GPU acceleration note
        if resolution:
            width, height = resolution
            if width >= 3840 or height >= 2160:  # 4K+
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message="4K compositions: ensure GPU acceleration is enabled for better performance",
                        reason="GPU effects and renders significantly speed up workflows",
                        suggestion="Project Settings > Video Rendering and Effects > Mercury GPU",
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
                    message="MP4 container is supported for delivery",
                    reason="Standard format for H.264/H.265 output",
                )
            )

        return issues
