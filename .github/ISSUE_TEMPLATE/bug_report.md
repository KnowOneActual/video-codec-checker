---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With video file '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
What actually happened.

**Video File Information**
Please provide the output of:
```bash
ffprobe -v error -show_format -show_streams -print_format json <your_video_file>
```

**Environment:**
 - OS: [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
 - Python Version: [e.g., 3.11]
 - VideoWise Version: [e.g., 0.1.0]
 - FFmpeg Version: [output of `ffmpeg -version`]

**Additional context**
Add any other context about the problem here.
