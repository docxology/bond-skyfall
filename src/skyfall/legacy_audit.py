"""Legacy-system vulnerability audit of aging MI6 infrastructure.

The SILVA mission's operations layer audits the aging, under-maintained
systems that still underpin MI6's active networks. The film's plot hinges on a
security officer's compromised laptop and a tapping of Director M's systems —
aging infrastructure that was never designed for the modern threat
environment. This module makes that exposure measurable and deterministic:

* :func:`exposure_score` maps a legacy system's attributes (age, patch level,
  protocol vintage, open services) to a scalar risk in ``[0, 1]``;
* :func:`audit_fleet` evaluates a whole fleet and returns aggregate exposure,
  the risk-tier histogram, and the count of critical systems;
* :func:`prioritize_remediation` ranks systems by risk-reduction-per-effort so
  finite patching resources go where they reduce fleet exposure fastest.

Everything is pure and deterministic: scores are closed-form, ordering ties
break on system id, and no wall-clock or RNG appears in any persisted number.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "LegacySystem",
    "FleetAudit",
    "exposure_score",
    "audit_fleet",
    "prioritize_remediation",
    "EXPOSURE_THRESHOLDS",
]


@dataclass(frozen=True)
class LegacySystem:
    """A legacy system with the attributes driving its exposure.

    Args:
        system_id: Stable identifier (used for deterministic tie-breaking).
        name: Human-readable host/service name.
        age_years: Years the system has been in service (drives obsolescence).
        patch_level: Fraction of known security patches applied, in ``[0, 1]``.
        protocol_era: Era index of its dominant protocol; 0 = modern, higher =
            more obsolete (TLS 1.0 / telnet / legacy directory transports).
        open_services: Number of externally reachable services (attack surface).
        classification: Optional label (e.g. "classified", "operational").
    """

    system_id: str
    name: str
    age_years: float = 10.0
    patch_level: float = 0.5
    protocol_era: int = 1
    open_services: int = 3
    classification: str = "operational"

    def __post_init__(self) -> None:
        if not self.system_id.strip():
            raise ValueError("LegacySystem.system_id must be non-empty")
        if not self.name.strip():
            raise ValueError("LegacySystem.name must be non-empty")
        if self.age_years < 0:
            raise ValueError("LegacySystem.age_years must be >= 0")
        if not 0.0 <= self.patch_level <= 1.0:
            raise ValueError("LegacySystem.patch_level must be in [0, 1]")
        if self.protocol_era < 0:
            raise ValueError("LegacySystem.protocol_era must be >= 0")
        if self.open_services < 0:
            raise ValueError("LegacySystem.open_services must be >= 0")


#: Exposure tiers as (max_score_exclusive_or_inclusive, label) ordered ascending.
EXPOSURE_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (0.3, "low"),
    (0.6, "medium"),
    (0.8, "high"),
    (float("inf"), "critical"),
)


def _tier(score: float) -> str:
    for threshold, label in EXPOSURE_THRESHOLDS:
        if score < threshold:
            return label
    return "critical"


def exposure_score(system: LegacySystem) -> float:
    """Return the deterministic exposure score of a single legacy system.

    The score blends four independent risk factors, each normalized to
    ``[0, 1]`` and linearly combined with fixed weights:

    * age ::math:`s_a = min(age / 25, 1)` — older systems are more obsolete;
    * unpatched ::math:`s_p = 1 - patch_level` — more unpatched = more at risk;
    * protocol ::math:`s_r = min(protocol_era / 3, 1)` — obsolete protocols;
    * surface ::math:`s_s = min(open_services / 6, 1)` — more services exposed.

    Weights: age 0.25, unpatched 0.35, protocol 0.20, surface 0.20.

    Returns:
        A score in ``[0, 1]``.
    """
    s_age = min(system.age_years / 25.0, 1.0)
    s_patch = 1.0 - system.patch_level
    s_proto = min(system.protocol_era / 3.0, 1.0)
    s_surf = min(system.open_services / 6.0, 1.0)
    return round(0.25 * s_age + 0.35 * s_patch + 0.20 * s_proto + 0.20 * s_surf, 4)


@dataclass(frozen=True)
class FleetAudit:
    """Aggregate outcome of auditing a legacy-system fleet."""

    scores: dict[str, float]
    tiers: dict[str, tuple[str, ...]]
    tier_counts: dict[str, int]
    mean_exposure: float
    max_exposure: float
    critical_count: int
    fleet_size: int

    def risk(self) -> str:
        """Return a coarse overall fleet risk label."""
        if self.critical_count > 0:
            return "critical"
        if self.mean_exposure >= 0.6:
            return "high"
        if self.mean_exposure >= 0.4:
            return "medium"
        return "low"


def audit_fleet(systems: Iterable[LegacySystem]) -> FleetAudit:
    """Audit a fleet of legacy systems and return aggregate exposure metrics.

    Args:
        systems: The systems to audit.

    Returns:
        A :class:`FleetAudit` with per-system scores, tier membership, tier
        counts, mean/max exposure, and the count of critical systems.
    """
    from collections import defaultdict

    scores: dict[str, float] = {}
    tiers: dict[str, list[str]] = defaultdict(list)
    for system in systems:
        score = exposure_score(system)
        scores[system.system_id] = score
        tiers[_tier(score)].append(system.system_id)
    # Deterministic ordering of children within each tier.
    ordered_tiers = {label: tuple(sorted(members)) for label, members in tiers.items()}
    tier_counts = {label: len(members) for label, members in ordered_tiers.items()}
    if scores:
        mean = round(sum(scores.values()) / len(scores), 4)
        max_exp = max(scores.values())
    else:
        mean = 0.0
        max_exp = 0.0
    return FleetAudit(
        scores=scores,
        tiers=ordered_tiers,
        tier_counts=tier_counts,
        mean_exposure=mean,
        max_exposure=max_exp,
        critical_count=tier_counts.get("critical", 0),
        fleet_size=len(scores),
    )


@dataclass(frozen=True)
class RemediationAction:
    """A single prioritized remediation step.

    Args:
        system_id: Which system to patch.
        risk_reduction: Decrease in that system's exposure score from patching
            its highest-priority gap.
        effort: Units of work required (defaults to 1 per action).
    """

    system_id: str
    risk_reduction: float
    effort: float = 1.0


def _worst_reduction(system: LegacySystem) -> float:
    """Best single-source risk reduction for a system (its dominant gap)."""
    s_age = min(system.age_years / 25.0, 1.0)
    s_patch = 1.0 - system.patch_level
    s_proto = min(system.protocol_era / 3.0, 1.0)
    s_surf = min(system.open_services / 6.0, 1.0)
    factors = {
        "patch": 0.35 * s_patch,
        "protocol": 0.20 * s_proto,
        "surface": 0.20 * s_surf,
        "age": 0.25 * s_age,
    }
    return max(factors.values())


def prioritize_remediation(systems: Iterable[LegacySystem], budget: int | None = None) -> tuple[RemediationAction, ...]:
    """Rank systems by greatest risk-reduction-per-effort.

    Each pass picks the system whose dominant risk factor offers the largest
    exposure reduction, patches it (one effort unit), and moves to the next —
    a deterministic greedy descent. ``budget`` caps the number of actions.

    Args:
        systems: The fleet to prioritize.
        budget: Maximum number of remediation actions (``None`` = all systems
            get at least one action).

    Returns:
        An ordered tuple of :class:`RemediationAction`.
    """
    catalog = {system.system_id: system for system in systems}
    actions: list[RemediationAction] = []
    # Start each system at one action; iterate to budget or once per system.
    remaining = dict(catalog)
    count = 0
    while remaining:
        if budget is not None and count >= budget:
            break
        # Deterministic pick: highest reduction, then lexicographic id.
        chosen = max(remaining.values(), key=lambda s: (_worst_reduction(s), -ord(s.system_id[0])))
        reduction = _worst_reduction(chosen)
        actions.append(RemediationAction(system_id=chosen.system_id, risk_reduction=round(reduction, 4)))
        del remaining[chosen.system_id]
        count += 1
    return tuple(actions)


#: A representative legacy fleet used by the flagship audit scenario.
def default_legacy_fleet() -> dict[str, LegacySystem]:
    """Return the canonical legacy fleet for the SILVA audit scenario."""
    return {
        "ldap": LegacySystem(
            "ldap",
            "Legacy Directory LDAP",
            age_years=18,
            patch_level=0.3,
            protocol_era=3,
            open_services=4,
            classification="classified",
        ),
        "exchange": LegacySystem(
            "exchange",
            "Aging Exchange Cluster",
            age_years=14,
            patch_level=0.6,
            protocol_era=2,
            open_services=5,
            classification="operational",
        ),
        "field_ops": LegacySystem(
            "field_ops",
            "Field Ops Workstation Image",
            age_years=9,
            patch_level=0.2,
            protocol_era=1,
            open_services=6,
            classification="classified",
        ),
        "registry_arch": LegacySystem(
            "registry_arch",
            "Black-site Registry Archive",
            age_years=22,
            patch_level=0.1,
            protocol_era=3,
            open_services=2,
            classification="top_secret",
        ),
        "vpn_edge": LegacySystem(
            "vpn_edge",
            "Legacy VPN Edge",
            age_years=11,
            patch_level=0.8,
            protocol_era=1,
            open_services=3,
            classification="operational",
        ),
    }
