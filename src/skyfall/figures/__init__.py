"""Deterministic matplotlib figures for the skyfall (SILVA) mission.

Two deterministic figures back the manuscript:

* the Skyfall estate choke-point defense map
  (:func:`render_estate_defense_figure`), and
* the HQ traffic exfiltration-burst detection chart
  (:func:`render_traffic_figure`) — the residual traffic series with the
  CUSUM alarm and best change point annotated.

Matplotlib runs headless (Agg) and all styling is fixed, so every PNG is
byte-identical across runs.
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
from ..traffic_analysis import (
    DEFAULT_BASELINE_WINDOW,
    DEFAULT_TRAFFIC,
    analyze_traffic,
    detrend,
    periodic_baseline,
)

__all__ = [
    "render_estate_defense_figure",
    "render_traffic_figure",
    "DEFAULT_FIGURE_OUTPUT",
    "DEFAULT_TRAFFIC_FIGURE_OUTPUT",
]


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
    """Return the defensive-coverage fraction of a :class:`DefensePlan`.

    Deliberately typed ``object`` with an explicit ``isinstance`` gate: this
    is the figure layer's only entry point taking a domain object, it is
    reachable from the manuscript orchestrator, and a duck-typed near-miss
    would otherwise render a plausible but wrong coverage label onto the
    flagship figure.

    Raises:
        TypeError: if ``plan`` is not a :class:`DefensePlan`.
    """
    from ..estate_defense import DefensePlan, defense_coverage

    if not isinstance(plan, DefensePlan):
        raise TypeError(f"expected a DefensePlan, got {type(plan).__name__}")
    return defense_coverage(plan)


def _default_output_path() -> Path:
    return Path(__file__).resolve().parents[3] / "output" / "figures" / "estate_defense.png"


def render_traffic_figure(
    series: tuple[float, ...] = DEFAULT_TRAFFIC,
    output_path: str | Path | None = None,
) -> Path:
    """Render the HQ traffic detection chart to PNG and return its path.

    Plots the residualized traffic series (periodic baseline removed), marks
    the CUSUM alarm index and the best change point, and annotates the
    exfiltration burst window.

    Args:
        series: The traffic series to plot (defaults to the canonical one).
        output_path: Destination PNG path. Defaults to
            ``output/figures/traffic_detection.png`` under the package root.

    Returns:
        The resolved output path.
    """
    report = analyze_traffic(series)
    periodic = periodic_baseline(series, DEFAULT_BASELINE_WINDOW)
    residuals = detrend(series, periodic)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    hours = list(range(len(residuals)))
    ax.plot(hours, residuals, color="#1e3a8a", linewidth=1.1, label="residual traffic")
    ax.axhline(0.0, color="#94a3b8", linewidth=0.8)

    if report.cusum_alarm_index is not None:
        ax.axvline(
            report.cusum_alarm_index,
            color="#dc2626",
            linestyle="--",
            linewidth=1.4,
            label=f"CUSUM alarm @ hour {report.cusum_alarm_index}",
        )
    ax.axvline(
        report.best_change_point,
        color="#059669",
        linestyle=":",
        linewidth=1.4,
        label=f"best change point @ hour {report.best_change_point}",
    )

    ax.set_title(
        f"MI6 HQ Traffic — burst {'detected' if report.burst_detected else 'missed'}, max CUSUM {report.max_cusum:.1f}"
    )
    ax.set_xlabel("hour")
    ax.set_ylabel("residual packets/hour")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()

    path = Path(output_path) if output_path is not None else _default_traffic_output_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def _default_traffic_output_path() -> Path:
    return Path(__file__).resolve().parents[3] / "output" / "figures" / "traffic_detection.png"


#: Canonical default output location for the flagship figure.
DEFAULT_FIGURE_OUTPUT = _default_output_path()

#: Canonical default output location for the traffic detection figure.
DEFAULT_TRAFFIC_FIGURE_OUTPUT = _default_traffic_output_path()
