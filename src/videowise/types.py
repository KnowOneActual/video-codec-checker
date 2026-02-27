"""Core types and base classes for compatibility checking."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CompatibilityLevel(Enum):
    """Compatibility status levels."""

    COMPATIBLE = "compatible"
    WARNING = "warning"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue or warning."""

    level: CompatibilityLevel
    message: str
    reason: Optional[str] = None
    suggestion: Optional[str] = None


class CompatibilityChecker:
    """Base class for compatibility checking."""

    def check(self, video_info: Dict[str, Any]) -> List[CompatibilityIssue]:
        """Check compatibility and return list of issues.

        Args:
            video_info: Dictionary containing video metadata

        Returns:
            List of compatibility issues
        """
        raise NotImplementedError
