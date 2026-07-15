"""Shared plotting style and figure/output-path helpers for the report figures."""

from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"

# Consistent colours per career pathway, used across every figure in this project.
PATHWAY_COLOURS = {
    "academic": "#3B6FA0",       # blue
    "industry_data": "#2E8B57",  # green
    "industry_quant": "#D9631E",  # orange
}
PATHWAY_LABELS = {
    "academic": "Academic / research",
    "industry_data": "Industry (data / technical)",
    "industry_quant": "Industry (quant)",
}


def set_report_style():
    """Applies a clean, consistent matplotlib style for the report figures."""
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 10.5,
        "axes.labelsize": 10.5,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "legend.fontsize": 9.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "lines.linewidth": 1.8,
        "axes.edgecolor": "0.3",
    })


def savefig(fig, name, formats=("png",), dpi=200):
    """Saves `fig` to FIGURES_DIR under `name`, then closes it."""
    FIGURES_DIR.mkdir(exist_ok=True)
    for ext in formats:
        path = FIGURES_DIR / f"{name}.{ext}"
        fig.savefig(path, dpi=dpi)
        print(f"saved {path.relative_to(PROJECT_ROOT)}")
    plt.close(fig)


def format_gbp(value, _pos=None):
    """Matplotlib tick formatter: shows values as £ with thousands separators."""
    return f"£{value:,.0f}"
