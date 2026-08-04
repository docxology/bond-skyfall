"""The SILVA mission adapter: a BOND-API :class:`MissionProvider`.

This module is the seam between the pure domain core (:mod:`skyfall.cyber_ops`,
:mod:`skyfall.legacy_audit`, :mod:`skyfall.estate_defense`) and the frozen
BOND-API protocol. It implements the five-stage lifecycle — brief, recon,
plan, execute, debrief — against the real, deterministic domain modules and
registers the film's gadgets with :class:`bond_api.registry.GadgetRegistry`.

Convention (see ``bond_api.discovery``): this module is importable as
``skyfall.mission`` and exposes a ``MissionProvider`` class at module top
level under the stable name ``MissionProvider``.
"""

from __future__ import annotations

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from .cyber_ops import (
    DEFAULT_ENTRY,
    DEFAULT_NETWORK,
    DEFAULT_TARGET,
    cheapest_intrusion_path,
    intrusion_paths,
    path_success_probability,
    shortest_intrusion_path,
    simulate_intrusion,
)
from .estate_defense import (
    DEFAULT_ESTATE,
    choke_points,
    defense_coverage,
    default_island,
    estate_defense_plan,
    island_topology,
)
from .legacy_audit import (
    audit_fleet,
    default_legacy_fleet,
    prioritize_remediation,
)

__all__ = ["MissionProvider", "register_gadgets", "SILVA_SEED", "PACKAGE_VERSION"]

#: Deterministic seed for provenance (no randomness is actually drawn).
SILVA_SEED = 11

#: Package version recorded in provenance and the brief's asset manifest.
PACKAGE_VERSION = "0.1.0"

#: Defender call signs for the estate defense plan.
DEFENDERS = ("Mallory", "Tanner", "Q", "Eve")


def _input_hash() -> str:
    """Deterministic fingerprint of the SILVA scenario's fixed inputs."""
    from hashlib import sha256

    payload = (
        "|".join(sorted(DEFAULT_NETWORK.nodes))
        + "|"
        + DEFAULT_ENTRY
        + "|"
        + DEFAULT_TARGET
        + "|"
        + ",".join(sorted(DEFAULT_ESTATE.positions))
    )
    return sha256(payload.encode("utf-8")).hexdigest()


class MissionProvider:  # noqa: N801 — class name fixed by the discovery contract
    """BOND-API mission provider for the skyfall (SILVA) film.

    Every stage is deterministic and backed by the pure domain modules; the
    concurrence of the cyber intrusion, the legacy audit, and the estate
    defense together model the SILVA threat the way the 2012 film depicts a
    single coordinated assault on MI6 and its people.
    """

    film = "skyfall"

    def brief(self) -> MissionBrief:
        """Declare the SILVA mission: three linked defensive/threat objectives."""
        return MissionBrief(
            film=self.film,
            codename="SILVA",
            objectives=(
                "model the network intrusion paths into MI6's headquarters",
                "audit the aging legacy system exposure",
                "plan the Skyfall estate defense from its choke points",
            ),
            assets=(
                Asset(kind="network", name="mi6_hq", payload={"nodes": len(DEFAULT_NETWORK.nodes)}),
                Asset(kind="fleet", name="legacy_systems", payload={"size": len(default_legacy_fleet())}),
                Asset(kind="graph", name="estate", payload={"positions": len(DEFAULT_ESTATE.positions)}),
            ),
            constraints=(
                Constraint(kind="determinism", detail="fixed seed, no random draws, no external calls"),
                Constraint(kind="purity", detail="domain modules must not import bond-api"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the three threat surfaces and the mission constraints."""
        return ReconReport(
            findings=(
                Finding(label="entry", detail=DEFAULT_ENTRY),
                Finding(label="target", detail=DEFAULT_TARGET),
                Finding(
                    label="intrusion_paths",
                    detail=f"{len(intrusion_paths(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET))} simple paths",
                ),
                Finding(label="fleet", detail=f"{len(default_legacy_fleet())} legacy systems to audit"),
                Finding(label="estate", detail=f"{len(choke_points(DEFAULT_ESTATE))} estate choke points"),
                Finding(label="goal", detail=request.goal),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the three deterministic steps: intrusion, audit, defense."""
        return MissionPlan(
            steps=(
                Step(
                    name="intrusion",
                    action="simulate_intrusion",
                    params={"entry": DEFAULT_ENTRY, "target": DEFAULT_TARGET},
                ),
                Step(name="legacy_audit", action="audit_fleet", params={"size": len(default_legacy_fleet())}),
                Step(name="estate_defense", action="estate_defense_plan", params={"defenders": len(DEFENDERS)}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan against the real domain modules, deterministically."""
        # Cyber: shortest + cheapest intrusion path against the HQ network.
        shortest = shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        cheapest = cheapest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        shortcut = shortest.hosts if shortest else ()
        cheap = cheapest.hosts if cheapest else ()
        if shortest is not None:
            success = path_success_probability(DEFAULT_NETWORK, shortest)
            sim = simulate_intrusion(DEFAULT_NETWORK, shortest)
        else:
            success = 0.0
            sim = {"path": (), "contained": True, "verdict": "unreachable", "hops": 0}

        # Legacy: full fleet audit and a prioritized remediation budget.
        fleet = audit_fleet(default_legacy_fleet().values())
        remediation = prioritize_remediation(default_legacy_fleet().values(), budget=3)

        # Estate: choke-point analysis and defense plan.
        island = island_topology(default_island())
        points = choke_points(DEFAULT_ESTATE)
        plan_out = estate_defense_plan(DEFAULT_ESTATE, DEFENDERS)
        coverage = defense_coverage(plan_out)

        results: dict[str, object] = {
            "intrusion": {
                "shortest_path": shortcut,
                "shortest_hops": len(shortcut) - 1 if shortcut else None,
                "cheapest_path": cheap,
                "success_probability": round(success, 4),
                "simulation": sim,
            },
            "legacy": {
                "fleet_size": fleet.fleet_size,
                "mean_exposure": fleet.mean_exposure,
                "critical_count": fleet.critical_count,
                "tier_counts": fleet.tier_counts,
                "risk": fleet.risk(),
                "remediation_targets": [a.system_id for a in remediation],
            },
            "estate": {
                "island_corridor": island.corridor_length,
                "island_hideout": island.hideout,
                "choke_points": points,
                "defenders_used": plan_out.defenders_used,
                "covered": plan_out.covered,
                "uncovered": plan_out.uncovered,
                "coverage": round(coverage, 4),
            },
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SILVA_SEED,
                input_hash=_input_hash(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record the standing SILVA lessons."""
        estate = outcome.results.get("estate", {})
        coverage = estate.get("coverage", 0.0)
        lessons = [
            "aging infrastructure multiplies network-intrusion exposure — patching is the highest-leverage control",
            "choke-point defense only works if every articulation point is covered",
            "deterministic provenance is mandatory for audit trust",
        ]
        if coverage < 1.0:
            lessons.append("estate is under-defended: some choke points remain uncovered")
        return Debrief(outcome=outcome, lessons=tuple(lessons))


def register_gadgets(registry: GadgetRegistry) -> None:
    """Register the SILVA film's gadgets with a BOND :class:`GadgetRegistry`.

    Gadgets are deterministic payloads (callables) the orchestrator may look
    up; registering under this film's slug makes them discoverable alongside
    the mission provider.

    Args:
        registry: A BOND gadget registry to mutate.
    """
    registry.register(
        "skyfall",
        {
            "intrusion_analyzer": lambda: shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET),
            "legacy_auditor": lambda: audit_fleet(default_legacy_fleet().values()),
            "estate_planner": lambda: estate_defense_plan(DEFAULT_ESTATE, DEFENDERS),
        },
    )


#: The film instance the suite discovers (stable top-level name).
provider = MissionProvider()
