# VideoWise Roadmap

This roadmap outlines the development plan for VideoWise from initial concept through production-ready tool.

## ✅ Phase 1: Core Engine (COMPLETE - Feb 2026)

**Status:** All milestones achieved, 45 tests passing

### Milestones
- [x] Project structure and test framework
- [x] FFprobe integration for metadata extraction
- [x] Codec/container/profile parsing
- [x] Compatibility rules engine architecture
- [x] 9 system compatibility checkers
- [x] Comprehensive test coverage

### Deliverables
- `VideoAnalyzer` class for file analysis
- `CompatibilityChecker` base class and engine
- 5 live production system checkers (CasparCG, vMix, OBS, QLab, ProPresenter)
- 2 browser checkers (Safari, Chrome)
- 2 social media checkers (Instagram, Twitter/X)
- 45 passing tests

---

## 🚧 Phase 2: User Interface (IN PROGRESS)

**Target:** March 2026
**Priority:** HIGH - Make the tool actually usable

### Milestones

#### 2.1: Basic CLI (Week 1)
- [ ] Command-line argument parsing (argparse/click)
- [ ] Basic `videowise check <file>` command
- [ ] System selection (`--system` flag)
- [ ] Output formatting (clean, readable text)
- [ ] Exit codes (0 = compatible, 1 = warnings, 2 = incompatible)

#### 2.2: Enhanced Output (Week 2)
- [ ] Colored terminal output (compatible=green, warning=yellow, incompatible=red)
- [ ] Structured output formats (--json, --yaml)
- [ ] Verbose mode (`-v`, `-vv`) for debugging
- [ ] Quiet mode (`-q`) for scripts
- [ ] Summary statistics

#### 2.3: Batch Operations (Week 3)
- [ ] Multiple file checking
- [ ] Directory scanning
- [ ] Playlist validation (M3U, JSON lists)
- [ ] Report generation (CSV, HTML)
- [ ] Pre-show checklist mode

#### 2.4: Explanation System (Week 4)
- [ ] Human-readable explanations for each issue
- [ ] Contextual help (`--explain` flag)
- [ ] Severity level explanations
- [ ] Real-world impact descriptions

### Deliverables
- Fully functional CLI tool
- Professional output formatting
- Batch processing capability
- User documentation for CLI

---

## 📦 Phase 3: Distribution & Additional Systems

**Target:** April-May 2026
**Priority:** MEDIUM

### Milestones

#### 3.1: Package Distribution
- [ ] setup.py for pip installation
- [ ] pyproject.toml for modern Python packaging
- [ ] Publish to PyPI (`pip install videowise`)
- [ ] Homebrew formula for macOS
- [ ] Debian/Ubuntu package
- [ ] Docker image for containerized use

#### 3.2: Additional Live Production Systems
- [ ] Linux Show Player compatibility checker
- [ ] Wirecast compatibility checker
- [ ] Playback Pro compatibility checker
- [ ] Renewed Vision PVP compatibility checker
- [ ] Resolume compatibility checker

#### 3.3: Additional Platforms
- [ ] Firefox browser compatibility
- [ ] YouTube upload requirements
- [ ] TikTok platform requirements
- [ ] Vimeo platform requirements
- [ ] Facebook/Meta video requirements
- [ ] LinkedIn video requirements

#### 3.4: Video Editor Compatibility
- [ ] Adobe Premiere Pro import rules
- [ ] DaVinci Resolve compatibility
- [ ] Final Cut Pro compatibility
- [ ] Avid Media Composer rules

### Deliverables
- PyPI package
- 15+ system compatibility checkers
- Installation packages for major platforms

---

## 🔧 Phase 4: Advanced Features

**Target:** June-August 2026
**Priority:** LOW (nice-to-have)

### Milestones

#### 4.1: Fix Generation
- [ ] Generate ffmpeg commands to fix issues
- [ ] Transcode recommendation engine
- [ ] Batch fix script generation
- [ ] Safe transcoding profiles (preserve quality)
- [ ] Interactive fix mode (prompt before converting)

#### 4.2: Automation Features
- [ ] Watch folder mode (auto-check new files)
- [ ] Pre-commit git hook for video files
- [ ] CI/CD integration (GitHub Actions, GitLab CI)
- [ ] Slack/Discord notifications for issues
- [ ] Email reports for batch operations

#### 4.3: Production Workflow Tools
- [ ] Pre-show verification mode (checklist output)
- [ ] Playlist compatibility validator
- [ ] Show documentation generator
- [ ] Equipment compatibility matrix
- [ ] Performance prediction ("will this play smoothly?")

#### 4.4: Web Interface
- [ ] Simple web UI (Flask or FastAPI)
- [ ] Drag-and-drop file upload
- [ ] Visual compatibility reports
- [ ] Shareable result links
- [ ] REST API for integration

### Deliverables
- FFmpeg fix command generator
- Automation and integration tools
- Web interface for non-technical users
- REST API

---

## 🔮 Phase 5: Advanced Intelligence (Future)

**Target:** TBD (2027+)
**Priority:** RESEARCH

### Potential Features
- Machine learning for system-specific performance prediction
- Historical compatibility database (crowdsourced real-world data)
- Automatic profile detection ("this looks like a CasparCG workflow")
- Integration with media asset management systems
- Live playback performance monitoring
- Codec conversion quality prediction
- Network streaming compatibility (RTMP, SRT, NDI)

---

## Community Input Priorities

**Top Requests** (to be updated based on issues/discussions):

1. **CLI tool** - Most requested feature
2. **FFmpeg fix commands** - Automatic problem solving
3. **Batch processing** - Check entire libraries
4. **Linux Show Player support** - Requested by theater tech community
5. **YouTube/TikTok rules** - Content creator needs

---

## Technical Debt & Maintenance

**Ongoing:**
- Keep compatibility rules updated as platforms change
- Add regression tests for new edge cases
- Performance optimization for large file batches
- Documentation updates
- Security updates for dependencies

**Backlog:**
- Consider async file processing for better performance
- Add caching layer for repeated checks
- Improve error messages for missing ffprobe
- Add logging framework for debugging

---

## Success Metrics

**Phase 2 Goals:**
- CLI tool used by 10+ beta testers
- Positive feedback on usability
- Zero critical bugs in core engine

**Phase 3 Goals:**
- 100+ PyPI downloads per month
- 5+ community contributions
- 20+ systems supported

**Phase 4 Goals:**
- 1000+ users
- Integration into production workflows
- Featured in industry publications/forums

---

## Contributing to the Roadmap

We want YOUR input:

- **What features would make this tool essential for your workflow?**
- **What systems/platforms are we missing?**
- **What priority would you assign to each phase?**

Open an [issue](https://github.com/KnowOneActual/video-codec-checker/issues) or [discussion](https://github.com/KnowOneActual/video-codec-checker/discussions) to shape the roadmap!

---

*Last updated: February 9, 2026*
