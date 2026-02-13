# VideoWise Roadmap

This roadmap outlines the development plan for VideoWise from initial concept through production-ready tool.

## ✅ Phase 1: Core Engine (COMPLETE - Feb 2026)

**Status:** All milestones achieved, 107 tests passing

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
- 107 passing tests with 94% code coverage

---

## ✅ Phase 2: User Interface (NEARLY COMPLETE)

**Target:** March 2026
**Priority:** HIGH - Make the tool actually usable
**Status:** 3 of 4 milestones complete

### Milestones

#### 2.1: Basic CLI (COMPLETE ✅)
- [x] Command-line argument parsing (Click framework)
- [x] Basic `videowise check <file>` command
- [x] System selection (`--system` flag)
- [x] Output formatting (clean, readable text)
- [x] Exit codes (0 = compatible, 1 = warnings, 2 = incompatible)
- [x] `--all` flag to check against all systems at once
- [x] Mutual exclusion validation (--system vs --all)

#### 2.2: Enhanced Output (COMPLETE ✅)
- [x] Colored terminal output (compatible=green, warning=yellow, incompatible=red)
- [x] Structured output formats (--json)
- [x] Verbose mode (`-v`) for debugging
- [x] Summary statistics (when using --all flag)
- [x] Multi-system result formatting with clear separators
- [ ] YAML output format
- [ ] Quiet mode (`-q`) for scripts

#### 2.3: Batch Operations (COMPLETE ✅)
- [x] Multiple file checking
- [x] Directory scanning (recursive and non-recursive)
- [x] File extension filtering
- [x] Batch summary statistics
- [x] JSON output for batch results
- [x] Error handling with continue-on-error
- [x] 27 comprehensive tests for batch functionality
- [ ] Playlist validation (M3U, JSON lists)
- [ ] Report generation (CSV, HTML, Markdown)
- [ ] Pre-show checklist mode

#### 2.4: Explanation System (PARTIAL) 🎯 NEXT
- [x] Human-readable explanations for each issue (via reasons/suggestions)
- [ ] Contextual help (`--explain` flag)
- [ ] Severity level explanations
- [ ] Real-world impact descriptions
- [ ] Enhanced formatting for explanations

### Deliverables
- ✅ Fully functional CLI tool
- ✅ Professional output formatting
- ✅ Multi-system checking capability
- ✅ Batch processing capability
- ✅ Comprehensive CLI documentation
- 🚧 Enhanced explanation formatter

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

1. ✅ **CLI tool** - COMPLETE!
2. ✅ **Check all systems at once** - COMPLETE!
3. ✅ **Batch processing** - COMPLETE!
4. **Report generation** - CSV/HTML/Markdown exports (NEXT)
5. **FFmpeg fix commands** - Automatic problem solving
6. **Linux Show Player support** - Requested by theater tech community
7. **YouTube/TikTok rules** - Content creator needs

---

## Recent Achievements 🎉

**February 13, 2026:**
- ✅ Implemented comprehensive batch processing feature
- ✅ Added `batch` command with directory scanning
- ✅ Recursive directory traversal with `--recursive` flag
- ✅ File extension filtering with `--extensions` option
- ✅ Batch summary statistics and reporting
- ✅ 27 new tests for batch functionality
- ✅ Complete documentation updates (CLI_USAGE.md, README.md)
- ✅ 107 total tests with 94% code coverage
- ✅ All linters passing (Black, isort, flake8, mypy)

**Earlier February 2026:**
- ✅ Implemented `--all` flag for multi-system checking
- ✅ Added comprehensive summary view with categorization
- ✅ 12 new tests for --all flag functionality
- ✅ JSON output support for multi-system results
- ✅ Complete CLI_USAGE.md documentation

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
- Add progress bars for batch processing
- Consider parallel processing for batch operations

---

## Success Metrics

**Phase 2 Goals:**
- ✅ CLI tool functional and tested
- ✅ Multi-system checking capability
- ✅ Batch processing capability
- 🎯 CLI tool used by 10+ beta testers
- 🎯 Positive feedback on usability
- ✅ Zero critical bugs in core engine

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

*Last updated: February 13, 2026*
