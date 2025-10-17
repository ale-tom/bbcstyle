# Changelog
All notable changes to this project will be documented here.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.


## [0.1.1] - 2025-10-17

### Changed
- Packaging: move `license-files` to `[project]` to silence Setuptools deprecation.
- Packaging: stop including non-runtime images from repo-root `assets/` in the wheel.
- README: switch gallery images to absolute GitHub URLs so they render on PyPI.

### Added
- Tooling: `.pre-commit-config.yaml` with Ruff + basic hygiene hooks.

### Fixed
- Trusted Publishing configuration to PyPI (release now uploads correctly).

## [0.1.0] - 2025-10-16

### Added
- Initial PyPI packaging via `pyproject.toml` (PEP 621).
- Gallery examples:
  - `examples/gallery/01_bar_chart.py`
  - `examples/gallery/02_line_chart.py`
  - `examples/gallery/03_scatter_plot.py`
  - `examples/gallery/04_histograms.py`
  - `examples/gallery/05_bubble_scatter.py`
- GitHub Actions workflow to publish to PyPI on release (Trusted Publishing).
- Issue/PR templates and contributing guidance.

### Changed
- README: install/quick-start, gallery links, authorship, support, and licensing notes.

### Notes
- Python 3.8–3.12 supported.
- Dependencies: Matplotlib ≥ 3.5, Seaborn ≥ 0.12.
