"""Tests for error handling and edge cases."""

from click.testing import CliRunner

from videowise.analyzer import VideoAnalyzer
from videowise.cli import cli


class TestCLIErrorHandling:
    """Test CLI error handling paths."""

    def test_missing_ffprobe(self, tmp_path, monkeypatch):
        """Test error when ffmpeg/ffprobe is not installed."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake video")

        import subprocess

        def mock_run(*args, **kwargs):
            raise FileNotFoundError("ffprobe not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        runner = CliRunner()
        result = runner.invoke(cli, ["check", str(test_file), "--system", "casparcg"])

        assert result.exit_code == 2
        assert "ffmpeg/ffprobe installed" in result.output

    def test_corrupted_video_file(self, tmp_path):
        """Test error when video file is corrupted/invalid."""
        test_file = tmp_path / "corrupted.mp4"
        test_file.write_bytes(b"not a real video file")

        runner = CliRunner()
        result = runner.invoke(cli, ["check", str(test_file), "--system", "casparcg"])

        assert result.exit_code == 2
        assert "Error" in result.output

    def test_unexpected_error_verbose(self, tmp_path, monkeypatch):
        """Test unexpected error handling with verbose mode."""
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"fake")

        from videowise.analyzer import VideoAnalyzer

        def mock_metadata(self):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(VideoAnalyzer, "get_metadata", mock_metadata)

        runner = CliRunner()
        result = runner.invoke(cli, ["check", str(test_file), "--system", "casparcg", "--verbose"])

        assert result.exit_code == 2
        assert "Unexpected error" in result.output


class TestAnalyzerEdgeCases:
    """Test VideoAnalyzer edge cases that return None."""

    def test_no_video_stream(self, tmp_path, monkeypatch):
        """Test when video has no video stream (audio only)."""
        test_file = tmp_path / "audio_only.mp4"
        test_file.write_bytes(b"fake")

        analyzer = VideoAnalyzer(str(test_file))

        def mock_metadata():
            return {"streams": [{"codec_type": "audio"}]}

        monkeypatch.setattr(analyzer, "get_metadata", mock_metadata)

        assert analyzer.get_video_stream() is None
        assert analyzer.get_codec_name() is None
        assert analyzer.get_resolution() is None
        assert analyzer.get_frame_rate() is None

    def test_missing_video_metadata_fields(self, tmp_path, monkeypatch):
        """Test when video stream is missing expected fields."""
        test_file = tmp_path / "incomplete.mp4"
        test_file.write_bytes(b"fake")

        analyzer = VideoAnalyzer(str(test_file))

        def mock_stream():
            return {"codec_type": "video"}

        monkeypatch.setattr(analyzer, "get_video_stream", mock_stream)

        assert analyzer.get_codec_name() is None
        assert analyzer.get_resolution() is None
        assert analyzer.get_frame_rate() is None


class TestCompatibilityEdgeCases:
    """Test compatibility checker edge cases."""

    def test_casparcg_unsupported_codec(self):
        """Test CasparCG with unsupported codec."""
        from videowise.compatibility import CasparCGChecker

        video_info = {
            "codec": "vp9",
            "width": 1920,
            "height": 1080,
            "framerate": 25.0,
            "pixel_format": "yuv420p",
        }

        checker = CasparCGChecker()
        issues = checker.check(video_info)

        assert any("codec" in issue.message.lower() for issue in issues)

    def test_obs_unsupported_codec(self):
        """Test OBS with truly unsupported codec (line 227)."""
        from videowise.compatibility import OBSChecker

        video_info = {
            "codec": "theora",  # Old codec not in SUPPORTED_CODECS
            "container": "ogv",
        }

        checker = OBSChecker()
        issues = checker.check(video_info)

        # Should warn about limited support
        assert any("limited support" in issue.message.lower() for issue in issues)

    def test_vmix_no_issues_compatible(self):
        """Test vMix with perfect video (line 196)."""
        from videowise.compatibility import VmixChecker

        video_info = {
            "codec": "h264",
            "width": 1920,
            "height": 1080,
            "bitrate": 10000000,  # 10 Mbps - good
        }

        checker = VmixChecker()
        issues = checker.check(video_info)

        # Should get "compatible" or "should work" message when no issues
        assert any("supported" in issue.message.lower() for issue in issues)

    def test_obs_no_issues_compatible(self):
        """Test OBS with perfect video (line 263)."""
        from videowise.compatibility import OBSChecker

        video_info = {
            "codec": "h264",
            "container": "mp4",
        }

        checker = OBSChecker()
        issues = checker.check(video_info)

        # Should get supported message
        assert any("supported" in issue.message.lower() for issue in issues)

    def test_qlab_missing_codec(self):
        """Test QLab with missing/empty codec info (line 71)."""
        from videowise.compatibility import QLabChecker

        video_info = {
            "codec": "",  # Empty string should work
            "container": "mov",
        }

        checker = QLabChecker()
        issues = checker.check(video_info)

        # When codec is empty, should get warning about not performing well OR unable to determine
        assert len(issues) > 0

    def test_qlab_prores_non_hap_non_4444(self):
        """Test QLab with regular ProRes (line 304)."""
        from videowise.compatibility import QLabChecker

        video_info = {
            "codec": "prores_ks",  # Regular ProRes, not HAP or 4444
            "container": "mov",
        }

        checker = QLabChecker()
        issues = checker.check(video_info)

        assert any("compatible with qlab" in issue.message.lower() for issue in issues)

    def test_qlab_unsupported_codec(self):
        """Test QLab with unsupported codec (line 320)."""
        from videowise.compatibility import QLabChecker

        video_info = {
            "codec": "vp9",  # Not ProRes or H.264
            "container": "mov",
        }

        checker = QLabChecker()
        issues = checker.check(video_info)

        assert any("may not perform well" in issue.message.lower() for issue in issues)

    def test_qlab_wrong_container(self):
        """Test QLab with wrong container (line 331)."""
        from videowise.compatibility import QLabChecker

        video_info = {
            "codec": "prores",
            "container": "avi",  # Not MOV or MP4
        }

        checker = QLabChecker()
        issues = checker.check(video_info)

        assert any("mov or mp4" in issue.message.lower() for issue in issues)

    def test_propresenter_prores_non_hap(self):
        """Test ProPresenter with regular ProRes (line 390)."""
        from videowise.compatibility import ProPresenterChecker

        video_info = {
            "codec": "prores_ks",  # Not HAP
            "container": "mov",
        }

        checker = ProPresenterChecker()
        issues = checker.check(video_info)

        assert any("fully supported" in issue.message.lower() for issue in issues)

    def test_propresenter_h264(self):
        """Test ProPresenter with H.264 (line 405)."""
        from videowise.compatibility import ProPresenterChecker

        video_info = {
            "codec": "h264",
            "container": "mp4",
        }

        checker = ProPresenterChecker()
        issues = checker.check(video_info)

        assert any("compatible" in issue.message.lower() for issue in issues)

    def test_safari_wrong_container(self):
        """Test Safari with wrong container (line 437)."""
        from videowise.compatibility import SafariChecker

        video_info = {
            "codec": "h264",
            "container": "mkv",  # Not MP4
        }

        checker = SafariChecker()
        issues = checker.check(video_info)

        assert any("mp4 container" in issue.message.lower() for issue in issues)

    def test_chrome_unsupported_codec(self):
        """Test Chrome with unsupported codec (line 472)."""
        from videowise.compatibility import ChromeChecker

        video_info = {
            "codec": "prores",  # Not in supported list
        }

        checker = ChromeChecker()
        issues = checker.check(video_info)

        assert any("may not be supported" in issue.message.lower() for issue in issues)

    def test_twitter_wrong_codec(self):
        """Test Twitter with non-H.264 codec (line 559)."""
        from videowise.compatibility import TwitterChecker

        video_info = {
            "codec": "vp9",  # Not H.264
            "container": "mp4",
        }

        checker = TwitterChecker()
        issues = checker.check(video_info)

        assert any("recommends h.264" in issue.message.lower() for issue in issues)

    def test_twitter_wrong_container(self):
        """Test Twitter with wrong container (line 576)."""
        from videowise.compatibility import TwitterChecker

        video_info = {
            "codec": "h264",
            "container": "mkv",  # Not MP4 or MOV
        }

        checker = TwitterChecker()
        issues = checker.check(video_info)

        assert any("mp4 or mov" in issue.message.lower() for issue in issues)
