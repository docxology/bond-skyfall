"""Tests for skyfall.mission — the BOND-API SILVA MissionProvider.

Real provider implementing the frozen protocol (zero mocks). Exercises the
five-stage lifecycle, protocol membership, gadget registration, and the
deterministic outcome.
"""

from __future__ import annotations

from pathlib import Path

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

ROOT = Path(__file__).resolve().parent.parent


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
        assert len(brief.assets) == 5

    def test_recon(self) -> None:
        report = self.p.recon(ReconRequest(goal="assess"))
        assert isinstance(report, ReconReport)
        assert len(report.findings) >= 7

    def test_plan(self) -> None:
        plan = self.p.plan(self.p.brief())
        assert isinstance(plan, MissionPlan)
        assert [s.name for s in plan.steps] == [
            "intrusion",
            "detection",
            "severance",
            "legacy_audit",
            "patch_schedule",
            "estate_defense",
        ]

    def test_execute_deterministic(self) -> None:
        o1 = self.p.execute(self.p.plan(self.p.brief()))
        o2 = self.p.execute(self.p.plan(self.p.brief()))
        assert isinstance(o1, MissionOutcome)
        assert o1.success is True
        assert o1.results["intrusion"]["shortest_hops"] == 5
        assert o1.results["estate"]["coverage"] == 1.0
        assert o1.results["detection"]["burst_detected"] is True
        assert o1.results["severance"]["max_flow"] == 8.0
        assert o1.results["patch_schedule"]["patched_count"] == 12
        # Deterministic results & provenance.
        assert o1.results == o2.results
        assert o1.provenance == o2.provenance

    def test_execute_new_blocks_present(self) -> None:
        outcome = self.p.execute(self.p.plan(self.p.brief()))
        for key in ("intrusion", "detection", "severance", "legacy", "patch_schedule", "estate"):
            assert key in outcome.results

    def test_provenance(self) -> None:
        outcome = self.p.execute(self.p.plan(self.p.brief()))
        assert outcome.provenance.seed == SILVA_SEED
        assert outcome.provenance.package_version == PACKAGE_VERSION
        assert len(outcome.provenance.input_hash) == 64

    def test_debrief(self) -> None:
        outcome = self.p.execute(self.p.plan(self.p.brief()))
        debrief = self.p.debrief(outcome)
        assert isinstance(debrief, Debrief)
        assert len(debrief.lessons) >= 5
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
        assert set(names) == {
            "intrusion_analyzer",
            "traffic_detector",
            "severance_planner",
            "legacy_auditor",
            "patch_scheduler",
            "estate_planner",
        }

    def test_new_gadgets_return_expected(self) -> None:
        registry = GadgetRegistry()
        register_gadgets(registry)
        traffic = registry.lookup("skyfall", "traffic_detector")()
        assert traffic.burst_detected is True
        severance = registry.lookup("skyfall", "severance_planner")()
        assert severance["max_flow"] == 8.0
        patches = registry.lookup("skyfall", "patch_scheduler")()
        assert patches["patched_count"] == 12

    def test_lookup_missing_raises(self) -> None:
        import pytest

        registry = GadgetRegistry()
        with pytest.raises(KeyError):
            registry.lookup("skyfall", "nope")


class TestDefenders:
    def test_defenders_defined(self) -> None:
        assert DEFENDERS == ("Mallory", "Tanner", "Q", "Eve")


class TestPureCoreIsolation:
    def test_domain_modules_do_not_import_bond_api(self) -> None:
        """Importing the pure core must not pull the BOND protocol in.

        Runs in a fresh subprocess so no earlier test has already loaded
        bond_api into sys.modules.
        """
        import subprocess
        import sys
        import textwrap

        script = textwrap.dedent(
            """
            import sys
            sys.path.insert(0, "src")
            import skyfall.cyber_ops
            import skyfall.traffic_analysis
            import skyfall.exfiltration
            import skyfall.legacy_audit
            import skyfall.patch_strategy
            import skyfall.estate_defense
            print("bond_api" in sys.modules)
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == "False", f"pure core leaked bond_api: {result.stdout}"


class TestDebriefConditionalLessons:
    """The conditional lessons must be reachable, not decorative.

    The canonical scenario is fully covered / detected / well-patched, so on
    the default outcome these three branches never fire. Feeding the debrief a
    real (protocol-valid) degraded outcome proves each lesson is wired to the
    condition it claims to describe.
    """

    @staticmethod
    def _outcome(coverage: float, burst: bool, reduction: float) -> MissionOutcome:
        from bond_api.protocol import Provenance

        return MissionOutcome(
            success=True,
            results={
                "estate": {"coverage": coverage},
                "detection": {"burst_detected": burst},
                "patch_schedule": {"reduction_ratio": reduction},
            },
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SILVA_SEED,
                input_hash="0" * 64,
                wall_time_s=0.0,
            ),
        )

    def test_healthy_outcome_adds_no_warnings(self) -> None:
        debrief = MissionProvider().debrief(self._outcome(1.0, True, 0.9))
        assert len(debrief.lessons) == 5
        assert not any("under-defended" in lesson for lesson in debrief.lessons)

    def test_under_defended_estate_flagged(self) -> None:
        debrief = MissionProvider().debrief(self._outcome(0.5, True, 0.9))
        assert any("under-defended" in lesson for lesson in debrief.lessons)

    def test_missed_burst_flagged(self) -> None:
        debrief = MissionProvider().debrief(self._outcome(1.0, False, 0.9))
        assert any("undetected" in lesson for lesson in debrief.lessons)

    def test_weak_patch_schedule_flagged(self) -> None:
        debrief = MissionProvider().debrief(self._outcome(1.0, True, 0.2))
        assert any("less than half" in lesson for lesson in debrief.lessons)

    def test_all_three_warnings_can_stack(self) -> None:
        debrief = MissionProvider().debrief(self._outcome(0.0, False, 0.0))
        assert len(debrief.lessons) == 8


class TestRemediationBudgetIsShared:
    """The mission and the manuscript must read the same budget constant."""

    def test_outcome_honours_the_declared_budget(self) -> None:
        from skyfall.mission import REMEDIATION_BUDGET

        p = MissionProvider()
        outcome = p.execute(p.plan(p.brief()))
        assert len(outcome.results["legacy"]["remediation_targets"]) == REMEDIATION_BUDGET

    def test_manuscript_token_matches_the_same_constant(self) -> None:
        from skyfall.manuscript_variables import generate_variables
        from skyfall.mission import REMEDIATION_BUDGET

        variables = generate_variables()
        assert variables["SILVA_REMEDIATION_BUDGET"] == str(REMEDIATION_BUDGET)
        assert len(variables["SILVA_REMEDIATION_TARGETS"].split(", ")) == REMEDIATION_BUDGET


class TestUnreachableTargetIsReportedAsFailure:
    """An unmodellable primary objective must not report success.

    `execute` previously hard-coded `success=True`, so a network in which the
    target could not be reached still produced a well-formed outcome carrying
    a stubbed simulation — a consumer had no way to tell the analysis never
    ran. The keyword-only network override makes that path reachable.
    """

    @staticmethod
    def _severed() -> MissionProvider:
        from skyfall.cyber_ops import build_network

        # A real network in which `internet` cannot reach `registry`.
        network = build_network(
            nodes=[],
            edges={"internet": ("demarc",), "demarc": (), "registry": ()},
        )
        return MissionProvider(network=network)

    def test_outcome_reports_failure(self) -> None:
        p = self._severed()
        outcome = p.execute(p.plan(p.brief()))
        assert outcome.success is False

    def test_intrusion_block_is_explicitly_unreachable(self) -> None:
        p = self._severed()
        outcome = p.execute(p.plan(p.brief()))
        intrusion = outcome.results["intrusion"]
        assert intrusion["shortest_path"] == ()
        assert intrusion["shortest_hops"] is None
        assert intrusion["success_probability"] == 0.0
        assert intrusion["simulation"]["verdict"] == "unreachable"

    def test_other_layers_still_computed(self) -> None:
        """The degraded path must not silently drop the remaining analyses."""
        p = self._severed()
        outcome = p.execute(p.plan(p.brief()))
        assert outcome.results["estate"]["coverage"] == 1.0
        assert outcome.results["patch_schedule"]["patched_count"] == 12

    def test_default_provider_still_succeeds(self) -> None:
        """Positive control: the canonical scenario is unaffected."""
        p = MissionProvider()
        assert p.execute(p.plan(p.brief())).success is True

    def test_recon_and_brief_follow_the_bound_network(self) -> None:
        p = self._severed()
        assets = {a.name: a.payload for a in p.brief().assets}
        assert assets["mi6_hq"]["nodes"] == 3
        findings = {f.label: f.detail for f in p.recon(ReconRequest(goal="x")).findings}
        assert findings["intrusion_paths"] == "0 simple paths"
