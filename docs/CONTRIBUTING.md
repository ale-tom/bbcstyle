# Contributing to bbcstyle

Thanks for your interest in contributing!

- **Issues first for big changes.** For small fixes, feel free to open a PR directly.
- **Dev setup**
  ```bash
  python -m venv .venv && source .venv/bin/activate
  python -m pip install -U pip
  python -m pip install -e .
  python -m pip install -U pytest ruff pre-commit
  pre-commit install
