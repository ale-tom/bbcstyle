## Summary
Explain the change and why it’s needed.

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Docs / examples
- [ ] Refactor / chore
- [ ] CI / packaging

## Screenshots (if visual)
_Add before/after images when plot styling changes._

## How to test locally
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
# run examples that this PR touches
python examples/gallery/01_bar_chart.py
