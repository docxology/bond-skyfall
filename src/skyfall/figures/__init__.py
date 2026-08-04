"""Deterministic matplotlib figures for the skyfall (SILVA) mission.

A single flagship figure — the Skyfall estate choke-point defense map — is
generated so the manuscript has a reproducible visual artifact per the film
package contract ("figures/ for at least one concept"). The figure renders the
estate approach graph with articulation (choke) points highlighted and the
assigned defenders annotated; matplotlib runs headless (Agg) and all styling
is fixed, so the PNG is byte-identical across runs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from ..estate_defense import (
    DEFAULT_ESTATE,
    EstateGraph,
    choke_points,
    estate_defense_plan,
)

__all__ = ["render_estate_defense_figure", "DEFAULT_FIGURE_OUTPUT"]


def render_estate_defense_figure(
    graph: EstateGraph = DEFAULT_ESTATE,
    defenders: tuple[str, ...] | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Render the estate defense figure to PNG and return its path.

    Args:
        graph: The estate approach graph (defaults to the canonical one).
        defenders: Defender call signs for the plan (defaults to the SILVA set).
        output_path: Destination PNG path. Defaults to
            ``output/figures/estate_defense.png`` under the package root.

    Returns:
        The resolved output path.
    """
    if defenders is None:
        from ..mission import DEFENDERS

        defenders = DEFENDERS
    plan = estate_defense_plan(graph, defenders)
    points = choke_points(graph)

    fig, ax = plt.subplots(figsize=(8, 5))
    # Draw edges as straight segments.
    for src, connected in graph.roads.items():
        x1, y1 = graph.positions[src]
        for dst in connected:
            if src < dst:  # draw each undirected edge once
                x2, y2 = graph.positions[dst]
                ax.plot([x1, x2], [y1, y2], color="#64748b", linewidth=1.2, zorder=1)

    # Draw non-choke positions as plain nodes.
    for name, (x, y) in graph.positions.items():
        if name not in points:
            ax.scatter([x], [y], s=220, color="#1e3a8a", zorder=2)
            ax.text(x, y + 0.15, name, ha="center", fontsize=8, color="#0f172a")

    # Draw choke points prominently in red with their defender label.
    for name in points:
        x, y = graph.positions[name]
        ax.scatter([x], [y], s=320, color="#dc2626", zorder=3, edgecolor="#7f1d1d", linewidth=1.5)
        defender = plan.assigned.get(name, "")
        label = f"{name}\n[{defender}]" if defender else f"{name}\n[UNCOVERED]"
        ax.text(x, y + 0.3, label, ha="center", fontsize=8, color="#7f1d1d", weight="bold")

    ax.set_title(
        f"Skyfall Estate Defense — {len(points)} choke points, "
        f"{plan.defenders_used} defenders, coverage {defense_coverage_fraction(plan):.0%}"
    )
    ax.set_xlabel("position (row)")
    ax.set_ylabel("position (col)")
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()

    path = Path(output_path) if output_path is not None else _default_output_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def defense_coverage_fraction(plan: object) -> float:
    """Return the defensive-coverage fraction from a DefensePlan (as a float)."""
    from ..estate_defense import DefensePlan, defense_coverage

    if not isinstance(plan, DefensePlan):
        raise TypeError("expected a DefensePlan")
    return defense_coverage(plan)


def _default_output_path() -> Path:
    return Path(__file__).resolve().parents[3] / "output" / "figures" / "estate_defense.png"


#: Canonical default output location for the flagship figure.
DEFAULT_FIGURE_OUTPUT = _default_output_path()
