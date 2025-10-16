"""
Bar chart styled with bbcstyle.

Creates a simple bar chart, enables the bbcstyle theme via the package hook,
uses the theme's color cycle for bar colors, and finishes with
bbcstyle.finalise_plot (title, subtitle, source, logo, save).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple
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
    Enable the BBC theme via the official hook if available. Prefers root-level
    hooks (set_theme/use) and falls back to bbcstyle.theme.bbc_theme. If nothing
    is available, Matplotlib defaults are kept.
    """
    try:
        import bbcstyle as bbc  # type: ignore[attr-defined]

        for name in ("set_theme", "use"):
            fn = getattr(bbc, name, None)
            if callable(fn):
                fn()
                return
    except Exception:
        pass

    try:
        from bbcstyle.theme import bbc_theme  # type: ignore

        bbc_theme()
    except Exception:
        pass


def _theme_colors(n: int) -> List[str]:
    """
    Return n colors taken from the current theme's axes.prop_cycle. If fewer colors
    are defined than needed, the list is cycled to length n.
    """
    cycle = plt.rcParams.get("axes.prop_cycle")
    colors: List[str] = []
    if cycle is not None:
        colors = cycle.by_key().get("color", [])
    if not colors:
        colors = ["#1f77b4"]  # safe fallback

    # Extend by cycling if n > len(colors)
    return [colors[i % len(colors)] for i in range(n)]


def bar_chart(
    categories: Iterable[str],
    values: Iterable[float],
    *,
    title: str = "Example: Bar Chart (bbcstyle)",
    subtitle: Optional[str] = None,
    source: Optional[str] = None,
    logo_path: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Tuple[Figure, Axes]:
    """
    Render a bar chart for the given categories and values, enable the bbcstyle theme,
    color each bar using the theme's color cycle, and finish with bbcstyle.finalise_plot
    for consistent framing and saving.
    """
    _enable_bbcstyle_theme()

    cats = list(categories)
    vals = np.asarray(list(values), dtype=float)
    bar_colors = _theme_colors(len(cats))

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.bar(cats, vals, color=bar_colors)

    # Clean axes; the theme may add gridlines and typography
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")

    # Let the finaliser handle titles, subtitle, source, logo, margins, and saving
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
    cats = ["A", "B", "C", "D", "E"]
    vals = [5, 7, 3, 6, 4]

    out_path = Path(__file__).with_suffix("").parent / "out" / "bar_chart.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, _ = bar_chart(
        cats,
        vals,
        title="Example: Bar Chart",
        subtitle="Five categories coloured by the theme cycle",
        source="Source: Example data",
        logo_path=None,  # e.g. "assets/bbc_logo.png"
        output_path=out_path,
    )
    print(f"Saved: {out_path}")
