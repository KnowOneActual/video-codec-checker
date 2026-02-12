"""Pytest configuration and shared fixtures."""

import subprocess

import pytest


@pytest.fixture(scope="session")
def ffmpeg_available():
    """Check if ffmpeg is available on the system."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@pytest.fixture(scope="session")
def test_videos_dir(tmp_path_factory):
    """Create a temporary directory for test videos."""
    return tmp_path_factory.mktemp("test_videos")


@pytest.fixture(scope="session")
def h264_video(test_videos_dir, ffmpeg_available):
    """Generate a minimal H.264 MP4 test video."""
    if not ffmpeg_available:
        pytest.skip("ffmpeg not available")

    video_path = test_videos_dir / "test_h264.mp4"

    # Generate a 1-second 320x240 H.264 video
    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=320x240:d=1",
        "-c:v",
        "libx264",
        "-profile:v",
        "baseline",
        "-pix_fmt",
        "yuv420p",
        "-y",  # Overwrite if exists
        str(video_path),
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return video_path


@pytest.fixture(scope="session")
def h264_high_profile_video(test_videos_dir, ffmpeg_available):
    """Generate a minimal H.264 High Profile MP4 test video."""
    if not ffmpeg_available:
        pytest.skip("ffmpeg not available")

    video_path = test_videos_dir / "test_h264_high.mp4"

    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "color=c=red:s=320x240:d=1",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-pix_fmt",
        "yuv420p",
        "-y",
        str(video_path),
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return video_path


@pytest.fixture(scope="session")
def vp9_video(test_videos_dir, ffmpeg_available):
    """Generate a minimal VP9 WebM test video."""
    if not ffmpeg_available:
        pytest.skip("ffmpeg not available")

    video_path = test_videos_dir / "test_vp9.webm"

    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "color=c=green:s=320x240:d=1",
        "-c:v",
        "libvpx-vp9",
        "-b:v",
        "200k",
        "-y",
        str(video_path),
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return video_path
