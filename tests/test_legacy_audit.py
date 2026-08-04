"""Tests for skyfall.legacy_audit — aging-infrastructure exposure audit.

Real systems and closed-form computation only (zero mocks). Exercises the
per-system exposure score, fleet aggregation, risk-tiering, and prioritized
remediation ordering.
"""

from __future__ import annotations

import pytest

from skyfall.legacy_audit import (
    EXPOSURE_THRESHOLDS,
    FleetAudit,
    LegacySystem,
    audit_fleet,
    default_legacy_fleet,
    exposure_score,
    prioritize_remediation,
)


class TestLegacySystem:
    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            LegacySystem("", "name")
        with pytest.raises(ValueError):
            LegacySystem("id", "")
        with pytest.raises(ValueError):
            LegacySystem("id", "n", age_years=-1)
        with pytest.raises(ValueError):
            LegacySystem("id", "n", patch_level=1.5)
        with pytest.raises(ValueError):
            LegacySystem("id", "n", protocol_era=-1)
        with pytest.raises(ValueError):
            LegacySystem("id", "n", open_services=-2)


class TestExposureScore:
    def test_well_patched_is_low(self) -> None:
        s = LegacySystem("id", "n", age_years=3, patch_level=0.95, protocol_era=0, open_services=1)
        assert exposure_score(s) < 0.3

    def test_ancient_unpatched_is_critical(self) -> None:
        s = LegacySystem("id", "n", age_years=22, patch_level=0.05, protocol_era=3, open_services=6)
        assert exposure_score(s) > 0.8

    def test_monotonic_in_unpatched(self) -> None:
        low = exposure_score(LegacySystem("a", "n", patch_level=0.9))
        high = exposure_score(LegacySystem("b", "n", patch_level=0.1))
        assert high > low

    def test_bounded_and_deterministic(self) -> None:
        s = LegacySystem("id", "n")
        a = exposure_score(s)
        b = exposure_score(s)
        assert a == b
        assert 0.0 <= a <= 1.0


class TestAuditFleet:
    def test_default_fleet(self) -> None:
        fleet = audit_fleet(default_legacy_fleet().values())
        assert fleet.fleet_size == 5
        assert fleet.critical_count >= 1
        assert fleet.risk() == "critical"
        assert fleet.tier_counts["critical"] == fleet.critical_count

    def test_empty_fleet(self) -> None:
        fleet = audit_fleet([])
        assert fleet.fleet_size == 0
        assert fleet.mean_exposure == 0.0
        assert fleet.max_exposure == 0.0
        assert fleet.risk() == "low"

    def test_tier_membership(self) -> None:
        fleet = audit_fleet([LegacySystem("a", "n", age_years=1, patch_level=0.99, protocol_era=0, open_services=0)])
        assert fleet.tiers["low"] == ("a",)
        assert fleet.mean_exposure < 0.3


class TestRemediation:
    def test_budget_caps_actions(self) -> None:
        actions = prioritize_remediation(default_legacy_fleet().values(), budget=3)
        assert len(actions) == 3

    def test_priority_order(self) -> None:
        actions = prioritize_remediation(default_legacy_fleet().values())
        # First action targets the highest-exposure system.
        assert actions[0].system_id == "registry_arch"
        assert actions[0].risk_reduction > 0

    def test_unlimited_exhausts_fleet(self) -> None:
        actions = prioritize_remediation(default_legacy_fleet().values())
        assert len(actions) == len(default_legacy_fleet())

    def test_effort_default_one(self) -> None:
        (action,) = prioritize_remediation([LegacySystem("a", "n", patch_level=0.5)], budget=1)
        assert action.effort == 1.0


class TestThresholds:
    def test_thresholds_ordered_ascending(self) -> None:
        scores = [t for t, _ in EXPOSURE_THRESHOLDS[:-1]]
        assert scores == sorted(scores)

    def test_fleet_audit_dataclass(self) -> None:
        a = FleetAudit(
            scores={}, tiers={}, tier_counts={}, mean_exposure=0.0, max_exposure=0.0, critical_count=0, fleet_size=0
        )
        assert a.risk() == "low"
