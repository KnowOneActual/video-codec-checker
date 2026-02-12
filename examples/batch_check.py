#!/usr/bin/env python3
"""Example: Batch check videos and generate report."""

import json
import sys
from pathlib import Path

from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import CompatibilityLevel, check_compatibility
from videowise.utils import get_video_info


def check_video(file_path: Path, system: str) -> dict:
    """Check a single video file."""
    try:
        analyzer = VideoAnalyzer(str(file_path))
        video_info = get_video_info(analyzer)
        issues = check_compatibility(video_info, system)

        # Determine overall status
        has_incompatible = any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
        has_warning = any(issue.level == CompatibilityLevel.WARNING for issue in issues)

        if has_incompatible:
            status = "incompatible"
        elif has_warning:
            status = "warning"
        else:
            status = "compatible"

        return {
            "file": str(file_path),
            "status": status,
            "issues": [
                {
                    "level": issue.level.value,
                    "message": issue.message,
                    "reason": issue.reason,
                    "suggestion": issue.suggestion,
                }
                for issue in issues
            ],
        }
    except Exception as e:
        return {"file": str(file_path), "status": "error", "error": str(e)}


def main():
    if len(sys.argv) < 3:
        print("Usage: batch_check.py <directory> <system>")
        print("Example: batch_check.py ./videos casparcg")
        sys.exit(1)

    directory = Path(sys.argv[1])
    system = sys.argv[2]

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)

    # Find all video files
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mxf"}
    video_files = [f for f in directory.iterdir() if f.suffix.lower() in video_extensions]

    if not video_files:
        print(f"No video files found in {directory}")
        sys.exit(0)

    print(f"Checking {len(video_files)} videos for {system} compatibility...\n")

    results = []
    for video_file in sorted(video_files):
        print(f"Checking {video_file.name}...", end=" ")
        result = check_video(video_file, system)
        results.append(result)

        # Quick status indicator
        if result["status"] == "compatible":
            print("✓")
        elif result["status"] == "warning":
            print("⚠")
        elif result["status"] == "incompatible":
            print("✗")
        else:
            print("ERROR")

    # Summary
    compatible = sum(1 for r in results if r["status"] == "compatible")
    warnings = sum(1 for r in results if r["status"] == "warning")
    incompatible = sum(1 for r in results if r["status"] == "incompatible")
    errors = sum(1 for r in results if r["status"] == "error")

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  ✓ Compatible: {compatible}")
    print(f"  ⚠ Warnings: {warnings}")
    print(f"  ✗ Incompatible: {incompatible}")
    if errors:
        print(f"  ERROR: {errors}")

    # Save full report
    report_file = Path(f"compatibility_report_{system}.json")
    with open(report_file, "w") as f:
        json.dump(
            {
                "system": system,
                "directory": str(directory),
                "summary": {
                    "total": len(results),
                    "compatible": compatible,
                    "warnings": warnings,
                    "incompatible": incompatible,
                    "errors": errors,
                },
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\nFull report saved to: {report_file}")

    # Exit with appropriate code
    if incompatible > 0 or errors > 0:
        sys.exit(1)
    elif warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
