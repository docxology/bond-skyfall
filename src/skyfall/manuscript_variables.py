"""Manuscript variable hydration for skyfall.

Every ``{{TOKEN}}`` in ``manuscript/*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` plus the
deterministic outputs of the SILVA domain modules. Metrics are never
hand-authored in prose: they flow through this module so the manuscript cannot
drift from the code.

The consuming orchestrator is ``scripts/z_generate_manuscript_variables.py``
(thin wrapper); the live cross-reference gate lives in
``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .cyber_ops import (
    DEFAULT_ENTRY,
    DEFAULT_NETWORK,
    DEFAULT_TARGET,
    cheapest_intrusion_path,
    intrusion_paths,
    shortest_intrusion_path,
)
from .estate_defense import (
    DEFAULT_ESTATE,
    choke_points,
    defense_coverage,
    default_island,
    estate_defense_plan,
    island_topology,
)
from .exfiltration import (
    analyze_exfiltration,
)
from .legacy_audit import (
    audit_fleet,
    default_legacy_fleet,
    prioritize_remediation,
)
from .patch_strategy import (
    DEFAULT_DAILY_BUDGET,
    DEFAULT_HORIZON_DAYS,
    DEFAULT_VULNERABILITIES,
    analyze_patch_schedule,
)
from .traffic_analysis import (
    EXFIL_WINDOW,
    analyze_traffic,
)
from .mission import DEFENDERS, PACKAGE_VERSION, SILVA_SEED

__all__ = ["generate_variables", "load_manuscript_config", "resolve_manuscript_tree"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` → value mapping for the manuscript.

    All values are derived from the frozen domain modules (deterministic); no
    RNG or wall-clock enters a stable metric. ``GENERATION_TIMESTAMP`` is the
    sole non-deterministic token, matching the exemplar convention.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), verifies the domain modules
            produced a real intrusion path — the strict-mode gate.

    Raises:
        ValueError: if the intrusion target is unreachable in strict mode.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise ValueError("manuscript config 'paper' section must be a mapping")
    mission_block = config.get("mission", {})
    if not isinstance(mission_block, dict):
        raise ValueError("manuscript config 'mission' section must be a mapping")

    shortest = shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
    cheapest = cheapest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
    if require_outputs and shortest is None:
        raise ValueError("intrusion target is unreachable — skyfall domain core misconfigured")
    fleet = audit_fleet(default_legacy_fleet().values())
    remediation = prioritize_remediation(default_legacy_fleet().values(), budget=3)
    points = choke_points(DEFAULT_ESTATE)
    defense = estate_defense_plan(DEFAULT_ESTATE, DEFENDERS)
    island = island_topology(default_island())

    traffic = analyze_traffic()
    exfil = analyze_exfiltration()
    patches = analyze_patch_schedule()

    num_intrusion_paths = len(intrusion_paths(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET))
    shortest_hops = len(shortest.hosts) - 1 if shortest is not None else 0
    cheapest_hops = len(cheapest.hosts) - 1 if cheapest is not None else 0

    return {
        "SILVA_FILM": str(paper.get("film", "skyfall")),
        "SILVA_CODENAME": str(mission_block.get("codename", "SILVA")),
        "SILVA_TITLE": str(paper.get("title", "")),
        "SILVA_SUBTITLE": str(paper.get("subtitle", "")),
        "SILVA_VERSION": PACKAGE_VERSION,
        "SILVA_MISSION_VERSION": str(paper.get("version", "")),
        "SILVA_SEED": str(SILVA_SEED),
        "SILVA_NUM_NETWORK_NODES": str(len(DEFAULT_NETWORK.nodes)),
        "SILVA_ENTRY": DEFAULT_ENTRY,
        "SILVA_TARGET": DEFAULT_TARGET,
        "SILVA_NUM_INTRUSION_PATHS": str(num_intrusion_paths),
        "SILVA_SHORTEST_HOPS": str(shortest_hops),
        "SILVA_CHEAPEST_HOPS": str(cheapest_hops),
        "SILVA_BURST_DETECTED": "yes" if traffic.burst_detected else "no",
        "SILVA_ALARM_INDEX": str(traffic.cusum_alarm_index) if traffic.cusum_alarm_index is not None else "none",
        "SILVA_BEST_CHANGE_POINT": str(traffic.best_change_point),
        "SILVA_EXFIL_WINDOW": f"{EXFIL_WINDOW[0]}–{EXFIL_WINDOW[1]}",
        "SILVA_MAX_FLOW": f"{exfil['max_flow']:.1f}",
        "SILVA_MIN_CUT_VALUE": f"{exfil['min_cut_value']:.1f}",
        "SILVA_SEVERANCE": ", ".join(exfil["severance"]) if exfil["severance"] else "none",
        "SILVA_FLEET_SIZE": str(fleet.fleet_size),
        "SILVA_MEAN_EXPOSURE": f"{fleet.mean_exposure:.2f}",
        "SILVA_MAX_EXPOSURE": f"{fleet.max_exposure:.2f}",
        "SILVA_CRITICAL_COUNT": str(fleet.critical_count),
        "SILVA_FLEET_RISK": fleet.risk(),
        "SILVA_REMEDIATION_TARGETS": ", ".join(a.system_id for a in remediation),
        "SILVA_NUM_VULNERABILITIES": str(len(DEFAULT_VULNERABILITIES)),
        "SILVA_HORIZON_DAYS": str(DEFAULT_HORIZON_DAYS),
        "SILVA_DAILY_BUDGET": f"{DEFAULT_DAILY_BUDGET:.0f}",
        "SILVA_PATCHED_COUNT": str(patches["patched_count"]),
        "SILVA_PATCH_BASELINE": f"{patches['baseline_exposure']:.1f}",
        "SILVA_PATCH_SCHEDULED": f"{patches['scheduled_exposure']:.1f}",
        "SILVA_PATCH_REDUCTION": f"{patches['reduction_ratio']:.0%}",
        "SILVA_NUM_CHOKE_POINTS": str(len(points)),
        "SILVA_CHOKE_POINTS": ", ".join(points) if points else "none",
        "SILVA_NUM_DEFENDERS": str(len(DEFENDERS)),
        "SILVA_COVERAGE": f"{defense_coverage(defense):.2f}",
        "SILVA_ISLAND_CORRIDOR": str(island.corridor_length),
        "SILVA_ISLAND_HIDEOUT": f"{island.hideout[0]},{island.hideout[1]}",
        "PYTHON_VERSION": platform.python_version(),
        "GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def resolve_manuscript_tree(
    variables: dict[str, str],
    *,
    manuscript_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    strict: bool = True,
) -> tuple[Path, list[str]]:
    """Copy each manuscript section to ``output/manuscript/``, substituting tokens.

    Only ``NN_*.md`` section files are copied (not sidecars such as
    ``SYNTAX.md`` or ``AGENTS.md``). In strict mode any leftover ``{{TOKEN}}``
    fails the resolution so the manuscript can never render with raw braces.

    Returns:
        The output directory and the sorted list of resolved file names.
    """
    manuscript_dir = Path(manuscript_dir) if manuscript_dir is not None else PACKAGE_ROOT / "manuscript"
    output_dir = Path(output_dir) if output_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    resolved: list[str] = []
    for source in sorted(manuscript_dir.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        for token, value in variables.items():
            text = text.replace("{{" + token + "}}", value)
        unresolved = sorted(set(_TOKEN_RE.findall(text)))
        if unresolved and strict:
            raise ValueError(f"unresolved manuscript tokens in {source.name}: {unresolved}")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source.name).write_text(text, encoding="utf-8")
        resolved.append(source.name)
    return output_dir, resolved
