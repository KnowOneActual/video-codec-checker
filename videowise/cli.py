"""Command-line interface for video codec checker."""

import json
import sys
from pathlib import Path

import click

from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility

__version__ = "0.1.0"


@click.group()
@click.version_option(version=__version__)
def cli():
    """Video Codec Compatibility Checker.

    Check if your video files are compatible with various playback systems.
    """
    pass


@cli.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option(
    "--system",
    "-s",
    required=True,
    help=(
        "Target playback system (casparcg, vmix, obs, qlab, propresenter, "
        "safari, chrome, instagram, twitter)"
    ),
)
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def check(video_path: str, system: str, output_json: bool, verbose: bool):
    """Check video compatibility with a specific system.

    VIDEO_PATH: Path to the video file to check

    Examples:
        videowise check video.mp4 --system casparcg
        videowise check video.mov --system qlab --json
    """
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
            codec = f"{codec} ({codec_profile})"

        video_info = {
            "codec": codec.split()[0].lower(),
            "profile": codec_profile,
            "container": container,
            "width": resolution[0] if resolution else None,
            "height": resolution[1] if resolution else None,
            "framerate": float(framerate) if framerate else None,
            "bitrate": bitrate,
            "file_size": file_size,
        }

        issues = check_compatibility(video_info, system)

        if output_json:
            result = {
                "file": str(path),
                "system": system,
                "video_info": video_info,
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
            click.echo(json.dumps(result, indent=2))
        else:
            click.secho(f"\n📹 Video: {path.name}", bold=True)
            click.secho(f"🎬 System: {system}", bold=True)

            if verbose:
                click.echo(f"\nCodec: {codec}")
                click.echo(f"Container: {container}")
                if resolution:
                    click.echo(f"Resolution: {resolution[0]}x{resolution[1]}")
                if framerate:
                    click.echo(f"Framerate: {framerate} fps")
                if bitrate:
                    click.echo(f"Bitrate: {bitrate / 1_000_000:.2f} Mbps")

            click.echo("\n" + "=" * 50)

            if not issues:
                click.secho("✅ No compatibility issues found!", fg="green")
            else:
                for issue in issues:
                    if issue.level.value == "compatible":
                        color = "green"
                        icon = "✅"
                    elif issue.level.value == "warning":
                        color = "yellow"
                        icon = "⚠️"
                    else:
                        color = "red"
                        icon = "❌"

                    click.secho(f"\n{icon} {issue.message}", fg=color, bold=True)
                    if issue.reason:
                        click.echo(f"   Reason: {issue.reason}")
                    if issue.suggestion:
                        click.echo(f"   Suggestion: {issue.suggestion}")

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
