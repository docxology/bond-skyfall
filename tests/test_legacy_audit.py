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
    RemediationAction,
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


class TestRiskFactors:
    """The factor model is the single definition the score and ranker share."""

    def test_factors_are_normalized(self) -> None:
        from skyfall.legacy_audit import risk_factors

        system = LegacySystem("x", "X", age_years=100, patch_level=0.0, protocol_era=99, open_services=99)
        factors = risk_factors(system)
        assert set(factors) == {"age", "patch", "protocol", "surface"}
        assert all(0.0 <= value <= 1.0 for value in factors.values())
        # Fully saturated on every axis.
        assert factors == {"age": 1.0, "patch": 1.0, "protocol": 1.0, "surface": 1.0}

    def test_score_is_the_weighted_sum_of_the_factors(self) -> None:
        from skyfall.legacy_audit import EXPOSURE_WEIGHTS, risk_factors

        system = LegacySystem("y", "Y", age_years=12, patch_level=0.4, protocol_era=2, open_services=3)
        factors = risk_factors(system)
        expected = round(sum(EXPOSURE_WEIGHTS[k] * v for k, v in factors.items()), 4)
        assert exposure_score(system) == expected

    def test_weights_sum_to_one(self) -> None:
        from skyfall.legacy_audit import EXPOSURE_WEIGHTS

        assert abs(sum(EXPOSURE_WEIGHTS.values()) - 1.0) < 1e-12


class TestFleetRiskLabels:
    """`FleetAudit.risk()` has four outcomes; exercise each, not just the default."""

    @staticmethod
    def _audit(mean: float, critical: int) -> FleetAudit:
        return FleetAudit(
            scores={"a": mean},
            tiers={},
            tier_counts={},
            mean_exposure=mean,
            max_exposure=mean,
            critical_count=critical,
            fleet_size=1,
        )

    def test_critical_dominates(self) -> None:
        assert self._audit(0.1, 1).risk() == "critical"

    def test_high_band(self) -> None:
        assert self._audit(0.6, 0).risk() == "high"
        assert self._audit(0.95, 0).risk() == "high"

    def test_medium_band(self) -> None:
        assert self._audit(0.4, 0).risk() == "medium"
        assert self._audit(0.59, 0).risk() == "medium"

    def test_low_band(self) -> None:
        assert self._audit(0.39, 0).risk() == "low"


class TestRemediationTieBreak:
    """Ties must break on the whole id, not just its first character.

    The ranker previously keyed on ``-ord(system_id[0])``, so systems sharing
    a first letter compared equal and the winner fell out of dict insertion
    order. These two systems are identical apart from their ids.
    """

    @staticmethod
    def _twins(order: tuple[str, str]) -> tuple[RemediationAction, ...]:
        systems = [
            LegacySystem(sid, sid.upper(), age_years=10, patch_level=0.5, protocol_era=1, open_services=3)
            for sid in order
        ]
        return prioritize_remediation(systems, budget=1)

    def test_lexicographically_smallest_id_wins(self) -> None:
        assert self._twins(("ldap_alpha", "ldap_beta"))[0].system_id == "ldap_alpha"

    def test_result_is_insertion_order_independent(self) -> None:
        assert self._twins(("ldap_alpha", "ldap_beta")) == self._twins(("ldap_beta", "ldap_alpha"))
