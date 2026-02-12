"""Setup configuration for VideoWise."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="videowise",
    version="0.1.0",
    author="Beau Bremer",
    author_email="beau@example.com",
    description="Video codec compatibility checker for live production and content creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KnowOneActual/video-codec-checker",
    project_urls={
        "Bug Tracker": "https://github.com/KnowOneActual/video-codec-checker/issues",
        "Documentation": "https://github.com/KnowOneActual/video-codec-checker/blob/main/README.md",
        "Source Code": "https://github.com/KnowOneActual/video-codec-checker",
        "Changelog": "https://github.com/KnowOneActual/video-codec-checker/blob/main/CHANGELOG.md",
        "Roadmap": "https://github.com/KnowOneActual/video-codec-checker/blob/main/ROADMAP.md",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "videowise=videowise.cli:main",
        ],
    },
    keywords="video codec compatibility ffmpeg live-production casparcg vmix obs qlab propresenter",
)
