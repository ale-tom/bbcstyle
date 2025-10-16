# examples/gallery/05_bubble_scatter.py
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Import finalise_plot from bbcstyle library (support both layouts)
try:
    from bbcstyle.finalise_plot import finalise_plot
except Exception as exc:
    warnings.warn(f"finalise_plot not available: {exc}")


def enable_bbcstyle_theme() -> None:
    """
    Enable the BBC theme via the official hook. Prefers root-level hooks and falls back
    to the submodule hook if needed. If nothing is available, it keeps Matplotlib defaults.
    """
    try:
        import bbcstyle as bbc  # type: ignore
    except Exception as exc:  # pragma: no cover
        warnings.warn(f"bbcstyle not available: {exc}")
        return

    # Official hook first
    for name in ("set_theme", "use"):
        fn = getattr(bbc, name, None)  # type: ignore[attr-defined]
        if callable(fn):
            fn()
            return

    # Fallback to submodule name if exposed
    try:
        from bbcstyle.theme import bbc_theme  # type: ignore

        bbc_theme()
        return
    except Exception:
        pass

    warnings.warn("bbcstyle import succeeded but no known theme hook was found.")


def _mock_cities(n: int = 900, seed: int = 7) -> pd.DataFrame:
    """
    Create a synthetic city dataset with a positive correlation between vulnerability and growth.
    Two cities (Lagos, Kinshasa) are appended for callouts.
    """
    rng = np.random.default_rng(seed)
    regions = np.array(["Africa", "Asia", "Americas", "Europe", "Oceania"])
    region = rng.choice(regions, size=n, p=[0.28, 0.42, 0.18, 0.10, 0.02])

    vulnerability = rng.beta(a=1.3, b=2.2, size=n)
    growth_pct = np.clip(
        0.6 + 4.8 * vulnerability + rng.normal(0.0, 0.7, size=n), 0.0, 6.0
    )
    population_m = np.clip(np.exp(rng.normal(1.2, 0.9, size=n)), 0.1, 30.0)

    df = pd.DataFrame(
        {
            "region": region,
            "vulnerability": vulnerability,
            "growth_pct": growth_pct,
            "population_m": population_m,
        }
    )
    # Append highlighted cities
    df.loc[len(df)] = ["Africa", 0.86, 4.1, 14.9]  # Lagos
    df.loc[len(df)] = ["Africa", 0.90, 4.7, 15.6]  # Kinshasa
    df.loc[df.index[-2:], "name"] = ["Lagos", "Kinshasa"]
    return df


def _palette() -> Dict[str, str]:
    """
    Provide a categorical palette for regions.
    """
    return {
        "Africa": "#b55b49",
        "Asia": "#ffb339",
        "Americas": "#0e8ccb",
        "Europe": "#ad68f6",
        "Oceania": "#496009",
    }


def _bubble_sizes(pop_m: Iterable[float], base: float = 18.0) -> np.ndarray:
    """
    Convert population in millions into scatter marker areas. Square-root scaling
    keeps large cities prominent without overwhelming the chart.
    """
    p = np.asarray(list(pop_m))
    return base * (np.sqrt(p) ** 2)


def plot_bubble_scatter(
    df: pd.DataFrame,
    title: str,
    subtitle: str,
    source: str,
    logo_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (12, 8),
) -> plt.Figure:
    """
    Draw a BBC-style bubble scatter where x is vulnerability (0-1) and y is growth rate (0-6%).
    The function applies your BBC theme hook, hides the y-axis, and finishes with finalise_plot.
    """

    enable_bbcstyle_theme()

    fig, ax = plt.subplots(figsize=figsize)

    # Clean axes: hide y-axis entirely, keep subtle horizontal guides
    ax.set_facecolor("white")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(2.0)

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 6.0)

    ax.set_yticks([0, 2, 4, 6], labels=["0%", "2%", "4%", "6%"])
    ax.grid(axis="y", linestyle="-", linewidth=0.8, color="#E6E6E6")
    ax.tick_params(axis="y", which="both", left=False, labelleft=True, pad=1)

    ax.set_xticks([])
    ax.axhline(0.0, color="black", linewidth=2.0)
    ax.text(
        0.1,
        -0.03,
        "Less vulnerable",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=14,
    )
    ax.text(
        0.9,
        -0.03,
        "More vulnerable",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=14,
    )

    # Plot by region for legend control
    palette = _palette()
    for region, g in df.groupby("region", sort=False):
        ax.scatter(
            g["vulnerability"],
            g["growth_pct"],
            s=_bubble_sizes(g["population_m"]),
            c=palette.get(region, "#999999"),
            alpha=0.6,
            linewidths=0.3,
            edgecolors="white",
            label=region,
        )

    # Legend across top-left
    present = [
        r
        for r in ("Africa", "Asia", "Americas", "Europe", "Oceania")
        if r in df["region"].unique()
    ]
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markersize=9,
            markerfacecolor=palette[r],
            alpha=0.9,
            markeredgewidth=0.0,
            label=r,
        )
        for r in present
    ]
    ax.legend(
        handles=handles,
        labels=present,
        loc="upper left",
        frameon=False,
        ncol=5,
        handletextpad=0.4,
        columnspacing=1.2,
        borderaxespad=0.0,
        fontsize=11,
        bbox_to_anchor=(-0.11, 1.07),
    )

    # Callouts for Lagos & Kinshasa (if present)
    for name in ("Lagos", "Kinshasa"):
        subset = df[df.get("name", "") == name]
        if not subset.empty:
            x, y = subset[["vulnerability", "growth_pct"]].iloc[0]
            ax.scatter(
                [x],
                [y],
                s=_bubble_sizes([subset["population_m"].iloc[0]]) * 1.15,
                facecolors="none",
                edgecolors="#222222",
                linewidths=1.6,
            )
            ax.annotate(
                name,
                xy=(x, y),
                xytext=(x + 0.04, y + 0.35),
                textcoords="data",
                ha="center",
                va="center",
                arrowprops={"arrowstyle": "-", "lw": 1.2, "color": "#222222"},
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"),
                fontsize=12,
            )

    # "Growing" arrow near bottom-right
    ax.annotate(
        "Growing",
        xy=(0.87, 0.2),
        xytext=(0.87, 0.02),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "#222222"},
        ha="center",
        va="bottom",
        fontsize=12,
    )

    finalise_plot(
        fig=fig,
        output_path=str(output_path),
        source=source,
        title=title,
        subtitle=subtitle,
        logo_path=str(logo_path),
        dpi=300,
        logo_zoom=0.5,
        logo_vertical_pad_pts=-2,
        divider_gap_pts=6,
    )
    return fig


if __name__ == "__main__":
    out_path = Path("examples/gallery/out/bubble_scatter.png")
    logo_path = Path("assets/bbc_logo.png")
    df = _mock_cities()
    plot_bubble_scatter(
        df=df,
        title="Fast-growing cities face worse climate risks",
        subtitle="Population growth 2018–2035 over climate change vulnerability",
        source="Source: Simulated data | design by BBC.",
        logo_path=logo_path,
        output_path=out_path,
        figsize=(12, 8),
    )
    print(f"Saved: {out_path}")
