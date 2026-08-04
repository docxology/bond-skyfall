"""Tests for skyfall.mission — the BOND-API SILVA MissionProvider.

Real provider implementing the frozen protocol (zero mocks). Exercises the
five-stage lifecycle, protocol membership, gadget registration, and the
deterministic outcome.
"""

from __future__ import annotations

from bond_api.protocol import (
    Debrief,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    ReconReport,
    ReconRequest,
    MissionProvider as ProtocolProvider,
)
from bond_api.registry import GadgetRegistry

from skyfall.mission import (
    DEFENDERS,
    MissionProvider,
    PACKAGE_VERSION,
    SILVA_SEED,
    provider,
    register_gadgets,
)


class TestProviderIdentity:
    def test_film(self) -> None:
        assert MissionProvider().film == "skyfall"

    def test_module_instance(self) -> None:
        assert provider.film == "skyfall"
        assert isinstance(provider, MissionProvider)

    def test_runtime_protocol(self) -> None:
        assert isinstance(provider, ProtocolProvider)


class TestLifecycle:
    def setup_method(self) -> None:
        self.p = MissionProvider()

    def test_brief(self) -> None:
        brief = self.p.brief()
        assert isinstance(brief, MissionBrief)
        assert brief.codename == "SILVA"
        assert "network intrusion" in brief.objectives[0]
        assert len(brief.assets) == 3

    def test_recon(self) -> None:
        report = self.p.recon(ReconRequest(goal="assess"))
        assert isinstance(report, ReconReport)
        assert len(report.findings) >= 5

    def test_plan(self) -> None:
        plan = self.p.plan(self.p.brief())
        assert isinstance(plan, MissionPlan)
        assert [s.name for s in plan.steps] == ["intrusion", "legacy_audit", "estate_defense"]

    def test_execute_deterministic(self) -> None:
        o1 = self.p.execute(self.p.plan(self.p.brief()))
        o2 = self.p.execute(self.p.plan(self.p.brief()))
        assert isinstance(o1, MissionOutcome)
        assert o1.success is True
        assert o1.results["intrusion"]["shortest_hops"] == 5
        assert o1.results["estate"]["coverage"] == 1.0
        # Deterministic results & provenance.
        assert o1.results == o2.results
        assert o1.provenance == o2.provenance

    def test_provenance(self) -> None:
        outcome = self.p.execute(self.p.plan(self.p.brief()))
        assert outcome.provenance.seed == SILVA_SEED
        assert outcome.provenance.package_version == PACKAGE_VERSION
        assert len(outcome.provenance.input_hash) == 64

    def test_debrief(self) -> None:
        outcome = self.p.execute(self.p.plan(self.p.brief()))
        debrief = self.p.debrief(outcome)
        assert isinstance(debrief, Debrief)
        assert len(debrief.lessons) >= 3
        assert debrief.outcome is outcome

    def test_run_mission_flow(self) -> None:
        from bond_api.protocol import run_mission

        debrief = run_mission(self.p, ReconRequest(goal="full flow"))
        assert isinstance(debrief, Debrief)
        assert debrief.outcome.success is True


class TestGadgets:
    def test_register_and_lookup(self) -> None:
        registry = GadgetRegistry()
        register_gadgets(registry)
        assert registry.contains("skyfall", "intrusion_analyzer")
        analyzer = registry.lookup("skyfall", "intrusion_analyzer")
        result = analyzer()
        assert result is not None
        assert result.hosts[-1] == "registry"

    def test_gadget_names(self) -> None:
        registry = GadgetRegistry()
        register_gadgets(registry)
        names = registry.gadgets_for("skyfall")
        assert set(names) == {"intrusion_analyzer", "legacy_auditor", "estate_planner"}

    def test_lookup_missing_raises(self) -> None:
        import pytest

        registry = GadgetRegistry()
        with pytest.raises(KeyError):
            registry.lookup("skyfall", "nope")


class TestDefenders:
    def test_defenders_defined(self) -> None:
        assert DEFENDERS == ("Mallory", "Tanner", "Q", "Eve")
