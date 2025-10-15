"""
Bar chart styled with bbcstyle.

This script creates a simple bar chart and tries to enable the bbcstyle theme
if the installed package exposes a theme hook. It saves a PNG to ./examples/gallery/out/bar_chart.png.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes


def _try_enable_bbcstyle() -> None:
    """Enable the bbcstyle theme if a known hook exists."""
    try:
        import bbcstyle as bbc  # type: ignore
    except Exception:
        Warning("could not import bbcstyle")

    for attr in ("set_theme", "use", "mpl_style", "apply", "style"):
        fn = getattr(bbc, attr, None)
        if callable(fn):
            try:
                fn()
                return
            except Exception:
                continue


def bar_chart(
    categories: Iterable[str], values: Iterable[float]
) -> Tuple[Figure, Axes]:
    """Render a bar chart for the given categories and values."""
    _try_enable_bbcstyle()

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.bar(list(categories), list(values))
    ax.set_title("Example: Bar Chart (bbcstyle)")
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig, ax


if __name__ == "__main__":
    cats = ["A", "B", "C", "D", "E"]
    vals = [5, 7, 3, 6, 4]

    fig, _ = bar_chart(cats, vals)
    out_dir = Path(__file__).with_suffix("").parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "bar_chart.png"
    fig.savefig(out_path)
    print(f"Saved: {out_path}")
