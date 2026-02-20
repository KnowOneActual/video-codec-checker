"""Rule-based compatibility checking engine.

Replaces hardcoded checker classes with declarative YAML rules.
Reduces codebase from ~150KB to ~30KB while making system addition trivial.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .compatibility import CompatibilityChecker, CompatibilityIssue, CompatibilityLevel


# Module-level cache for RuleEngine instances
_ENGINE_CACHE: Dict[Optional[str], "RuleEngine"] = {}


def _get_cached_engine(config_path: Optional[Union[str, Path]] = None) -> "RuleEngine":
    """Get or create a cached RuleEngine instance.
    
    Args:
        config_path: Path to system_profiles.yaml (defaults to bundled file)
        
    Returns:
        Cached RuleEngine instance
    """
    # Convert Path to string for cache key, or use None
    cache_key = str(config_path) if config_path is not None else None
    
    if cache_key not in _ENGINE_CACHE:
        _ENGINE_CACHE[cache_key] = RuleEngine(config_path)
    
    return _ENGINE_CACHE[cache_key]


class RuleEngine:
    """Evaluates compatibility rules defined in YAML configuration."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize rule engine with system profiles.

        Args:
            config_path: Path to system_profiles.yaml (defaults to bundled file)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "system_profiles.yaml"
        elif isinstance(config_path, str):
            config_path = Path(config_path)

        with open(config_path, "r") as f:
            self.config: Dict[str, Any] = yaml.safe_load(f)

        self.systems: Dict[str, Any] = self.config.get("systems", {})
        self.profiles: Dict[str, Any] = self.config.get("profiles", {})

    def get_available_systems(self) -> List[str]:
        """Return list of all available system names."""
        return sorted(list(self.systems.keys()))

    def get_profile_systems(self, profile: str) -> List[str]:
        """Get all systems in a profile (e.g., 'editing', 'live_production')."""
        profile_data = self.profiles.get(profile, {})
        return list(profile_data.get("systems", []))

    def check_compatibility(
        self, video_info: Dict[str, Any], system: str
    ) -> List[CompatibilityIssue]:
        """Check video compatibility for a specific system.

        Args:
            video_info: Dictionary containing video metadata
            system: System to check compatibility for

        Returns:
            List of compatibility issues
        """
        system_config = self.systems.get(system.lower())
        if not system_config:
            return [
                CompatibilityIssue(
                    level=CompatibilityLevel.UNKNOWN,
                    message=f"Unknown system: {system}",
                    reason=(f"Available systems: " f"{', '.join(self.get_available_systems())}"),
                )
            ]

        issues: List[CompatibilityIssue] = []
        rules: List[Dict[str, Any]] = system_config.get("rules", [])

        # Evaluate each rule
        for rule in rules:
            if self._evaluate_condition(rule.get("condition", {}), video_info):
                issue = self._create_issue_from_rule(rule, video_info)
                issues.append(issue)

        # If no rules matched and codec is in supported list, add compatible issue
        if not issues:
            codec = video_info.get("codec", "").lower()
            codecs_config = system_config.get("codecs", {})
            supported_codecs: List[str] = codecs_config.get("supported", [])
            if codec in supported_codecs or not supported_codecs:
                issues.append(
                    CompatibilityIssue(
                        level=CompatibilityLevel.COMPATIBLE,
                        message=(
                            f"Video should be compatible with "
                            f"{system_config.get('name', system)}"
                        ),
                    )
                )

        return issues

    def _evaluate_condition(self, condition: Dict[str, Any], video_info: Dict[str, Any]) -> bool:
        """Evaluate a rule condition against video metadata.

        Args:
            condition: Condition dictionary from rule
            video_info: Video metadata

        Returns:
            True if condition matches, False otherwise
        """
        codec = video_info.get("codec", "").lower()
        profile = video_info.get("profile", "").lower()
        container = video_info.get("container", "").lower()
        resolution = video_info.get("resolution", (0, 0))
        bitrate = video_info.get("bitrate", 0)
        file_size = video_info.get("file_size", 0)
        duration = video_info.get("duration", 0)

        # Codec conditions
        if "codec_eq" in condition:
            return bool(codec == condition["codec_eq"])
        if "codec_ne" in condition:
            return bool(codec != condition["codec_ne"])
        if "codec_in" in condition:
            return bool(codec in condition["codec_in"])
        if "codec_not_in" in condition:
            return bool(codec not in condition["codec_not_in"])
        if "codec_contains" in condition:
            return bool(condition["codec_contains"] in codec)

        # Profile conditions
        if "profile_contains" in condition:
            return bool(condition["profile_contains"] in profile)
        if "profile_not_contains" in condition:
            return bool(condition["profile_not_contains"] not in profile)

        # Container conditions
        if "container_contains" in condition:
            return bool(condition["container_contains"] in container)
        if "container_not_contains" in condition:
            return bool(condition["container_not_contains"] not in container)

        # Resolution conditions
        if "resolution_gt" in condition:
            target_width, target_height = condition["resolution_gt"]
            width, height = resolution
            return bool(width > target_width or height > target_height)
        if "resolution_gte" in condition:
            target_width, target_height = condition["resolution_gte"]
            width, height = resolution
            return bool(width >= target_width and height >= target_height)

        # Bitrate conditions
        if "bitrate_gt" in condition:
            return bool(bitrate > condition["bitrate_gt"])
        if "bitrate_gte" in condition:
            return bool(bitrate >= condition["bitrate_gte"])
        if "bitrate_lt" in condition:
            return bool(bitrate < condition["bitrate_lt"])
        if "bitrate_lte" in condition:
            return bool(bitrate <= condition["bitrate_lte"])

        # File size conditions
        if "file_size_gt" in condition:
            return bool(file_size > condition["file_size_gt"])

        # Duration conditions
        if "duration_gt" in condition:
            return bool(duration > condition["duration_gt"])

        # If no condition matched, return False
        return False

    def _create_issue_from_rule(
        self, rule: Dict[str, Any], video_info: Dict[str, Any]
    ) -> CompatibilityIssue:
        """Create CompatibilityIssue from rule and video info.

        Args:
            rule: Rule dictionary with message templates
            video_info: Video metadata for template substitution

        Returns:
            CompatibilityIssue with templated messages
        """
        # Parse level
        level_str = rule.get("level", "unknown")
        level_map = {
            "compatible": CompatibilityLevel.COMPATIBLE,
            "warning": CompatibilityLevel.WARNING,
            "incompatible": CompatibilityLevel.INCOMPATIBLE,
            "unknown": CompatibilityLevel.UNKNOWN,
        }
        level = level_map.get(level_str, CompatibilityLevel.UNKNOWN)

        # Create template variables
        codec = video_info.get("codec", "").upper()
        profile = video_info.get("profile", "")
        container = video_info.get("container", "").upper()
        resolution = video_info.get("resolution", (0, 0))
        width, height = resolution
        bitrate = video_info.get("bitrate", 0)
        bitrate_mbps = bitrate // 1_000_000 if bitrate else 0

        template_vars = {
            "codec": codec,
            "profile": profile,
            "container": container,
            "width": width,
            "height": height,
            "bitrate_mbps": bitrate_mbps,
        }

        # Template substitution
        message = self._substitute_template(rule.get("message", ""), template_vars)
        reason = self._substitute_template(rule.get("reason", ""), template_vars) or None
        suggestion = self._substitute_template(rule.get("suggestion", ""), template_vars) or None

        return CompatibilityIssue(
            level=level,
            message=message,
            reason=reason,
            suggestion=suggestion,
        )

    def _substitute_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute template variables in string.

        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            String with variables substituted
        """
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


class RuleBasedChecker(CompatibilityChecker):
    """Compatibility checker that uses rule engine.

    This replaces individual checker classes (CasparCGChecker, SafariChecker, etc.)
    with a single rule-based checker.
    """

    def __init__(self, system: str, config_path: Optional[Union[str, Path]] = None):
        """Initialize rule-based checker.

        Args:
            system: System name to check compatibility for
            config_path: Optional path to custom system_profiles.yaml
        """
        self.system = system
        self.engine = _get_cached_engine(config_path)

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check video compatibility using rule engine.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues
        """
        return self.engine.check_compatibility(video_info, self.system)


# Convenience function for backward compatibility
def check_compatibility(video_info: Dict[str, Any], system: str) -> List[CompatibilityIssue]:
    """Check video compatibility for a specific system.

    This function maintains backward compatibility with existing code.

    Args:
        video_info: Dictionary containing video metadata
        system: System to check compatibility for

    Returns:
        List of compatibility issues
    """
    engine = _get_cached_engine()
    return engine.check_compatibility(video_info, system)


def get_available_systems() -> List[str]:
    """Return list of all available system names.

    Maintains backward compatibility with existing code.
    """
    engine = _get_cached_engine()
    return engine.get_available_systems()
