"""
Line chart styled with bbcstyle.

Creates a multi-series line chart, enables the bbcstyle theme via the package hook,
and finishes the figure with bbcstyle.finalise_plot (title, subtitle, source, logo, save).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


try:
    from bbcstyle.finalise_plot import finalise_plot
except Exception as exc:
    warnings.warn(f"bbcstyle.finalise_plot not available: {exc}")


def _enable_bbcstyle_theme() -> None:
    """
    Enable the BBC theme via the official hook if available.
    Prefers root-level hooks (set_theme/use), falls back to bbcstyle.theme.bbc_theme.
    """
    try:
        import bbcstyle as bbc  # type: ignore

        for name in ("set_theme", "use"):
            fn = getattr(bbc, name, None)  # type: ignore[attr-defined]
            if callable(fn):
                fn()
                return
    except Exception:
        pass

    # Fallback: submodule hook
    try:
        from bbcstyle.theme import bbc_theme  # type: ignore

        bbc_theme()
    except Exception:
        # If neither hook exists, keep Matplotlib defaults.
        pass


def line_chart(
    series_labels: List[str],
    seed: int = 7,
    *,
    title: str = "Example: Line Chart (bbcstyle)",
    subtitle: Optional[str] = None,
    source: Optional[str] = None,
    logo_path: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Tuple[Figure, Axes]:
    """
    Render a multi-series line chart, enable the bbcstyle theme, ensure distinct line colors,
    and finish with bbcstyle.finalise_plot for consistent framing and saving.
    """
    _enable_bbcstyle_theme()

    rng = np.random.default_rng(seed)
    x = np.arange(0, 24)
    y = [np.cumsum(rng.normal(0, 0.8, size=x.size)) for _ in series_labels]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)

    for yy, label in zip(y, series_labels):
        ax.plot(x, yy, label=label, linewidth=2)

    # Minimal, clean axes styling (theme may add grid etc.)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Index")

    # Legend
    ax.legend(frameon=False, ncols=4, bbox_to_anchor=(0.5, 1.1))

    finalise_plot(
        fig=fig,
        output_path=str(output_path) if output_path is not None else None,
        # source=source,
        title=title,
        subtitle=subtitle,
        logo_path=logo_path,
        dpi=300,
        enforce_size=True,
    )
    return fig, ax


if __name__ == "__main__":
    labels = ["North", "South", "East", "West"]
    fig, _ = line_chart(
        labels,
        title="Regional index over the day",
        subtitle="Four regions, hourly values (synthetic data)",
        source="Source: Example data",
        logo_path=None,  # e.g. "assets/bbc_logo.png"
        output_path=Path(__file__).with_suffix("").parent / "out" / "line_chart.png",
    )
    out_path = Path(__file__).with_suffix("").parent / "out" / "line_chart.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    print(f"Saved: {out_path}")
