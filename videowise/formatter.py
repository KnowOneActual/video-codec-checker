"""Formatter for enhanced compatibility issue explanations."""

from typing import Dict, Optional

from videowise.compatibility import CompatibilityIssue, CompatibilityLevel


class ExplanationFormatter:
    """Format compatibility issues with enhanced explanations."""

    # Severity icons and colors
    SEVERITY_INFO = {
        CompatibilityLevel.COMPATIBLE: {
            "icon": "✅",
            "color": "\033[92m",  # Green
            "name": "Compatible",
            "description": "This video will work without issues.",
            "impact": "No problems expected. The video should play smoothly.",
        },
        CompatibilityLevel.WARNING: {
            "icon": "⚠️",
            "color": "\033[93m",  # Yellow
            "name": "Warning",
            "description": "This video may have issues or suboptimal performance.",
            "impact": (
                "The video might work but could have quality loss, "
                "performance issues, or compatibility problems."
            ),
        },
        CompatibilityLevel.INCOMPATIBLE: {
            "icon": "❌",
            "color": "\033[91m",  # Red
            "name": "Incompatible",
            "description": "This video will NOT work.",
            "impact": (
                "The video will fail to play, upload, or process. " "Conversion is required."
            ),
        },
    }

    RESET_COLOR = "\033[0m"

    def __init__(self, use_color: bool = True, explain_mode: bool = False):
        """Initialize formatter.

        Args:
            use_color: Whether to use ANSI color codes
            explain_mode: Whether to show extended explanations
        """
        self.use_color = use_color
        self.explain_mode = explain_mode

    def format_issue(self, issue: CompatibilityIssue, system: str = "") -> str:
        """Format a single compatibility issue.

        Args:
            issue: The compatibility issue to format
            system: Optional system name for context

        Returns:
            Formatted string with issue details
        """
        severity = self.SEVERITY_INFO[issue.level]
        icon = severity["icon"]
        color = severity["color"] if self.use_color else ""
        reset = self.RESET_COLOR if self.use_color else ""

        # Basic issue message
        output = f"{color}{icon} {issue.message}{reset}\n"

        # Add reason if available
        if issue.reason:
            output += f"   Reason: {issue.reason}\n"

        # Add suggestion if available
        if issue.suggestion:
            output += f"   Suggestion: {issue.suggestion}\n"

        # Add extended explanation in explain mode
        if self.explain_mode:
            output += self._format_extended_explanation(issue, system)

        return output

    def _format_extended_explanation(self, issue: CompatibilityIssue, system: str) -> str:
        """Format extended explanation for explain mode.

        Args:
            issue: The compatibility issue
            system: System name for context

        Returns:
            Extended explanation text
        """
        severity = self.SEVERITY_INFO[issue.level]
        output = "\n"

        # Severity level explanation
        output += f"   📖 About {severity['name']}:\n"
        output += f"      {severity['description']}\n"
        output += f"      {severity['impact']}\n\n"

        # Add codec-specific knowledge if available
        knowledge = self._get_codec_knowledge(issue, system)
        if knowledge:
            output += "   💡 Additional Context:\n"
            output += f"      {knowledge}\n\n"

        return output

    def _get_codec_knowledge(self, issue: CompatibilityIssue, system: str) -> Optional[str]:
        """Get additional codec/system-specific knowledge.

        Args:
            issue: The compatibility issue
            system: System name

        Returns:
            Additional context or None
        """
        # Extract codec from message (simple pattern matching)
        message_lower = issue.message.lower()

        # H.264 knowledge
        if "h.264" in message_lower or "h264" in message_lower:
            if "profile" in message_lower:
                return (
                    "H.264 profiles (Baseline, Main, High) determine feature "
                    "complexity. Baseline is most compatible but least efficient. "
                    "High offers better compression but requires more processing "
                    "power."
                )
            if system.lower() == "instagram":
                return (
                    "Instagram re-encodes videos to H.264 Baseline for maximum "
                    "device compatibility. Using Baseline from the start prevents "
                    "quality loss from double encoding."
                )

        # VP9 knowledge
        if "vp9" in message_lower:
            if system.lower() in ["safari", "casparcg"]:
                return (
                    "VP9 is a modern, efficient codec by Google, but not "
                    "universally supported. H.264 or HEVC are safer choices for "
                    "broad compatibility."
                )

        # ProRes knowledge
        if "prores" in message_lower:
            if "proxy" in message_lower or "lt" in message_lower:
                return (
                    "ProRes Proxy and LT are optimized for editing and playback, "
                    "with lower bitrates than standard ProRes. They're ideal for "
                    "real-time systems like QLab."
                )
            if "4444" in message_lower:
                return (
                    "ProRes 4444 supports alpha channels (transparency), making it "
                    "perfect for overlays and graphics in live production."
                )

        # HAP codec knowledge
        if "hap" in message_lower:
            return (
                "HAP is GPU-accelerated and designed for real-time playback. It "
                "offloads video decoding to the graphics card, providing best "
                "performance in ProPresenter."
            )

        # Bitrate knowledge
        if "bitrate" in message_lower:
            if "100" in message_lower or "200" in message_lower:
                return (
                    "High bitrates require fast storage (SSD recommended) and "
                    "powerful CPU/GPU. For live production, consider ProRes Proxy "
                    "or DNxHD 36 for lower bitrates with similar quality."
                )

        # Variable frame rate knowledge
        if "variable" in message_lower and "frame" in message_lower:
            return (
                "Variable Frame Rate (VFR) videos change frame rate during "
                "playback, which causes timing issues in live production. Always "
                "use Constant Frame Rate (CFR) for precise timing."
            )

        return None

    def format_severity_guide(self) -> str:
        """Format a guide explaining all severity levels.

        Returns:
            Formatted severity level guide
        """
        output = "\n📊 SEVERITY LEVELS EXPLAINED\n"
        output += "=" * 60 + "\n\n"

        for level, info in self.SEVERITY_INFO.items():
            color = info["color"] if self.use_color else ""
            reset = self.RESET_COLOR if self.use_color else ""

            output += f"{color}{info['icon']} {info['name'].upper()}{reset}\n"
            output += f"   {info['description']}\n"
            output += f"   Impact: {info['impact']}\n\n"

        return output

    def format_system_summary(self, system: str, issues: list, explain: bool = False) -> str:
        """Format a summary for a specific system.

        Args:
            system: System name
            issues: List of compatibility issues
            explain: Whether to include explanations

        Returns:
            Formatted system summary
        """
        output = "\n" + "=" * 60 + "\n"
        output += f"🎬 {system.upper()}\n"
        output += "=" * 60 + "\n"

        if not issues:
            output += "✅ No compatibility issues found.\n"
            return output

        # Group issues by severity
        compatible = [i for i in issues if i.level == CompatibilityLevel.COMPATIBLE]
        warnings = [i for i in issues if i.level == CompatibilityLevel.WARNING]
        incompatible = [i for i in issues if i.level == CompatibilityLevel.INCOMPATIBLE]

        # Show issues by severity (worst first)
        for issue_list in [incompatible, warnings, compatible]:
            for issue in issue_list:
                output += self.format_issue(issue, system)

        return output


def get_severity_info(level: CompatibilityLevel) -> Dict[str, str]:
    """Get information about a severity level.

    Args:
        level: The compatibility level

    Returns:
        Dictionary with severity information
    """
    return ExplanationFormatter.SEVERITY_INFO[level].copy()
