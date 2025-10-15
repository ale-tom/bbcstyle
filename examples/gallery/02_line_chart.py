"""
Line chart styled with bbcstyle.

This script creates a small-multiples line plot and tries to enable the bbcstyle theme.
It saves a PNG to ./examples/gallery/out/line_chart.png.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np


def _try_enable_bbcstyle() -> None:
    """Enable the bbcstyle theme if a known hook exists."""
    try:
        import bbcstyle as bbc  # type: ignore
    except Exception:
        return

    for attr in ("set_theme", "use", "mpl_style", "apply", "style"):
        fn = getattr(bbc, attr, None)
        if callable(fn):
            try:
                fn()
                return
            except Exception:
                continue


def line_chart(series_labels: List[str], seed: int = 7) -> Tuple[Figure, Axes]:
    """Render a small-multiples line chart for several series with the same x domain."""
    _try_enable_bbcstyle()

    rng = np.random.default_rng(seed)
    x = np.arange(0, 24)
    y = [np.cumsum(rng.normal(0, 0.8, size=x.size)) for _ in series_labels]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    for yy, label in zip(y, series_labels):
        ax.plot(x, yy, label=label, linewidth=2)
    ax.set_title("Example: Line Chart (bbcstyle)")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Index")
    ax.legend(frameon=False, ncols=min(3, len(series_labels)))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig, ax


if __name__ == "__main__":
    labels = ["North", "South", "East", "West"]
    fig, _ = line_chart(labels)
    out_dir = Path(__file__).with_suffix("").parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "line_chart.png"
    fig.savefig(out_path)
    print(f"Saved: {out_path}")
