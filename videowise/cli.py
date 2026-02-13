"""Command-line interface for video codec checker."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import click

from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility, get_available_systems

__version__ = "0.1.0"


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
def check(video_path: str, system: str, check_all: bool, output_json: bool, verbose: bool):
    r"""Check video compatibility with a specific system.

    VIDEO_PATH: Path to the video file to check

    Examples:\b
        videowise check video.mp4 --system casparcg
        videowise check video.mov --system qlab --json
        videowise check video.mp4 --all
        videowise check video.mp4 --all --verbose
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
            # Regular output
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

            # Display results for each system
            for result_data in all_results:
                sys_name_str: str = result_data["system"]
                issues_list: List[Dict[str, Any]] = result_data["issues"]

                # System header
                click.echo("\n" + "=" * 60)
                click.secho(f"🎬 {sys_name_str.upper()}", bold=True, fg="cyan")
                click.echo("=" * 60)

                if not issues_list:
                    click.secho("✅ No compatibility issues found!", fg="green")
                else:
                    for issue_dict in issues_list:
                        level = issue_dict.get("level", "").lower()
                        message = issue_dict.get("message", "")
                        reason = issue_dict.get("reason")
                        suggestion = issue_dict.get("suggestion")

                        if level == "compatible":
                            color = "green"
                            icon = "✅"
                        elif level == "warning":
                            color = "yellow"
                            icon = "⚠️"
                        elif level == "incompatible":
                            color = "red"
                            icon = "❌"
                        else:
                            color = "white"
                            icon = "ℹ️"

                        click.secho(f"\n{icon} {message}", fg=color, bold=True)
                        if reason:
                            click.echo(f"   Reason: {reason}")
                        if suggestion:
                            click.echo(f"   Suggestion: {suggestion}")

            # Summary if checking all systems
            if check_all:
                click.echo("\n" + "=" * 60)
                click.secho("📊 SUMMARY", bold=True, fg="cyan")
                click.echo("=" * 60)

                compatible_systems = []
                warning_systems = []
                incompatible_systems = []

                for result_data in all_results:
                    sys_name_str: str = result_data["system"]
                    issues_list: List[Dict[str, Any]] = result_data["issues"]

                    has_incompatible = any(
                        issue_dict.get("level", "").lower() == "incompatible"
                        for issue_dict in issues_list
                    )
                    has_warning = any(
                        issue_dict.get("level", "").lower() == "warning"
                        for issue_dict in issues_list
                    )

                    if has_incompatible:
                        incompatible_systems.append(sys_name_str)
                    elif has_warning:
                        warning_systems.append(sys_name_str)
                    else:
                        compatible_systems.append(sys_name_str)

                if compatible_systems:
                    click.secho(
                        f"\n✅ Compatible ({len(compatible_systems)}):",
                        fg="green",
                        bold=True,
                    )
                    for sys_name_str in compatible_systems:
                        click.echo(f"   • {sys_name_str}")

                if warning_systems:
                    click.secho(
                        f"\n⚠️  Warnings ({len(warning_systems)}):",
                        fg="yellow",
                        bold=True,
                    )
                    for sys_name_str in warning_systems:
                        click.echo(f"   • {sys_name_str}")

                if incompatible_systems:
                    click.secho(
                        f"\n❌ Incompatible ({len(incompatible_systems)}):",
                        fg="red",
                        bold=True,
                    )
                    for sys_name_str in incompatible_systems:
                        click.echo(f"   • {sys_name_str}")

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


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    cli()
