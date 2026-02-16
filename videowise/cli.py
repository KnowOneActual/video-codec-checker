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


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    r"""VideoWise - Video Codec Compatibility Checker.

    Check if your videos work with CasparCG, Instagram, browsers, and more.

    \b
    QUICK START:
      videowise video.mp4              # Check against all systems
      videowise casparcg video.mp4     # Check for CasparCG compatibility
      videowise instagram video.mp4    # Check for Instagram compatibility
      videowise learn video.mp4        # Educational mode with explanations

    \b
    COMMON WORKFLOWS:
      # Pre-show check for live production
      videowise casparcg show-videos/ -r

      # Social media batch export check
      videowise instagram exports/*.mp4

      # Learn about codec issues
      videowise learn problematic_video.mp4

    Run 'videowise --help' to see all commands and options.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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


def run_compatibility_check(
    paths: Tuple[str, ...],
    systems_to_check: List[str],
    recursive: bool = False,
    extensions: Optional[str] = None,
    output_json: bool = False,
    verbose: bool = False,
    explain: bool = False,
    no_color: bool = False,
):
    """Core compatibility checking logic shared between commands."""
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

    # Single file or batch processing
    is_batch = len(video_files) > 1

    if not output_json and is_batch:
        click.secho(f"\n📂 Found {len(video_files)} video file(s) to check\n", bold=True)

    # Create formatter
    use_color = not no_color and not output_json
    formatter = ExplanationFormatter(use_color=use_color, explain_mode=explain)

    # Process files
    batch_results = []
    errors = []
    worst_exit_code = 0

    for file_path in video_files:
        if not output_json and verbose and is_batch:
            click.secho(f"\nProcessing: {file_path}", fg="cyan")

        result, exit_code = check_single_file(file_path, systems_to_check, verbose)

        batch_results.append(result)
        worst_exit_code = max(worst_exit_code, exit_code)

        if "error" in result:
            errors.append(result)

        # For single file, show detailed output
        if not is_batch and not output_json:
            path = Path(file_path)
            analyzer = VideoAnalyzer(str(path))

            codec = analyzer.get_codec_name() or "unknown"
            codec_profile = analyzer.get_codec_profile()
            container = analyzer.get_container_format() or "unknown"
            resolution = analyzer.get_resolution()
            framerate = analyzer.get_frame_rate()
            bitrate = analyzer.get_bitrate()

            if codec_profile:
                codec_display = f"{codec} ({codec_profile})"
            else:
                codec_display = codec

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

            check_all = len(systems_to_check) > 1
            if check_all:
                click.secho(
                    f"\n🔍 Checking against all {len(systems_to_check)} systems\n", bold=True
                )

            # Show severity guide in explain mode
            if explain and not check_all:
                click.echo(formatter.format_severity_guide())

            # Display results for each system
            all_issues_objects: List[Tuple[str, List[CompatibilityIssue]]] = []
            for result_data in result["results"]:
                sys_name = result_data["system"]
                issues = check_compatibility(result["video_info"], sys_name)
                all_issues_objects.append((sys_name, issues))
                click.echo(formatter.format_system_summary(sys_name, issues, explain))

            # Summary if checking all systems
            if check_all:
                click.echo("\n" + "=" * 60)
                click.secho("📊 SUMMARY", bold=True, fg="cyan")
                click.echo("=" * 60)

                compatible_systems = []
                warning_systems = []
                incompatible_systems = []

                for result_data in result["results"]:
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

    # Output results
    if output_json:
        if is_batch:
            output = {
                "total_files": len(video_files),
                "processed_files": len(batch_results),
                "systems_checked": systems_to_check,
                "results": batch_results,
                "errors": len(errors),
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Single file JSON
            result = batch_results[0]
            if len(systems_to_check) == 1:
                # Backward compatibility
                output = {
                    "file": result["file"],
                    "system": systems_to_check[0],
                    "video_info": result["video_info"],
                    "issues": result["results"][0]["issues"],
                }
            else:
                output = result
            click.echo(json.dumps(output, indent=2))
    elif is_batch:
        # Batch summary
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


# Preset commands for common systems
def create_system_command(system_name: str, system_display: str, description: str):
    """Create system-specific command dynamically."""

    @cli.command(name=system_name)
    @click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
    @click.option("--recursive", "-r", is_flag=True, help="Scan directories recursively")
    @click.option("--extensions", "-e", help="File extensions to check (e.g., .mp4,.mov)")
    @click.option("--json", "output_json", is_flag=True, help="Output as JSON")
    @click.option("--verbose", "-v", is_flag=True, help="Show detailed video information")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    def system_command(paths, recursive, extensions, output_json, verbose, no_color):
        rf"""Check video compatibility with {system_display}.

        \b
        Quick Examples:
          videowise {system_name} video.mp4
          videowise {system_name} videos/ -r
          videowise {system_name} *.mp4 --json

        {description}
        """
        run_compatibility_check(
            paths=paths,
            systems_to_check=[system_name],
            recursive=recursive,
            extensions=extensions,
            output_json=output_json,
            verbose=verbose,
            explain=False,
            no_color=no_color,
        )

    system_command.__doc__ = rf"""Check video compatibility with {system_display}.

    \b
    Quick Examples:
      videowise {system_name} video.mp4
      videowise {system_name} videos/ -r
      videowise {system_name} *.mp4 --json

    {description}
    """

    return system_command


# Create preset commands for all major systems
create_system_command("casparcg", "CasparCG", "For live broadcast playout servers")
create_system_command("vmix", "vMix", "For live video mixing and streaming")
create_system_command("obs", "OBS Studio", "For live streaming and recording")
create_system_command("qlab", "QLab", "For theatre and live show playback")
create_system_command("resolume", "Resolume", "For VJ and live video performance")
create_system_command("propresenter", "ProPresenter", "For church presentations")
create_system_command("safari", "Safari", "For Safari browser playback")
create_system_command("chrome", "Chrome", "For Chrome browser playback")
create_system_command("firefox", "Firefox", "For Firefox browser playback")
create_system_command("instagram", "Instagram", "For Instagram upload compatibility")
create_system_command("twitter", "Twitter/X", "For Twitter/X upload compatibility")
create_system_command("youtube", "YouTube", "For YouTube upload compatibility")
create_system_command("tiktok", "TikTok", "For TikTok upload compatibility")


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Scan directories recursively")
@click.option("--extensions", "-e", help="File extensions to check (e.g., .mp4,.mov)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed video information")
@click.option("--no-color", is_flag=True, help="Disable colored output")
def learn(paths, recursive, extensions, output_json, verbose, no_color):
    r"""Educational mode - Learn why videos have compatibility issues.

    Shows extended explanations about codecs, profiles, and compatibility.
    Perfect for training teams or understanding video encoding.

    \b
    Examples:
      videowise learn problem_video.mp4
      videowise learn exports/ -r
      videowise learn video.mp4 > training_guide.txt

    This mode explains:
    - What each codec is and how it works
    - Why certain systems don't support specific formats
    - Best practices for video encoding
    - How to fix compatibility issues
    """
    run_compatibility_check(
        paths=paths,
        systems_to_check=get_available_systems(),
        recursive=recursive,
        extensions=extensions,
        output_json=output_json,
        verbose=verbose,
        explain=True,
        no_color=no_color,
    )


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--system",
    "-s",
    help="Check specific system (or use preset commands like 'casparcg', 'instagram')",
)
@click.option("--all", "check_all", is_flag=True, help="Check against all systems (default)")
@click.option("--recursive", "-r", is_flag=True, help="Scan directories recursively")
@click.option("--extensions", "-e", help="File extensions to check (e.g., .mp4,.mov)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed video information")
@click.option("--explain", is_flag=True, help="Show educational explanations")
@click.option("--no-color", is_flag=True, help="Disable colored output")
def check(paths, system, check_all, recursive, extensions, output_json, verbose, explain, no_color):
    r"""Check video compatibility (defaults to all systems).

    The main compatibility checker. By default, checks against all systems.
    For quicker checks, use preset commands like 'casparcg' or 'instagram'.

    \b
    Examples:
      videowise check video.mp4                    # Check all systems
      videowise check video.mp4 --system casparcg  # Check one system
      videowise check videos/ -r --all             # Batch check all
      videowise check video.mp4 --explain          # Educational mode

    \b
    TIP: For faster, simpler commands use:
      videowise casparcg video.mp4      # Instead of --system casparcg
      videowise instagram video.mp4     # Instead of --system instagram
      videowise learn video.mp4         # Instead of --explain
    """
    # Handle backward compatibility and defaults
    if system and check_all:
        click.secho(
            "Error: Cannot use both --system and --all flags",
            fg="red",
            err=True,
        )
        click.echo("\nTIP: Use preset commands for easier usage:")
        click.echo(f"  videowise {system} {paths[0] if paths else 'video.mp4'}")
        sys.exit(2)

    # Default to all systems if nothing specified
    if not system and not check_all:
        systems_to_check = get_available_systems()
    elif check_all:
        systems_to_check = get_available_systems()
    else:
        systems_to_check = [system]

    run_compatibility_check(
        paths=paths,
        systems_to_check=systems_to_check,
        recursive=recursive,
        extensions=extensions,
        output_json=output_json,
        verbose=verbose,
        explain=explain,
        no_color=no_color,
    )


@cli.command()
@click.argument("paths", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--system",
    "-s",
    help="Target system (use preset commands for easier usage)",
)
@click.option("--all", "check_all", is_flag=True, help="Check against all systems")
@click.option("--recursive", "-r", is_flag=True, help="Scan directories recursively")
@click.option("--extensions", "-e", help="File extensions to check (e.g., .mp4,.mov)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option("--explain", is_flag=True, help="Show educational explanations")
@click.option("--no-color", is_flag=True, help="Disable colored output")
def batch(paths, system, check_all, recursive, extensions, output_json, verbose, explain, no_color):
    r"""Check multiple files or directories (legacy command).

    NOTE: The 'check' command now handles both single files and batches.
    This command is kept for backward compatibility.

    \b
    Use 'check' instead:
      videowise check videos/ -r --all
      videowise casparcg videos/ -r
    """
    if not system and not check_all:
        click.secho(
            "Error: Must specify either --system or --all flag",
            fg="red",
            err=True,
        )
        click.echo("\nTIP: Use simpler preset commands:")
        click.echo("  videowise casparcg videos/ -r")
        click.echo("  videowise instagram exports/")
        sys.exit(2)

    if system and check_all:
        click.secho(
            "Error: Cannot use both --system and --all flags",
            fg="red",
            err=True,
        )
        sys.exit(2)

    systems_to_check = get_available_systems() if check_all else [system]

    run_compatibility_check(
        paths=paths,
        systems_to_check=systems_to_check,
        recursive=recursive,
        extensions=extensions,
        output_json=output_json,
        verbose=verbose,
        explain=explain,
        no_color=no_color,
    )


@cli.command()
def systems():
    r"""List all available systems you can check against.

    Shows all supported playback systems, browsers, and platforms.
    Use these names with --system flag or as preset commands.

    \b
    Example:
      videowise systems                 # See all available
      videowise casparcg video.mp4      # Use as preset command
      videowise check video.mp4 -s obs  # Use with --system flag
    """
    available_systems = get_available_systems()

    click.secho("\n📋 Available Systems:\n", bold=True, fg="cyan")

    # Group by category
    categories = {
        "Live Production": [
            "casparcg",
            "vmix",
            "obs",
            "qlab",
            "propresenter",
            "wirecast",
            "playbackpro",
            "provideoplayer",
            "easyworship",
            "playoutbee",
        ],
        "VJ / Media Players": ["resolume", "vlc", "mitti", "millumin"],
        "Browsers": ["safari", "chrome", "firefox"],
        "Social Media": ["instagram", "twitter", "youtube", "tiktok", "vimeo", "facebook"],
    }

    for category, system_list in categories.items():
        click.secho(f"{category}:", bold=True)
        for system_name in system_list:
            if system_name in available_systems:
                # Show both preset command and --system usage
                click.echo(f"  • {system_name:20} → videowise {system_name} video.mp4")
        click.echo()

    click.secho("💡 TIP:", fg="cyan", bold=True)
    click.echo("  Use system names directly as commands for simpler usage!")
    click.echo(
        "  Example: 'videowise casparcg video.mp4' instead of "
        "'videowise check video.mp4 --system casparcg'\n"
    )


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    cli()
