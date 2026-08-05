"""Legacy-fleet patch scheduling: minimize cumulative exposure over a horizon.

The SILVA mission's maintenance layer closes the loop opened by
:mod:`skyfall.legacy_audit`: an audit says *which* systems are exposed, but a
response plan must say *when* each known vulnerability gets patched under a
finite daily patching budget. This module implements that deterministic
scheduling problem:

* :class:`Vulnerability` — a known weakness on a legacy system, with a
  severity, the day it was discovered, and a patching effort (in budget
  units);
* :func:`fleet_exposure` — the cumulative fleet exposure over a horizon with
  no patching (each unpatched vulnerability contributes its severity every
  day from discovery onward);
* :func:`schedule_patches` — a deterministic greedy scheduler: every day it
  spends the daily budget on the *highest-severity* unpatched
  vulnerabilities (ties broken lexicographically by vulnerability id);
* :func:`exposure_with_schedule` — the cumulative exposure given a patch
  schedule (a vulnerability stops contributing the day it is patched);
* :func:`reduction` — the absolute and relative exposure reduction of a
  schedule against the no-patching baseline.

The canonical scenario (``DEFAULT_VULNERABILITIES``) is a fixed set of
vulnerabilities over the legacy fleet from :mod:`skyfall.legacy_audit`, with
discovery days staggered across a 30-day horizon. All math is closed-form
and deterministic; no RNG or wall-clock enters any result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "Vulnerability",
    "ScheduleEntry",
    "PatchSummary",
    "fleet_exposure",
    "schedule_patches",
    "exposure_with_schedule",
    "reduction",
    "DEFAULT_VULNERABILITIES",
    "DEFAULT_HORIZON_DAYS",
    "DEFAULT_DAILY_BUDGET",
]


@dataclass(frozen=True)
class Vulnerability:
    """A known vulnerability on a legacy system."""

    vuln_id: str
    system_id: str
    severity: float
    discovered_day: int
    patch_effort: float = 1.0

    def __post_init__(self) -> None:
        if not self.vuln_id.strip():
            raise ValueError("Vulnerability.vuln_id must be non-empty")
        if not self.system_id.strip():
            raise ValueError("Vulnerability.system_id must be non-empty")
        if not 0.0 <= self.severity <= 10.0:
            raise ValueError("Vulnerability.severity must be in [0, 10]")
        if self.discovered_day < 0:
            raise ValueError("Vulnerability.discovered_day must be >= 0")
        if self.patch_effort <= 0:
            raise ValueError("Vulnerability.patch_effort must be positive")


@dataclass(frozen=True)
class ScheduleEntry:
    """One patching action: patch ``vuln_id`` on ``day``."""

    day: int
    vuln_id: str
    system_id: str


@dataclass(frozen=True)
class PatchSummary:
    """Aggregate outcome of a patch schedule over the horizon."""

    baseline_exposure: float
    scheduled_exposure: float
    reduction_abs: float
    reduction_ratio: float
    entries: tuple[ScheduleEntry, ...]
    patched_count: int


def fleet_exposure(
    vulnerabilities: tuple[Vulnerability, ...],
    horizon_days: int,
) -> float:
    """Return cumulative fleet exposure over ``horizon_days`` with no patching.

    Each vulnerability contributes ``severity`` for every day from its
    discovery day through the end of the horizon (exclusive).

    Args:
        vulnerabilities: The known vulnerabilities.
        horizon_days: Number of days in the exposure horizon.

    Returns:
        Cumulative exposure (severity-days).
    """
    total = 0.0
    for vuln in vulnerabilities:
        if vuln.discovered_day >= horizon_days:
            continue
        days = horizon_days - vuln.discovered_day
        total += vuln.severity * days
    return total


def schedule_patches(
    vulnerabilities: tuple[Vulnerability, ...],
    horizon_days: int,
    daily_budget: float,
) -> tuple[ScheduleEntry, ...]:
    """Greedily schedule patching within a daily budget.

    Each day ``d`` in ``0 .. horizon_days - 1``, the scheduler spends the
    daily budget on the unpatched, already-discovered vulnerabilities with the
    highest severity (ties broken by ``vuln_id``). A vulnerability can only be
    patched on or after its discovery day.

    Args:
        vulnerabilities: The known vulnerabilities.
        horizon_days: Number of days in the scheduling horizon.
        daily_budget: Patching capacity (in effort units) available each day.

    Returns:
        An ordered tuple of :class:`ScheduleEntry`.
    """
    if horizon_days < 0:
        raise ValueError("horizon_days must be >= 0")
    if daily_budget <= 0:
        raise ValueError("daily_budget must be positive")
    pending = {vuln.vuln_id: vuln for vuln in vulnerabilities}
    entries: list[ScheduleEntry] = []
    for day in range(horizon_days):
        available = [vuln for vuln in pending.values() if vuln.discovered_day <= day]
        if not available:
            continue
        # Highest severity first, then lexicographic vuln_id for ties.
        ordered = sorted(available, key=lambda v: (-v.severity, v.vuln_id))
        budget_left = daily_budget
        for vuln in ordered:
            if budget_left < vuln.patch_effort:
                continue
            entries.append(ScheduleEntry(day=day, vuln_id=vuln.vuln_id, system_id=vuln.system_id))
            del pending[vuln.vuln_id]
            budget_left -= vuln.patch_effort
    return tuple(entries)


def exposure_with_schedule(
    vulnerabilities: tuple[Vulnerability, ...],
    entries: tuple[ScheduleEntry, ...],
    horizon_days: int,
) -> float:
    """Return cumulative exposure given a patch schedule.

    A vulnerability contributes its severity for every day from discovery
    until the day it is patched (patched day itself excluded, since the patch
    lands at the start of that day).

    Args:
        vulnerabilities: The known vulnerabilities.
        entries: The patch schedule (as produced by :func:`schedule_patches`).
        horizon_days: Number of days in the exposure horizon.

    Returns:
        Cumulative exposure (severity-days).
    """
    patched_day: dict[str, int] = {}
    for entry in entries:
        patched_day[entry.vuln_id] = entry.day
    total = 0.0
    for vuln in vulnerabilities:
        end_day = patched_day.get(vuln.vuln_id, horizon_days)
        if end_day <= vuln.discovered_day:
            continue
        total += vuln.severity * (end_day - vuln.discovered_day)
    return total


def reduction(
    vulnerabilities: tuple[Vulnerability, ...],
    entries: tuple[ScheduleEntry, ...],
    horizon_days: int,
) -> PatchSummary:
    """Compare a schedule against the no-patching baseline.

    Args:
        vulnerabilities: The known vulnerabilities.
        entries: The patch schedule.
        horizon_days: Number of days in the exposure horizon.

    Returns:
        A :class:`PatchSummary` with baseline and scheduled exposure plus the
        absolute and relative reduction.
    """
    baseline = fleet_exposure(vulnerabilities, horizon_days)
    scheduled = exposure_with_schedule(vulnerabilities, entries, horizon_days)
    absolute = baseline - scheduled
    ratio = absolute / baseline if baseline > 0 else 0.0
    return PatchSummary(
        baseline_exposure=baseline,
        scheduled_exposure=scheduled,
        reduction_abs=absolute,
        reduction_ratio=ratio,
        entries=entries,
        patched_count=len(entries),
    )


#: Canonical vulnerability set over the legacy fleet (fixed constants).
#: Discoveries are CLUSTERED (days 1-6) — a single security sweep reveals the
#: backlog at once — so the daily budget of one patch forces real scheduling
#: contention and the greedy order is observable.
DEFAULT_VULNERABILITIES: tuple[Vulnerability, ...] = (
    Vulnerability("VULN-001", "registry_arch", 9.8, 1),
    Vulnerability("VULN-002", "ldap", 9.2, 1),
    Vulnerability("VULN-003", "registry_arch", 8.9, 1),
    Vulnerability("VULN-004", "field_ops", 8.1, 2),
    Vulnerability("VULN-005", "exchange", 7.4, 2),
    Vulnerability("VULN-006", "ldap", 6.9, 3),
    Vulnerability("VULN-007", "vpn_edge", 6.2, 3),
    Vulnerability("VULN-008", "exchange", 5.5, 4),
    Vulnerability("VULN-009", "field_ops", 7.8, 4),
    Vulnerability("VULN-010", "vpn_edge", 6.6, 5),
    Vulnerability("VULN-011", "registry_arch", 5.9, 5),
    Vulnerability("VULN-012", "ldap", 5.1, 6),
)

#: The canonical scheduling horizon (30 days).
DEFAULT_HORIZON_DAYS = 30

#: The canonical daily patching budget (effort units per day).
DEFAULT_DAILY_BUDGET = 1.0


def analyze_patch_schedule(
    vulnerabilities: tuple[Vulnerability, ...] = DEFAULT_VULNERABILITIES,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    daily_budget: float = DEFAULT_DAILY_BUDGET,
) -> dict[str, Any]:
    """Run the full scheduling analysis and return a deterministic summary.

    Args:
        vulnerabilities: The known vulnerabilities.
        horizon_days: Number of days in the scheduling horizon.
        daily_budget: Patching capacity available each day.

    Returns:
        A dict with the schedule, patched count, and the reduction metrics.
    """
    entries = schedule_patches(vulnerabilities, horizon_days, daily_budget)
    summary = reduction(vulnerabilities, entries, horizon_days)
    return {
        "schedule": [(e.day, e.vuln_id) for e in entries],
        "patched_count": summary.patched_count,
        "baseline_exposure": round(summary.baseline_exposure, 4),
        "scheduled_exposure": round(summary.scheduled_exposure, 4),
        "reduction_abs": round(summary.reduction_abs, 4),
        "reduction_ratio": round(summary.reduction_ratio, 4),
    }
