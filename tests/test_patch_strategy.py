"""Tests for skyfall.patch_strategy — greedy patch scheduling.

Real vulnerabilities and computation only (zero mocks). Exercises the
cumulative-exposure model, the greedy scheduler, and the reduction summary
against the canonical backlog.
"""

from __future__ import annotations

import pytest

from skyfall.patch_strategy import (
    DEFAULT_DAILY_BUDGET,
    DEFAULT_HORIZON_DAYS,
    DEFAULT_VULNERABILITIES,
    PatchSummary,
    ScheduleEntry,
    Vulnerability,
    analyze_patch_schedule,
    exposure_with_schedule,
    fleet_exposure,
    reduction,
    schedule_patches,
)


class TestVulnerability:
    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            Vulnerability("", "sys", 5.0, 0)
        with pytest.raises(ValueError):
            Vulnerability("v", "", 5.0, 0)
        with pytest.raises(ValueError):
            Vulnerability("v", "sys", 11.0, 0)
        with pytest.raises(ValueError):
            Vulnerability("v", "sys", -1.0, 0)
        with pytest.raises(ValueError):
            Vulnerability("v", "sys", 5.0, -1)
        with pytest.raises(ValueError):
            Vulnerability("v", "sys", 5.0, 0, patch_effort=0.0)


class TestFleetExposure:
    def test_accumulates_severity_days(self) -> None:
        vulns = (Vulnerability("a", "s", 5.0, 2), Vulnerability("b", "s", 3.0, 5))
        assert fleet_exposure(vulns, 10) == 5.0 * 8 + 3.0 * 5
        assert fleet_exposure(vulns, 10) == pytest.approx(55.0)

    def test_discovered_after_horizon_ignored(self) -> None:
        vulns = (Vulnerability("a", "s", 5.0, 20),)
        assert fleet_exposure(vulns, 10) == 0.0


class TestSchedulePatches:
    def test_budget_zero_raises(self) -> None:
        with pytest.raises(ValueError):
            schedule_patches(DEFAULT_VULNERABILITIES, 10, 0.0)

    def test_negative_horizon_raises(self) -> None:
        with pytest.raises(ValueError):
            schedule_patches(DEFAULT_VULNERABILITIES, -1, 1.0)

    def test_only_patches_after_discovery(self) -> None:
        entries = schedule_patches(DEFAULT_VULNERABILITIES, 30, 1.0)
        by_id = {v.vuln_id: v for v in DEFAULT_VULNERABILITIES}
        for entry in entries:
            assert entry.day >= by_id[entry.vuln_id].discovered_day

    def test_canonical_schedule_count(self) -> None:
        entries = schedule_patches(DEFAULT_VULNERABILITIES, DEFAULT_HORIZON_DAYS, DEFAULT_DAILY_BUDGET)
        assert len(entries) == 12
        assert isinstance(entries[0], ScheduleEntry)

    def test_highest_severity_first(self) -> None:
        entries = schedule_patches(DEFAULT_VULNERABILITIES, DEFAULT_HORIZON_DAYS, 1.0)
        assert entries[0].vuln_id == "VULN-001"  # severity 9.8, discovered day 1


class TestExposureWithSchedule:
    def test_patched_after_discovery_counts_subinterval(self) -> None:
        vulns = (Vulnerability("a", "s", 5.0, 2),)
        entries = (ScheduleEntry(day=4, vuln_id="a", system_id="s"),)
        # Contributes days 2,3 (2 days) x severity 5 = 10.
        assert exposure_with_schedule(vulns, entries, 10) == pytest.approx(10.0)

    def test_unpatched_runs_full_horizon(self) -> None:
        vulns = (Vulnerability("a", "s", 5.0, 2),)
        assert exposure_with_schedule(vulns, (), 10) == pytest.approx(40.0)


class TestReduction:
    def test_canonical_reduction(self) -> None:
        entries = schedule_patches(DEFAULT_VULNERABILITIES, DEFAULT_HORIZON_DAYS, DEFAULT_DAILY_BUDGET)
        summary = reduction(DEFAULT_VULNERABILITIES, entries, DEFAULT_HORIZON_DAYS)
        assert isinstance(summary, PatchSummary)
        assert summary.patched_count == 12
        assert summary.baseline_exposure > summary.scheduled_exposure
        assert 0.0 < summary.reduction_ratio < 1.0

    def test_no_patching_ratio_zero(self) -> None:
        summary = reduction(DEFAULT_VULNERABILITIES, (), DEFAULT_HORIZON_DAYS)
        assert summary.reduction_ratio == 0.0

    def test_analyze_summary(self) -> None:
        out = analyze_patch_schedule()
        assert out["patched_count"] == 12
        assert out["reduction_ratio"] == pytest.approx(0.889, abs=1e-3)
        assert out["baseline_exposure"] > out["scheduled_exposure"]

    def test_deterministic(self) -> None:
        a = analyze_patch_schedule()
        b = analyze_patch_schedule()
        assert a == b
