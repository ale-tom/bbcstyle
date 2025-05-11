# bbcstyle/finalise.py

import matplotlib.pyplot as plt
from PIL import Image
from typing import Optional, Tuple


# def finalise_plot(
#     fig: plt.Figure,
#     output_path: Optional[str] = None,
#     source: Optional[str] = None,
#     logo_path: Optional[str] = None,
#     logo_position: Tuple[int, int] = (30, 30),
#     fig_size: Tuple[int, int] = (12, 7),
#     dpi: int = 300,
# ) -> None:
#     """
#     Finalise and save the figure in BBC-style: sets figure size, optionally adds source text and a logo, and saves it.

#     - `source`: Bottom-left annotation, e.g. "Source: ONS"
#     - `logo_path`: Optional path to PNG logo image (placed at specified pixel offset)
#     - `fig_size`: Figure size in inches (width, height)
#     - `dpi`: Dots per inch for saving quality
#     """
#     fig.set_size_inches(*fig_size)
#     fig.tight_layout()

#     if source:
#         fig.text(0.01, 0.01, source, fontsize=10, color="#555555", ha="left")

#     # Save to temporary file if we need to add logo
#     tmp_path = output_path
#     if logo_path:
#         tmp_path = output_path.replace(".png", "_tmp.png")

#     if output_path:
#         fig.savefig(tmp_path, dpi=dpi, bbox_inches="tight", facecolor="white")

#     if logo_path:
#         # Add logo to the saved image using Pillow
#         background = Image.open(tmp_path)
#         logo = Image.open(logo_path).convert("RGBA")
#         background.paste(logo, logo_position, logo)  # use logo as mask for transparency
#         background.save(output_path)
#         # Optionally delete tmp_path if different


def finalise_plot(
    fig: plt.Figure,
    output_path: Optional[str] = None,
    source: Optional[str] = None,
    logo_path: Optional[str] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    logo_position: Tuple[int, int] = (30, 30),
    fig_size: Tuple[int, int] = (12, 7),
    dpi: int = 300,
) -> None:
    """
    Finalise and save the figure in BBC-style: set figure size, draw
    optional title, subtitle, source text and a logo, then save to disk.
    """
    # figure sizing & make room for titles
    fig.set_size_inches(*fig_size)
    # leave extra space at top for suptitle + subtitle
    fig.subplots_adjust(top=0.82)

    # main title
    if title:
        fig.suptitle(title, x=0.05, y=0.99, ha="left")

    # subtitle just under main title
    if subtitle:
        fig.text(
            0.05,  # centered in x
            0.90,  # just below the suptitle
            subtitle,
            ha="left",
            fontsize=17,
        )

    # source text in bottom-left
    if source:
        fig.text(
            0.01,
            0.001,
            source,
            fontsize=14,
            color="#555555",
            ha="left",
        )

    # if we're going to paste a logo, save to temp first
    tmp_path = output_path
    if logo_path and output_path:
        tmp_path = output_path.replace(".png", "_tmp.png")

    # save the figure
    if output_path:
        fig.savefig(tmp_path, dpi=dpi, facecolor="white")

    # paste in the logo if requested
    if logo_path and output_path:
        background = Image.open(tmp_path)
        logo = Image.open(logo_path).convert("RGBA")
        background.paste(logo, logo_position, logo)
        background.save(output_path)
