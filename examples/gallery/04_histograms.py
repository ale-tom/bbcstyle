"""
Blue wave-style histogram with two upright panels and brick-stacked bars.

Democrats are shown in the top panel and Republicans in the bottom panel. Each
panel stacks "Didn't win" (light shade) and "Won seat" (dark shade). The legend
uses custom stacked symbols that combine blue (Dem) and red (Rep). The y-axes
have no spines or tick marks — only the numeric labels remain for readability.

Running this file saves a PNG to ./examples/gallery/out/blue_wave_histogram.png.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Callable, Optional, List

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase
from matplotlib.ticker import FixedLocator, FuncFormatter
import warnings
import sys

try:
    from bbcstyle.finalise_plot import finalise_plot
except Exception as exc:
    warnings.warn(f"bbcstyle.finalise_plot not available: {exc}")


# Optional: allow running examples without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _try_enable_bbcstyle() -> None:
    """Try to enable the bbcstyle theme if available, otherwise keep defaults."""
    try:
        import bbcstyle as bbc  # type: ignore
    except Exception as exc:
        warnings.warn(f"bbcstyle not available: {exc}")
        return

    for attr in ("set_theme", "use", "mpl_style", "apply", "style"):
        fn: Optional[Callable[[], None]] = getattr(bbc, attr, None)  # type: ignore[attr-defined]
        if callable(fn):
            try:
                fn()
                return
            except Exception as exc:
                warnings.warn(f"bbcstyle.{attr}() failed: {exc}")
    warnings.warn("bbcstyle import succeeded but no known theme hook was found.")


@dataclass
class VoteData:
    """Vote-share changes and outcomes for one party, using fractional deltas."""

    delta: np.ndarray
    won: np.ndarray


def make_synthetic_votes(
    n: int, mean: float, sd: float, bias: float, seed: int
) -> VoteData:
    """Generate synthetic vote-share deltas and a correlated win/lose outcome.

    Deltas are normal(mean, sd) clipped to ±22%. Win probability rises with
    positive delta via a logistic curve centered using `bias`.
    """
    rng = np.random.default_rng(seed)
    delta = rng.normal(mean, sd, size=n)
    delta = np.clip(delta, -0.22, 0.25)
    p = 1.0 / (1.0 + np.exp(-(delta - bias) / max(sd * 0.75, 1e-6)))
    won = rng.random(n) < p
    return VoteData(delta=delta, won=won)


def _stacked_hist_counts(
    x: np.ndarray, mask_top: np.ndarray, bins: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return counts for top mask and its complement in the same bins."""
    c_top, _ = np.histogram(x[mask_top], bins=bins)
    c_bottom, _ = np.histogram(x[~mask_top], bins=bins)
    return c_top.astype(float), c_bottom.astype(float)


def _draw_bricklines(
    ax: plt.Axes,
    lefts: np.ndarray,
    widths: np.ndarray,
    heights: np.ndarray,
    line_color: str = "white",
) -> None:
    """Overlay white horizontal separators so bars look like stacked bricks."""
    for l, w, h in zip(lefts, widths, heights):
        if h <= 1:
            continue
        # integer separators at y = 1..h-1
        ys = np.arange(1, int(h))
        ax.hlines(ys, l, l + w, colors=line_color, linewidths=0.8, zorder=4)


class StackedSymbol:
    """Lightweight payload for custom legend handle, carrying two colors."""

    def __init__(self, top_color: str, bottom_color: str) -> None:
        self.top_color = top_color
        self.bottom_color = bottom_color


class StackedHandler(HandlerBase):
    """Draw two stacked rectangles inside the legend handle area."""

    def create_artists(
        self,
        legend: mpl.legend.Legend,
        orig_handle: StackedSymbol,
        x0: float,
        y0: float,
        width: float,
        height: float,
        fontsize: float,
        trans,
    ):
        h2 = height / 2.0
        r_top = Rectangle(
            (x0, y0 + h2), width, h2, facecolor=orig_handle.top_color, edgecolor="none"
        )
        r_bottom = Rectangle(
            (x0, y0), width, h2, facecolor=orig_handle.bottom_color, edgecolor="none"
        )
        r_top.set_transform(trans)
        r_bottom.set_transform(trans)
        return [r_bottom, r_top]


def _percent_xtick(x: float, _: int) -> str:
    """Format x ticks as percent with a special multi-line label at 0%."""
    if np.isclose(x, 0.0):
        return "0% change in\nvote share"
    s = f"{x * 100:.0f}%"
    return s if x < 0 else f"+{s}"


def plot_blue_wave(
    dem: VoteData,
    rep: VoteData,
    bins: Iterable[float] = np.linspace(-0.20, 0.20, 41),
    title: str = "Blue wave",
    savepath: Path | None = None,
) -> tuple[plt.Figure, List[plt.Axes]]:
    """Render two upright, stacked-panel histograms with BBC-like styling."""
    # Gentle defaults (overridden if your theme applies)
    mpl.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.linestyle": ":",
            "grid.linewidth": 0.7,
            "grid.alpha": 0.35,
            "axes.titleweight": "bold",
            "axes.titlesize": 28,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
        }
    )
    _try_enable_bbcstyle()

    # Palette (dark = won, light = didn't win)
    blue_dark, blue_light = "#1e5aa6", "#7fb0e6"
    red_dark, red_light = "#c72727", "#f2a7a7"

    bins = np.asarray(list(bins))
    widths = np.diff(bins)
    lefts = bins[:-1]

    # Histogram counts
    dem_win, dem_lose = _stacked_hist_counts(dem.delta, dem.won, bins)
    rep_win, rep_lose = _stacked_hist_counts(rep.delta, rep.won, bins)
    dem_total = dem_win + dem_lose
    rep_total = rep_win + rep_lose
    ymax = int(np.ceil(max(dem_total.max(), rep_total.max()) / 5.0) * 5.0)

    # Figure + two upright panels
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, sharex=True, figsize=(8.4, 10.8), dpi=170, gridspec_kw={"hspace": 0.08}
    )
    fig.suptitle(title, x=0.06, y=0.98, ha="left", va="top", fontsize=30, weight="bold")

    # Helper to style a panel (no visible y-axis line, show labels only)
    def _style_panel(ax: plt.Axes) -> None:
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.xaxis.set_tick_params(width=0)
        ax.set_ylim(0, ymax)
        ax.grid(axis="x", which="major", alpha=0)
        ax.grid(axis="x", which="minor", alpha=0)
        ax.grid(axis="y", which="major", alpha=0.20, ls="-", lw=2)

    # Top: Democrats
    ax_top.xaxis.set_visible(False)
    ax_top.axvline(0, color="black", linestyle="--", linewidth=1.2, zorder=5)
    ax_top.bar(
        lefts,
        dem_lose,
        width=widths,
        align="edge",
        color=blue_light,
        edgecolor="white",
        linewidth=0.9,
        zorder=2,
    )
    ax_top.bar(
        lefts,
        dem_win,
        width=widths,
        align="edge",
        bottom=dem_lose,
        color=blue_dark,
        edgecolor="white",
        linewidth=0.9,
        zorder=3,
    )
    _draw_bricklines(ax_top, lefts, widths, dem_total)
    _style_panel(ax_top)
    ax_top.text(
        0,
        0.98,
        "Democrat candidates",
        transform=ax_top.transAxes,
        ha="left",
        va="center",
        fontsize=18,
        weight="bold",
    )
    ax_top.axhline(linewidth=5, y=0, color="black", zorder=10)

    # Bottom: Republicans
    ax_bot.axvline(0, color="black", linestyle="--", linewidth=1.2, zorder=5)
    ax_bot.bar(
        lefts,
        rep_lose,
        width=widths,
        align="edge",
        color=red_light,
        edgecolor="white",
        linewidth=0.9,
        zorder=2,
    )
    ax_bot.bar(
        lefts,
        rep_win,
        width=widths,
        align="edge",
        bottom=rep_lose,
        color=red_dark,
        edgecolor="white",
        linewidth=0.9,
        zorder=3,
    )
    _draw_bricklines(ax_bot, lefts, widths, rep_total)
    _style_panel(ax_bot)
    ax_bot.text(
        0,
        0.98,
        "Republican candidates",
        transform=ax_bot.transAxes,
        ha="left",
        va="center",
        fontsize=18,
        weight="bold",
    )

    # Shared X
    ax_bot.xaxis.set_major_locator(FixedLocator([-0.20, -0.10, 0.00, 0.10, 0.20]))
    ax_bot.xaxis.set_minor_locator(plt.MultipleLocator(0.05))
    ax_bot.xaxis.set_major_formatter(FuncFormatter(_percent_xtick))
    ax_bot.tick_params(axis="x", which="both", length=0, pad=15)
    ax_bot.set_xlim(bins[0], bins[-1])

    # Y ticks as values, no axis line
    yticks = list(range(0, ymax + 1, 10))
    ax_top.set_yticks(yticks)
    ax_bot.set_yticks(yticks)
    ax_bot.axhline(linewidth=5, y=0, color="black", zorder=10)

    # Legend with stacked symbols (blue over red)
    won_handle = StackedSymbol(top_color=blue_dark, bottom_color=red_dark)
    lose_handle = StackedSymbol(top_color=blue_light, bottom_color=red_light)

    leg = ax_top.legend(
        [won_handle, lose_handle],
        ["Won seat", "Didn't win"],
        handler_map={StackedSymbol: StackedHandler()},
        loc="upper left",
        bbox_to_anchor=(-0.08, 1.13),
        frameon=False,
        borderaxespad=0.0,
        handlelength=1.2,
        handleheight=0.3,  # adjust with your marker size
        ncols=2,
        alignment="center",
    )
    for txt in leg.get_texts():
        try:
            txt.set_va("center_baseline")  # best when available
        except Exception:
            txt.set_va("center")
        txt.set_fontsize(12)

    # Example annotations
    ax_top.annotate(
        "Sharice Davids, the joint-first\nNative American woman\nin Congress, increased\nDem vote share by 13%",
        xy=(0.14, max(dem_total.max() * 0.16, 1)),
        xytext=(0.08, ymax * 0.6),
        ha="left",
        va="center",
        fontsize=9,
        arrowprops=dict(
            arrowstyle="-", connectionstyle="arc3,rad=-0.25", color="gray", lw=1.5
        ),
    )
    ax_bot.annotate(
        "Republicans held onto\nOregon 2 and Ohio 12,\ndespite a 15% swing\nagainst them",
        xy=(-0.145, max(rep_total.max() * 0.10, 1)),
        xytext=(-0.18, ymax * 0.7),
        ha="left",
        va="center",
        fontsize=9,
        arrowprops=dict(
            arrowstyle="-", connectionstyle="arc3,rad=0.25", color="gray", lw=1.5
        ),
    )

    finalise_plot(
        fig=fig,
        logo_path="assets/bbc_logo.png",
        source="Source: Simulated data | original design by BBC",
        logo_zoom=0.5,
        logo_vertical_pad_pts=-2,
        divider_gap_pts=6,
    )

    # Save
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    if savepath is not None:
        savepath.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(savepath, dpi=220, bbox_inches="tight")

    return fig, [ax_top, ax_bot]


if __name__ == "__main__":
    # Tuned synthetic data to evoke a "blue wave" (illustrative only)
    dem = make_synthetic_votes(n=260, mean=0.06, sd=0.05, bias=0.00, seed=7)
    rep = make_synthetic_votes(n=260, mean=-0.06, sd=0.05, bias=0.00, seed=11)

    out_path = Path(__file__).with_suffix("").parent / "out" / "blue_wave_histogram.png"
    fig, _ = plot_blue_wave(dem, rep, savepath=out_path)
    print(f"Saved: {out_path}")
