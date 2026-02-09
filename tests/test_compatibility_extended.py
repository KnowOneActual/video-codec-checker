"""Extended tests for all compatibility checkers."""

import pytest
from videowise.compatibility import (
    OBSChecker,
    QLabChecker,
    ProPresenterChecker,
    SafariChecker,
    ChromeChecker,
    InstagramChecker,
    TwitterChecker,
    CompatibilityLevel,
    check_compatibility,
)


# OBS Studio Tests
def test_obs_h264_compatible():
    """Test that H.264 is fully supported by OBS."""
    checker = OBSChecker()
    video_info = {'codec': 'h264', 'container': 'mkv'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_obs_mkv_container():
    """Test that MKV is recognized as OBS default."""
    checker = OBSChecker()
    video_info = {'codec': 'h264', 'container': 'matroska,webm'}
    
    issues = checker.check(video_info)
    assert any('mkv' in issue.message.lower() for issue in issues)


# QLab Tests
def test_qlab_prores_proxy_optimal():
    """Test that ProRes Proxy is optimal for QLab."""
    checker = QLabChecker()
    video_info = {'codec': 'prores_proxy', 'container': 'mov'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any('best performance' in issue.message.lower() for issue in issues)


def test_qlab_h264_warning():
    """Test that H.264 gets performance warning in QLab."""
    checker = QLabChecker()
    video_info = {'codec': 'h264', 'container': 'mov'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any('scrubbing' in issue.message.lower() or 'speed' in issue.message.lower() for issue in issues)


def test_qlab_prores4444_alpha():
    """Test that ProRes 4444 is recognized for alpha channel."""
    checker = QLabChecker()
    video_info = {'codec': 'prores4444', 'container': 'mov'}
    
    issues = checker.check(video_info)
    assert any('alpha' in issue.message.lower() or 'transparency' in issue.message.lower() for issue in issues)


# ProPresenter Tests
def test_propresenter_hap_optimal():
    """Test that HAP is optimal for ProPresenter."""
    checker = ProPresenterChecker()
    video_info = {'codec': 'hap', 'container': 'mov'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)
    assert any('best performance' in issue.message.lower() or 'gpu' in issue.message.lower() for issue in issues)


def test_propresenter_unsupported_codec():
    """Test that unsupported codecs are rejected."""
    checker = ProPresenterChecker()
    video_info = {'codec': 'vp9', 'container': 'webm'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)


def test_propresenter_prores4444():
    """Test ProRes 4444 alpha support."""
    checker = ProPresenterChecker()
    video_info = {'codec': 'prores4444', 'container': 'mov'}
    
    issues = checker.check(video_info)
    assert any('alpha' in issue.message.lower() for issue in issues)


# Safari Tests
def test_safari_h264_compatible():
    """Test that Safari supports H.264."""
    checker = SafariChecker()
    video_info = {'codec': 'h264', 'container': 'mp4'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_safari_vp9_incompatible():
    """Test that Safari doesn't support VP9."""
    checker = SafariChecker()
    video_info = {'codec': 'vp9', 'container': 'webm'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    assert any('does not support' in issue.message.lower() for issue in issues)


def test_safari_hevc_supported():
    """Test that Safari supports HEVC."""
    checker = SafariChecker()
    video_info = {'codec': 'hevc', 'container': 'mp4'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Chrome Tests
def test_chrome_vp9_compatible():
    """Test that Chrome supports VP9."""
    checker = ChromeChecker()
    video_info = {'codec': 'vp9', 'container': 'webm'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_chrome_av1_compatible():
    """Test that Chrome supports AV1."""
    checker = ChromeChecker()
    video_info = {'codec': 'av1', 'container': 'mp4'}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


# Instagram Tests
def test_instagram_h264_baseline_optimal():
    """Test that H.264 Baseline is optimal for Instagram."""
    checker = InstagramChecker()
    video_info = {'codec': 'h264', 'profile': 'Constrained Baseline', 'resolution': (1080, 1920)}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_instagram_high_profile_warning():
    """Test that High Profile triggers re-encode warning."""
    checker = InstagramChecker()
    video_info = {'codec': 'h264', 'profile': 'High', 'resolution': (1080, 1920)}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.WARNING for issue in issues)
    assert any('baseline' in issue.message.lower() for issue in issues)


def test_instagram_resolution_downscale():
    """Test that high resolution triggers downscale warning."""
    checker = InstagramChecker()
    video_info = {'codec': 'h264', 'profile': 'Baseline', 'resolution': (3840, 2160)}
    
    issues = checker.check(video_info)
    assert any('downscale' in issue.message.lower() for issue in issues)


def test_instagram_wrong_codec():
    """Test that non-H.264 triggers warning."""
    checker = InstagramChecker()
    video_info = {'codec': 'prores', 'resolution': (1080, 1920)}
    
    issues = checker.check(video_info)
    assert any('re-encode' in issue.message.lower() for issue in issues)


# Twitter Tests
def test_twitter_h264_compatible():
    """Test that H.264 is compatible with Twitter."""
    checker = TwitterChecker()
    video_info = {'codec': 'h264', 'container': 'mp4', 'file_size': 100*1024*1024}
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.COMPATIBLE for issue in issues)


def test_twitter_file_size_limit_standard():
    """Test that file size limit is enforced for standard accounts."""
    checker = TwitterChecker(account_type="standard")
    video_info = {'codec': 'h264', 'container': 'mp4', 'file_size': 600*1024*1024}  # 600MB
    
    issues = checker.check(video_info)
    assert any(issue.level == CompatibilityLevel.INCOMPATIBLE for issue in issues)
    assert any('exceeds' in issue.message.lower() for issue in issues)


def test_twitter_file_size_ok_premium():
    """Test that premium accounts have higher limits."""
    checker = TwitterChecker(account_type="premium")
    video_info = {'codec': 'h264', 'container': 'mp4', 'file_size': 1024*1024*1024}  # 1GB
    
    issues = checker.check(video_info)
    # Should not have incompatible file size issue
    assert not any(issue.level == CompatibilityLevel.INCOMPATIBLE and 'exceeds' in issue.message.lower() for issue in issues)


# Integration Tests
def test_check_compatibility_all_systems():
    """Test that check_compatibility works for all systems."""
    video_info = {'codec': 'h264', 'container': 'mp4'}
    
    systems = ['casparcg', 'vmix', 'obs', 'qlab', 'propresenter', 'safari', 'chrome', 'instagram', 'twitter']
    
    for system in systems:
        issues = check_compatibility(video_info, system)
        assert len(issues) > 0, f"No issues returned for {system}"
