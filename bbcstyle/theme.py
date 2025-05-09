# bbplot/theme.py
import matplotlib as mpl
import seaborn as sns


def bbc_theme(font_family: str = "DejaVu Sans") -> None:
    """
    Apply the BBC visual style globally using Matplotlib rcParams and register it for Seaborn.

    This sets bold titles, sans-serif font, minimal spines, no ticks, and light gridlines.
    Call this before plotting with Matplotlib or Seaborn to use the BBC theme.
    """
    base_color = "#222222"
    grid_color = "#cbcbcb"
    accent_color = "#007f7f"

    rc = {
        # Font and text
        "font.family": font_family,
        "axes.titlesize": 28,
        "axes.titleweight": "bold",
        "axes.titlecolor": base_color,
        "axes.labelsize": 0,  # BBC typically omits axis labels
        "xtick.labelsize": 18,
        "ytick.labelsize": 18,
        "text.color": base_color,
        # Axes
        "axes.edgecolor": "none",  # No spines
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.prop_cycle": mpl.cycler(color=[accent_color]),
        # Gridlines
        "grid.color": grid_color,
        "grid.linestyle": "-",
        "grid.linewidth": 1,
        # Ticks
        "xtick.bottom": False,
        "xtick.top": False,
        "ytick.left": False,
        "ytick.right": False,
        # Legend
        "legend.frameon": False,
        "legend.loc": "upper center",
        "legend.framealpha": 0,
        "legend.fontsize": 18,
    }

    mpl.rcParams.update(rc)

    # Also register as a seaborn style
    sns.set_style("whitegrid", rc=rc)
