"""Rule engine for evaluating compatibility rules from YAML profiles.

This module replaces 31 individual checker classes with a declarative
rule-based system that evaluates conditions and generates compatibility issues.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .compatibility import CompatibilityIssue, CompatibilityLevel


class RuleEngine:
    """Evaluates compatibility rules from system profiles."""

    def __init__(self, profiles_path: Optional[Path] = None):
        """Initialize rule engine.

        Args:
            profiles_path: Path to profiles.yaml, defaults to videowise/systems/profiles.yaml
        """
        if profiles_path is None:
            profiles_path = Path(__file__).parent / "systems" / "profiles.yaml"

        with open(profiles_path, "r") as f:
            self.profiles = yaml.safe_load(f)

    def get_system_profile(self, system: str, variant: Optional[str] = None) -> Optional[Dict]:
        """Get profile for a specific system.

        Args:
            system: System name (e.g., 'casparcg', 'davinci', 'instagram')
            variant: Optional variant (e.g., 'studio', 'raspberrypi')

        Returns:
            System profile dictionary or None if not found
        """
        # Search across all categories
        for category in self.profiles.values():
            if system in category:
                profile = category[system].copy()

                # Merge variant-specific rules if specified
                if variant and "variants" in profile:
                    if variant in profile["variants"]:
                        variant_data = profile["variants"][variant]
                        # Merge variant rules
                        if "rules" in variant_data:
                            if "rules" not in profile:
                                profile["rules"] = []
                            profile["rules"].extend(variant_data["rules"])

                return profile

        return None

    def check_compatibility(
        self,
        video_info: Dict[str, Any],
        system: str,
        variant: Optional[str] = None,
    ) -> List[CompatibilityIssue]:
        """Check video compatibility against system profile.

        Args:
            video_info: Dictionary containing video metadata
            system: System to check (e.g., 'casparcg', 'premiere')
            variant: Optional variant (e.g., 'studio', 'mobile')

        Returns:
            List of compatibility issues
        """
        issues: List[CompatibilityIssue] = []
        profile = self.get_system_profile(system, variant)

        if not profile:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.UNKNOWN,
                    message=f"Unknown system: {system}",
                )
            ]

        codec = video_info.get("codec", "").lower()
        container = video_info.get("container", "").lower()

        # Check codec compatibility
        if "codecs" in profile:
            codec_issues = self._check_codecs(codec, profile["codecs"], profile.get("name", system))
            issues.extend(codec_issues)

        # Check container compatibility
        if "containers" in profile:
            container_issues = self._check_containers(
                container, profile["containers"], profile.get("name", system)
            )
            issues.extend(container_issues)

        # Evaluate custom rules
        if "rules" in profile:
            rule_issues = self._evaluate_rules(video_info, profile["rules"])
            issues.extend(rule_issues)

        # Check limits (file size, duration, etc.)
        if "limits" in profile:
            limit_issues = self._check_limits(video_info, profile["limits"])
            issues.extend(limit_issues)

        # If no issues found, add generic compatible message
        if not issues:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.COMPATIBLE,
                    message=f"Video should be compatible with {profile.get('name', system)}",
                )
            )

        return issues

    def _check_codecs(
        self, codec: str, codec_spec: Dict[str, List[str]], system_name: str
    ) -> List[CompatibilityIssue]:
        """Check codec against profile specifications."""
        issues = []

        # Check optimal codecs
        if "optimal" in codec_spec:
            for optimal in codec_spec["optimal"]:
                if optimal in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is optimal for {system_name}",
                            reason="Best performance and quality for this system",
                        )
                    )
                    return issues  # Found optimal, return early

        # Check recommended codecs
        if "recommended" in codec_spec:
            for recommended in codec_spec["recommended"]:
                if recommended in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is recommended for {system_name}",
                            reason="Good compatibility and performance",
                        )
                    )
                    return issues

        # Check supported codecs
        if "supported" in codec_spec:
            for supported in codec_spec["supported"]:
                if supported in codec:
                    issues.append(
                        CompatibilityIssue(
                            level=CompatibilityLevel.COMPATIBLE,
                            message=f"{codec.upper()} is supported by {system_name}",
                        )
                    )
                    return issues

        # Codec not in any list - generate warning
        all_codecs = []
        for key in ["optimal", "recommended", "supported"]:
            if key in codec_spec:
                all_codecs.extend(codec_spec[key])

        if all_codecs:
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.WARNING,
                    message=f"{codec.upper()} may have limited support in {system_name}",
                    reason=f"Supported codecs: {', '.join(all_codecs)}",
                    suggestion=f"Consider converting to {all_codecs[0].upper()}",
                )
            )

        return issues

    def _check_containers(
        self, container: str, container_spec: Dict[str, List[str]], system_name: str
    ) -> List[CompatibilityIssue]:
        """Check container format against profile specifications."""
        issues = []

        if "required" in container_spec:
            required = container_spec["required"]
            if not any(req in container for req in required):
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.INCOMPATIBLE,
                        message=f"{system_name} requires {' or '.join(required).upper()} container",
                        suggestion=f"Remux to {required[0].upper()} container",
                    )
                )
        elif "preferred" in container_spec:
            preferred = container_spec["preferred"]
            if any(pref in container for pref in preferred):
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=f"{container.upper()} container is preferred by {system_name}",
                    )
                )
            else:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"{system_name} works best with {' or '.join(preferred).upper()} container",
                        suggestion=f"Consider remuxing to {preferred[0].upper()}",
                    )
                )

        return issues

    def _evaluate_rules(
        self, video_info: Dict[str, Any], rules: List[Dict[str, Any]]
    ) -> List[CompatibilityIssue]:
        """Evaluate custom rules against video info."""
        issues = []

        for rule in rules:
            # Simple codec match
            if "codec" in rule and "condition" not in rule:
                codec = video_info.get("codec", "").lower()
                rule_codecs = rule["codec"] if isinstance(rule["codec"], list) else [rule["codec"]]

                if any(rc in codec for rc in rule_codecs):
                    issues.append(
                        CompatibilityIssue(
                            level=self._parse_level(rule.get("level", "compatible")),
                            message=rule.get("message", ""),
                            reason=rule.get("reason"),
                            suggestion=rule.get("suggestion"),
                        )
                    )

            # Conditional expression
            elif "condition" in rule:
                if self._evaluate_condition(rule["condition"], video_info):
                    issues.append(
                        CompatibilityIssue(
                            level=self._parse_level(rule.get("level", "warning")),
                            message=rule.get("message", ""),
                            reason=rule.get("reason"),
                            suggestion=rule.get("suggestion"),
                        )
                    )

        return issues

    def _evaluate_condition(self, condition: str, video_info: Dict[str, Any]) -> bool:
        """Evaluate a condition string against video info.

        Supports expressions like:
        - codec == 'h264'
        - bitrate > 100000000
        - resolution[0] >= 3840
        - codec in ['h264', 'hevc']
        """
        try:
            # Create a safe namespace with video_info variables
            namespace = {
                "codec": video_info.get("codec", "").lower(),
                "container": video_info.get("container", "").lower(),
                "bitrate": video_info.get("bitrate", 0),
                "resolution": video_info.get("resolution", (0, 0)),
                "frame_rate": video_info.get("frame_rate"),
                "profile": video_info.get("profile", "").lower(),
                "file_size": video_info.get("file_size", 0),
            }

            # Evaluate the condition
            return eval(condition, {"__builtins__": {}}, namespace)
        except Exception:
            # If evaluation fails, return False (don't apply rule)
            return False

    def _check_limits(
        self, video_info: Dict[str, Any], limits: Dict[str, Any]
    ) -> List[CompatibilityIssue]:
        """Check video against system limits."""
        issues = []

        # Check file size
        file_size = video_info.get("file_size", 0)
        if "max_file_size" in limits and file_size > limits["max_file_size"]:
            size_mb = file_size // (1024 * 1024)
            limit_mb = limits["max_file_size"] // (1024 * 1024)
            issues.append(
                CompatibilityIssue(
                    level=CompatibilityLevel.INCOMPATIBLE,
                    message=f"File size {size_mb}MB exceeds limit of {limit_mb}MB",
                    suggestion="Compress video to reduce file size",
                )
            )

        # Check resolution
        resolution = video_info.get("resolution")
        if resolution and "max_resolution" in limits:
            max_res = limits["max_resolution"]
            if resolution[0] > max_res[0] or resolution[1] > max_res[1]:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Resolution {resolution[0]}x{resolution[1]} exceeds maximum {max_res[0]}x{max_res[1]}",
                        suggestion=f"Downscale to {max_res[0]}x{max_res[1]}",
                    )
                )

        # Check bitrate range
        bitrate = video_info.get("bitrate")
        if bitrate and "optimal_bitrate_range" in limits:
            min_br, max_br = limits["optimal_bitrate_range"]
            if bitrate < min_br or bitrate > max_br:
                min_mbps = min_br // 1_000_000
                max_mbps = max_br // 1_000_000
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.WARNING,
                        message=f"Bitrate outside optimal range of {min_mbps}-{max_mbps} Mbps",
                        suggestion=f"Adjust bitrate to {min_mbps}-{max_mbps} Mbps for best results",
                    )
                )

        return issues

    def _parse_level(self, level_str: str) -> CompatibilityLevel:
        """Parse level string to CompatibilityLevel enum."""
        level_map = {
            "compatible": CompatibilityLevel.COMPATIBLE,
            "warning": CompatibilityLevel.WARNING,
            "incompatible": CompatibilityLevel.INCOMPATIBLE,
            "unknown": CompatibilityLevel.UNKNOWN,
        }
        return level_map.get(level_str.lower(), CompatibilityLevel.UNKNOWN)

    def list_systems(self) -> List[str]:
        """Get list of all available system names."""
        systems = []
        for category in self.profiles.values():
            systems.extend(category.keys())
        return sorted(systems)

    def get_system_info(self, system: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a system."""
        profile = self.get_system_profile(system)
        if not profile:
            return None

        return {
            "name": profile.get("name", system),
            "category": profile.get("category", "unknown"),
            "variants": list(profile.get("variants", {}).keys()),
            "optimal_codecs": profile.get("codecs", {}).get("optimal", []),
        }
