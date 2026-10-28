"""The book's two charts, kept out of the chapters so the notebooks show the analysis, not styling.

Blue and orange are the first two slots of a categorical palette checked for colour-vision
deficiency on a white background. Text stays grey or black; colour only marks which group a
dot or bar belongs to.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK_SOFT, GRID = "#262624", "#5f5e5a", "#e4e3df"


def _style(ax, grid_axis):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_SOFT, labelsize=9, length=0)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _symlog_ticks(low, high):
    """Round ticks (0, 3, 10, 30, ...) inside the observed score range, negatives included."""
    magnitudes = [m * 10**e for e in range(7) for m in (3, 10)]
    ticks = sorted(t for t in [0] + magnitudes + [-m for m in magnitudes] if low <= t <= high)
    return ticks if len(ticks) >= 2 else sorted({low, high})


def score_by_depth(scored, winners):
    """Every scored comment by reply depth; replies that outscored their parent in orange."""
    if scored.empty:  # e.g. a Hacker News thread, which has no comment scores
        raise ValueError("no visible scores to plot")
    rng = np.random.default_rng(3)  # fixed jitter so the chart is the same on every build
    x = scored.depth.astype(float) + rng.uniform(-0.18, 0.18, len(scored))
    is_winner = scored.comment_id.isin(winners.comment_id).to_numpy()
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
    for mask, colour, label in [(~is_winner, BLUE, "other comments"),
                                (is_winner, ORANGE, "reply that outscored its parent")]:
        ax.scatter(x[mask], scored.score[mask].astype(float), s=40, color=colour,
                   edgecolor="white", linewidth=1.2, label=label, zorder=3)
    if not winners.empty:
        top = winners.iloc[0]
        top_x = x[scored.comment_id.to_numpy() == top.comment_id].iloc[0]
        ax.annotate(f"{top.comment_id}: {top.score} points, its parent {top.parent_score}",
                    (top_x, float(top.score)), xytext=(-10, 4), textcoords="offset points",
                    ha="right", fontsize=8.5, color=INK_SOFT)
    # symlog, not log: a downvoted comment can score zero or less
    ax.set_yscale("symlog", linthresh=10)
    ax.set_yticks(_symlog_ticks(int(scored.score.min()), int(scored.score.max())))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks(range(int(scored.depth.max()) + 1))
    ax.set_xlabel("Reply depth (0 = top-level comment)", color=INK_SOFT)
    ax.set_ylabel("Score", color=INK_SOFT)
    ax.set_title("Scores fall with depth, but some replies beat their parent",
                 loc="left", color=INK, fontsize=11.5)
    _style(ax, "y")
    ax.legend(frameon=False, loc="upper right", labelcolor=INK_SOFT, fontsize=9)
    fig.tight_layout()
    return fig


def phrases_by_depth(table, title):
    """Stacked bars: how many comments use each phrase, top-level comments first, then replies."""
    table = table.iloc[::-1]  # matplotlib draws the first row at the bottom
    fig, ax = plt.subplots(figsize=(7.5, 0.34 * len(table) + 1.3), dpi=150)
    ax.barh(table.index, table["top-level"], color=BLUE, height=0.6,
            edgecolor="white", linewidth=2, label="top-level comments")
    ax.barh(table.index, table["replies"], left=table["top-level"], color=ORANGE, height=0.6,
            edgecolor="white", linewidth=2, label="replies")
    for y, total in enumerate(table["comments"]):
        ax.text(total + 0.08, y, str(total), va="center", fontsize=8.5, color=INK_SOFT)
    ax.set_xlim(0, table["comments"].max() + 1)
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_xlabel("Comments that use it", color=INK_SOFT)
    ax.set_title(title, loc="left", color=INK, fontsize=11.5)
    _style(ax, "x")
    ax.tick_params(axis="y", labelcolor=INK)
    ax.legend(frameon=False, loc="lower right", labelcolor=INK_SOFT, fontsize=9)
    fig.tight_layout()
    return fig
