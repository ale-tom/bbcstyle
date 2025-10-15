from typing import Optional, Tuple
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


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
    divider_gap_pts: float = 10.0,
    enforce_size: bool = False,
) -> None:
    """
    Finalise and save a figure in a BBC-style layout. Titles and subtitles are added without forcing
    a resize unless enforce_size is True. If source text is provided, a grey divider is drawn at a
    constant point-based gap above the source's rendered bounding box so spacing is consistent across
    different figure sizes, fonts, and DPIs.
    """
    # Only resize if explicitly requested
    if enforce_size:
        fig.set_size_inches(*fig_size)

    # Leave extra top space only when we actually have a title/subtitle
    if title or subtitle:
        fig.subplots_adjust(top=0.82)

    # Title
    if title:
        fig.suptitle(title, x=0.05, y=0.99, ha="left")

    # Subtitle
    if subtitle:
        fig.text(
            0.05, 0.90, subtitle, ha="left", fontsize=17, transform=fig.transFigure
        )

    # Source + divider positioned from the measured text bbox (keeps constant gap)
    if source:
        # Draw the source first. Use va="bottom" so the bbox top is the reference for the divider.
        y_source = 0.012
        src_text = fig.text(
            0.5,
            y_source,
            source,
            ha="center",
            va="bottom",
            fontsize=14,
            color="#080808",
            transform=fig.transFigure,
        )

        # Force a render to get accurate text extents
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

        # Get bbox in display coords, convert to figure coords
        bbox_disp = src_text.get_window_extent(renderer=renderer)
        bbox_fig = bbox_disp.transformed(fig.transFigure.inverted())

        # Convert point gap to figure coords (independent of DPI/size)
        fig_h_in = fig.get_size_inches()[1]
        gap_fig = (divider_gap_pts / 72.0) / fig_h_in

        y_divider = bbox_fig.y1 + gap_fig

        # Full-width divider line across the figure
        fig.add_artist(
            Line2D(
                [0.0, 1.0],
                [y_divider, y_divider],
                transform=fig.transFigure,
                linewidth=2.0,
                color="#ACA6A6FF",
            )
        )

    # If we're going to paste a logo, save to temp first
    tmp_path = output_path
    if logo_path and output_path:
        tmp_path = output_path.replace(".png", "_tmp.png")

    # Save the figure
    if output_path:
        fig.savefig(tmp_path, dpi=dpi, facecolor="white")

    # Paste in the logo if requested
    if logo_path and output_path:
        background = Image.open(tmp_path)
        logo = Image.open(logo_path).convert("RGBA")
        background.paste(logo, logo_position, logo)
        background.save(output_path)
