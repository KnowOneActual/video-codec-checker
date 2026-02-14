"""Command-line interface for video codec checker."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import CompatibilityIssue, check_compatibility, get_available_systems
from videowise.formatter import ExplanationFormatter

__version__ = "0.1.0"

# Common video file extensions
DEFAULT_VIDEO_EXTENSIONS = [
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".m4v",
    ".webm",
    ".flv",
    ".wmv",
    ".mpg",
    ".mpeg",
    ".m2v",
    ".mxf",
]


@click.group()
@click.version_option(version=__version__)
def cli():
    """Video Codec Compatibility Checker.

    Check if your video files are compatible with various playback systems.
    """
    pass


def determine_worst_level(all_results: List[Dict[str, Any]]) -> int:
    """Determine worst compatibility level across all systems.

    Args:
        all_results: List of result dictionaries for each system

    Returns:
        Exit code: 0 for all compatible, 1 for warnings, 2 for incompatible
    """
    has_incompatible = False
    has_warning = False

    for result in all_results:
        for issue in result.get("issues", []):
            level = issue.get("level", "").lower()
            if level == "incompatible":
                has_incompatible = True
            elif level == "warning":
                has_warning = True

    if has_incompatible:
        return 2
    elif has_warning:
        return 1
    return 0


def find_video_files(
    paths: List[str],
    recursive: bool = False,
    extensions: Optional[List[str]] = None,
) -> List[Path]:
    """Find all video files in the given paths.

    Args:
        paths: List of file or directory paths
        recursive: If True, scan directories recursively
        extensions: List of file extensions to include (with dots)

    Returns:
        List of Path objects for video files
    """
    if extensions is None:
        extensions = DEFAULT_VIDEO_EXTENSIONS

    extensions_lower = [ext.lower() for ext in extensions]
    video_files = []

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            click.secho(f"Warning: Path does not exist: {path}", fg="yellow", err=True)
            continue

        if path.is_file():
            if path.suffix.lower() in extensions_lower:
                video_files.append(path)
        elif path.is_dir():
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"

            for ext in extensions_lower:
                video_files.extend(path.glob(f"{pattern}{ext}"))

    # Remove duplicates and sort
    video_files = sorted(set(video_files))
    return video_files


def check_single_file(
    file_path: Path, systems_to_check: List[str], verbose: bool = False
) -> Tuple[Dict[str, Any], int]:
    """Check a single video file against specified systems.

    Args:
        file_path: Path to video file
        systems_to_check: List of system names to check
        verbose: Show detailed information

    Returns:
        Tuple of (result_dict, exit_code)
    """
    try:
        analyzer = VideoAnalyzer(str(file_path))
        metadata = analyzer.get_metadata()

        if not metadata:
            return {
                "file": str(file_path),
                "error": "Unable to extract video metadata",
                "results": [],
            }, 2

        codec = analyzer.get_codec_name() or "unknown"
        codec_profile = analyzer.get_codec_profile()
        container = analyzer.get_container_format() or "unknown"
        resolution = analyzer.get_resolution()
        framerate = analyzer.get_frame_rate()
        bitrate = analyzer.get_bitrate()
        file_size = analyzer.get_file_size()

        video_info = {
            "codec": codec.split()[0].lower(),
            "profile": codec_profile,
            "container": container,
            "width": resolution[0] if resolution else None,
            "height": resolution[1] if resolution else None,
            "resolution": resolution,
            "framerate": float(framerate) if framerate else None,
            "bitrate": bitrate,
            "file_size": file_size,
        }

        # Check all systems
        all_results: List[Dict[str, Any]] = []
        for sys_name in systems_to_check:
            issues = check_compatibility(video_info, sys_name)
            all_results.append(
                {
                    "system": sys_name,
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
            )

        exit_code = determine_worst_level(all_results)

        result = {
            "file": str(file_path),
            "video_info": video_info,
            "systems_checked": systems_to_check,
            "results": all_results,
            "exit_code": exit_code,
        }

        return result, exit_code

    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "results": [],
        }, 2


@cli.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option(
    "--system",
    "-s",
    help=(
        "Target playback system (casparcg, vmix, obs, qlab, propresenter, "
        "safari, chrome, instagram, twitter). Use --all to check all systems."
    ),
)
@click.option("--all", "check_all", is_flag=True, help="Check against all systems")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option(
    "--explain",
    "-e",
    is_flag=True,
    help="Show extended explanations with codec knowledge and context",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output (useful for logs/files)",
)
def check(
    video_path: str,
    system: str,
    check_all: bool,
    output_json: bool,
    verbose: bool,
    explain: bool,
    no_color: bool,
):
    r"""Check video compatibility with a specific system.

    VIDEO_PATH: Path to the video file to check

    Examples:\b
        videowise check video.mp4 --system casparcg
        videowise check video.mov --system qlab --json
        videowise check video.mp4 --all
        videowise check video.mp4 --all --verbose
        videowise check video.mp4 --system safari --explain
    """
    # Validation: must specify either --system or --all
    if not system and not check_all:
        click.secho(
            "Error: Must specify either --system or --all flag",
            fg="red",
            err=True,
        )
        click.echo("\nExamples:")
        click.echo("  videowise check video.mp4 --system casparcg")
        click.echo("  videowise check video.mp4 --all")
        sys.exit(2)

    if system and check_all:
        click.secho(
            "Error: Cannot use both --system and --all flags",
            fg="red",
            err=True,
        )
        sys.exit(2)

    # Create formatter
    use_color = not no_color and not output_json
    formatter = ExplanationFormatter(use_color=use_color, explain_mode=explain)

    try:
        path = Path(video_path)
        analyzer = VideoAnalyzer(str(path))

        metadata = analyzer.get_metadata()
        if not metadata:
            click.secho(
                "Error: Unable to extract video metadata. Is ffmpeg/ffprobe installed?",
                fg="red",
                err=True,
            )
            sys.exit(2)

        codec = analyzer.get_codec_name() or "unknown"
        codec_profile = analyzer.get_codec_profile()
        container = analyzer.get_container_format() or "unknown"
        resolution = analyzer.get_resolution()
        framerate = analyzer.get_frame_rate()
        bitrate = analyzer.get_bitrate()
        file_size = analyzer.get_file_size()

        if codec_profile:
            codec_display = f"{codec} ({codec_profile})"
        else:
            codec_display = codec

        video_info = {
            "codec": codec.split()[0].lower(),
            "profile": codec_profile,
            "container": container,
            "width": resolution[0] if resolution else None,
            "height": resolution[1] if resolution else None,
            "resolution": resolution,
            "framerate": float(framerate) if framerate else None,
            "bitrate": bitrate,
            "file_size": file_size,
        }

        # Determine systems to check
        systems_to_check = get_available_systems() if check_all else [system]

        # Check all systems
        all_results: List[Dict[str, Any]] = []
        all_issues_objects: List[Tuple[str, List[CompatibilityIssue]]] = []

        for sys_name in systems_to_check:
            issues = check_compatibility(video_info, sys_name)
            all_issues_objects.append((sys_name, issues))
            all_results.append(
                {
                    "system": sys_name,
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
            )

        # Output results
        if output_json:
            # For backward compatibility: if single system, use old format
            if len(systems_to_check) == 1:
                result = {
                    "file": str(path),
                    "system": systems_to_check[0],
                    "video_info": video_info,
                    "issues": all_results[0]["issues"],
                }
            else:
                # Multiple systems: use new format
                result = {
                    "file": str(path),
                    "video_info": video_info,
                    "systems_checked": systems_to_check,
                    "results": all_results,
                }
            click.echo(json.dumps(result, indent=2))
        else:
            # Regular output with formatter
            click.secho(f"\n📹 Video: {path.name}", bold=True)

            if verbose:
                click.echo(f"\nCodec: {codec_display}")
                click.echo(f"Container: {container}")
                if resolution:
                    click.echo(f"Resolution: {resolution[0]}x{resolution[1]}")
                if framerate:
                    click.echo(f"Framerate: {framerate} fps")
                if bitrate:
                    click.echo(f"Bitrate: {bitrate / 1_000_000:.2f} Mbps")

            if check_all:
                click.secho(
                    f"\n🔍 Checking against all {len(systems_to_check)} systems\n", bold=True
                )

            # Show severity guide in explain mode
            if explain and not check_all:
                click.echo(formatter.format_severity_guide())

            # Display results for each system using formatter
            for sys_name, issues in all_issues_objects:
                click.echo(formatter.format_system_summary(sys_name, issues, explain))

            # Summary if checking all systems
            if check_all:
                click.echo("\n" + "=" * 60)
                click.secho("📊 SUMMARY", bold=True, fg="cyan")
                click.echo("=" * 60)

                compatible_systems = []
                warning_systems = []
                incompatible_systems = []

                for result_data in all_results:
                    system_name: str = result_data["system"]
                    system_issues: List[Dict[str, Any]] = result_data["issues"]

                    has_incompatible = any(
                        issue_dict.get("level", "").lower() == "incompatible"
                        for issue_dict in system_issues
                    )
                    has_warning = any(
                        issue_dict.get("level", "").lower() == "warning"
                        for issue_dict in system_issues
                    )

                    if has_incompatible:
                        incompatible_systems.append(system_name)
                    elif has_warning:
                        warning_systems.append(system_name)
                    else:
                        compatible_systems.append(system_name)

                if compatible_systems:
                    click.secho(
                        f"\n✅ Compatible ({len(compatible_systems)}):",
                        fg="green",
                        bold=True,
                    )
                    for system_name in compatible_systems:
                        click.echo(f"   • {system_name}")

                if warning_systems:
                    click.secho(
                        f"\n⚠️  Warnings ({len(warning_systems)}):",
                        fg="yellow",
                        bold=True,
                    )
                    for system_name in warning_systems:
                        click.echo(f"   • {system_name}")

                if incompatible_systems:
                    click.secho(
                        f"\n❌ Incompatible ({len(incompatible_systems)}):",
                        fg="red",
                        bold=True,
                    )
                    for system_name in incompatible_systems:
                        click.echo(f"   • {system_name}")

                click.echo()

        # Determine exit code
        exit_code = determine_worst_level(all_results)
        sys.exit(exit_code)

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(2)


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--system",
    "-s",
    help=(
        "Target playback system (casparcg, vmix, obs, qlab, propresenter, "
        "safari, chrome, instagram, twitter). Use --all to check all systems."
    ),
)
@click.option("--all", "check_all", is_flag=True, help="Check against all systems")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively scan directories for video files",
)
@click.option(
    "--extensions",
    "-e",
    help=f"Comma-separated list of file extensions (default: {','.join(DEFAULT_VIDEO_EXTENSIONS)})",
)
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option(
    "--explain",
    is_flag=True,
    help="Show extended explanations with codec knowledge and context",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output (useful for logs/files)",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue processing files even if some fail (default: True)",
)
def batch(
    paths: Tuple[str, ...],
    system: str,
    check_all: bool,
    recursive: bool,
    extensions: str,
    output_json: bool,
    verbose: bool,
    explain: bool,
    no_color: bool,
    continue_on_error: bool,
):
    r"""Check multiple video files or directories for compatibility.

    PATHS: One or more video files or directories to check

    Examples:\b
        videowise batch video1.mp4 video2.mov --system casparcg
        videowise batch /path/to/videos/ --recursive --all
        videowise batch *.mp4 --system instagram --json
        videowise batch /media --recursive --extensions .mp4,.mov
        videowise batch videos/ --system safari --explain
    """
    # Validation: must specify either --system or --all
    if not system and not check_all:
        click.secho(
            "Error: Must specify either --system or --all flag",
            fg="red",
            err=True,
        )
        sys.exit(2)

    if system and check_all:
        click.secho(
            "Error: Cannot use both --system and --all flags",
            fg="red",
            err=True,
        )
        sys.exit(2)

    # Parse extensions
    ext_list: Optional[List[str]] = None
    if extensions:
        ext_list = [
            ext.strip() if ext.startswith(".") else f".{ext.strip()}"
            for ext in extensions.split(",")
        ]

    # Find all video files
    video_files = find_video_files(list(paths), recursive, ext_list)

    if not video_files:
        click.secho("Error: No video files found", fg="red", err=True)
        sys.exit(2)

    if not output_json:
        click.secho(f"\n📂 Found {len(video_files)} video file(s) to check\n", bold=True)

    # Determine systems to check
    systems_to_check = get_available_systems() if check_all else [system]

    # Process all files
    batch_results = []
    errors = []
    worst_exit_code = 0

    for file_path in video_files:
        if not output_json and verbose:
            click.secho(f"\nProcessing: {file_path}", fg="cyan")

        result, exit_code = check_single_file(file_path, systems_to_check, verbose)

        batch_results.append(result)
        worst_exit_code = max(worst_exit_code, exit_code)

        if "error" in result:
            errors.append(result)
            if not continue_on_error:
                break

    # Output results
    if output_json:
        output = {
            "total_files": len(video_files),
            "processed_files": len(batch_results),
            "systems_checked": systems_to_check,
            "results": batch_results,
            "errors": len(errors),
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Display summary
        click.echo("\n" + "=" * 70)
        click.secho("📊 BATCH SUMMARY", bold=True, fg="cyan")
        click.echo("=" * 70)

        click.echo(f"\nTotal files processed: {len(batch_results)}")
        click.echo(f"Systems checked: {', '.join(systems_to_check)}")

        if errors:
            click.secho(f"\n⚠️  Errors encountered: {len(errors)}", fg="yellow")
            for error_result in errors:
                click.echo(
                    f"   • {error_result['file']}: {error_result.get('error', 'Unknown error')}"
                )

        # Count files by status
        compatible_files = []
        warning_files = []
        incompatible_files = []

        for result in batch_results:
            if "error" in result:
                continue

            exit_code = result.get("exit_code", 0)
            if exit_code == 0:
                compatible_files.append(result["file"])
            elif exit_code == 1:
                warning_files.append(result["file"])
            else:
                incompatible_files.append(result["file"])

        if compatible_files:
            click.secho(f"\n✅ Fully compatible: {len(compatible_files)}", fg="green", bold=True)

        if warning_files:
            click.secho(f"\n⚠️  Warnings: {len(warning_files)}", fg="yellow", bold=True)
            if verbose:
                for file in warning_files:
                    click.echo(f"   • {Path(file).name}")

        if incompatible_files:
            click.secho(f"\n❌ Incompatible: {len(incompatible_files)}", fg="red", bold=True)
            if verbose:
                for file in incompatible_files:
                    click.echo(f"   • {Path(file).name}")

        click.echo()

    sys.exit(worst_exit_code)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    cli()
