"""Command-line interface for VideoWise."""

import sys
from pathlib import Path
from typing import Optional

import click

from videowise.analyzer import VideoAnalyzer
from videowise.compatibility import check_compatibility, CompatibilityLevel
from videowise.utils import get_video_info


# Color mapping for output
COLOR_MAP = {
    CompatibilityLevel.COMPATIBLE: 'green',
    CompatibilityLevel.WARNING: 'yellow',
    CompatibilityLevel.INCOMPATIBLE: 'red',
    CompatibilityLevel.UNKNOWN: 'cyan',
}

SYMBOL_MAP = {
    CompatibilityLevel.COMPATIBLE: '✓',
    CompatibilityLevel.WARNING: '⚠',
    CompatibilityLevel.INCOMPATIBLE: '✗',
    CompatibilityLevel.UNKNOWN: '?',
}


@click.group()
@click.version_option(version='0.1.0', prog_name='videowise')
def cli():
    """VideoWise - Video codec compatibility checker for live production and content creation."""
    pass


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--system', '-s',
    required=True,
    type=click.Choice([
        'casparcg', 'vmix', 'obs', 'qlab', 'propresenter',
        'safari', 'chrome', 'instagram', 'twitter'
    ], case_sensitive=False),
    help='Target system to check compatibility against'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed information'
)
@click.option(
    '--json',
    'output_json',
    is_flag=True,
    help='Output results as JSON'
)
def check(file: Path, system: str, verbose: bool, output_json: bool):
    """Check video file compatibility with a specific system.
    
    Examples:
    
        videowise check video.mp4 --system casparcg
        
        videowise check sponsor.mov --system instagram -v
        
        videowise check playlist.mp4 --system qlab --json
    """
    try:
        # Analyze the video file (only show message if not JSON mode)
        if not output_json:
            click.echo(f"Analyzing {file.name}...", err=True)
        
        analyzer = VideoAnalyzer(str(file))
        
        # Check if we can extract metadata
        metadata = analyzer.get_metadata()
        if not metadata:
            click.secho(
                "Error: Unable to extract video metadata. Is ffmpeg/ffprobe installed?",
                fg='red',
                err=True
            )
            sys.exit(2)
        
        # Get video info and check compatibility
        video_info = get_video_info(analyzer)
        issues = check_compatibility(video_info, system)
        
        # Output results
        if output_json:
            import json
            output = {
                'file': str(file),
                'system': system,
                'issues': [
                    {
                        'level': issue.level.value,
                        'message': issue.message,
                        'reason': issue.reason,
                        'suggestion': issue.suggestion,
                    }
                    for issue in issues
                ]
            }
            click.echo(json.dumps(output, indent=2))
        else:
            # Human-readable output
            click.echo()
            click.secho(f"Compatibility Check: {system.upper()}", bold=True)
            click.echo("─" * 50)
            
            for issue in issues:
                color = COLOR_MAP[issue.level]
                symbol = SYMBOL_MAP[issue.level]
                
                click.secho(f"{symbol} {issue.message}", fg=color, bold=True)
                
                if verbose or issue.level == CompatibilityLevel.INCOMPATIBLE:
                    if issue.reason:
                        click.echo(f"  Reason: {issue.reason}")
                    if issue.suggestion:
                        click.echo(f"  Suggestion: {issue.suggestion}")
                    click.echo()
        
        # Determine exit code
        has_incompatible = any(
            issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues
        )
        has_warning = any(
            issue.level == CompatibilityLevel.WARNING for issue in issues
        )
        
        if has_incompatible:
            sys.exit(2)  # Incompatible
        elif has_warning:
            sys.exit(1)  # Warnings
        else:
            sys.exit(0)  # Compatible
    
    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(2)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
