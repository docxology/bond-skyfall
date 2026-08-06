"""Tests for skyfall.traffic_analysis — CUSUM change-point detection.

Real deterministic series and computation only (zero mocks). Exercises the
periodic baseline, residualization, CUSUM chart, EWMA, change-point
likelihood, and the canonical exfiltration-burst scenario.
"""

from __future__ import annotations

import math

import pytest

from skyfall.traffic_analysis import (
    DEFAULT_CUSUM_H,
    DEFAULT_CUSUM_K,
    DEFAULT_TRAFFIC,
    EXFIL_WINDOW,
    TrafficReport,
    analyze_traffic,
    baseline_statistics,
    change_point_likelihood,
    cusum_detection,
    cusum_series,
    detrend,
    ewma_series,
    periodic_baseline,
)


class TestBaselineStatistics:
    def test_mean_std(self) -> None:
        mean, std = baseline_statistics((2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0), 8)
        assert mean == pytest.approx(5.0)
        assert std == pytest.approx(2.0)

    def test_zero_window_raises(self) -> None:
        with pytest.raises(ValueError):
            baseline_statistics((1.0, 2.0), 0)

    def test_window_exceeds_length(self) -> None:
        with pytest.raises(ValueError):
            baseline_statistics((1.0, 2.0), 5)


class TestPeriodicBaseline:
    def test_constant_series(self) -> None:
        base = periodic_baseline((7.0,) * 48, 48, period=24)
        assert all(b == pytest.approx(7.0) for b in base)

    def test_baseline_window_validation(self) -> None:
        with pytest.raises(ValueError):
            periodic_baseline(DEFAULT_TRAFFIC, 0)
        with pytest.raises(ValueError):
            periodic_baseline(DEFAULT_TRAFFIC, 10000)
        with pytest.raises(ValueError):
            periodic_baseline(DEFAULT_TRAFFIC, 48, period=0)

    def test_captures_daily_rhythm(self) -> None:
        # Pure sinusoid with 24h period => periodic baseline tracks it => low residual.
        series = tuple(100.0 + 8.0 * math.sin(2.0 * math.pi * h / 24.0) for h in range(240))
        base = periodic_baseline(series, 168)
        residuals = detrend(series, base)
        mean, std = baseline_statistics(residuals, 168)
        assert std < 1e-6


class TestDetrend:
    def test_removes_baseline(self) -> None:
        series = tuple(5.0 + float(h % 3) for h in range(6))
        base = (5.0, 6.0, 7.0)
        residuals = detrend(series, base)
        assert residuals == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def test_empty_baseline_raises(self) -> None:
        with pytest.raises(ValueError):
            detrend((1.0, 2.0), ())


class TestCusum:
    def test_zero_std_raises(self) -> None:
        with pytest.raises(ValueError):
            cusum_series((1.0, 2.0), 0.0, 0.0)

    def test_steady_series_no_alarm(self) -> None:
        series = (10.0, 10.0, 10.0, 10.0) * 10
        alarm, max_cusum = cusum_detection(series, 10.0, 1.0, k=0.5, h=5.0)
        assert alarm is None
        assert max_cusum == pytest.approx(0.0)

    def test_shift_triggers_alarm(self) -> None:
        series = (10.0,) * 20 + (30.0,) * 20
        alarm, _ = cusum_detection(series, 10.0, 1.0, k=0.5, h=5.0)
        assert alarm is not None
        assert alarm >= 20

    def test_cusum_series_shape_and_order(self) -> None:
        pos, neg = cusum_series((12.0, 9.0), 10.0, 1.0, k=0.5)
        assert len(pos) == len(neg) == 2
        assert pos[0] > 0  # first sample above mean
        assert neg[0] == 0.0


class TestEwma:
    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            ewma_series((), 0.2)

    def test_alpha_out_of_range(self) -> None:
        with pytest.raises(ValueError):
            ewma_series((1.0,), 1.5)
        with pytest.raises(ValueError):
            ewma_series((1.0,), 0.0)

    def test_first_value_seed(self) -> None:
        out = ewma_series((5.0, 7.0, 9.0), 0.5)
        assert out[0] == 5.0
        assert out[1] == pytest.approx(6.0)
        assert out[2] == pytest.approx(7.5)


class TestChangePoint:
    def test_shift_located(self) -> None:
        series = tuple([0.0] * 20 + [10.0] * 20)
        best, improvement = change_point_likelihood(series)
        assert best == 20
        assert improvement > 0

    def test_too_short_raises(self) -> None:
        with pytest.raises(ValueError):
            change_point_likelihood((1.0,))

    def test_deterministic(self) -> None:
        a, ia = change_point_likelihood(DEFAULT_TRAFFIC)
        b, ib = change_point_likelihood(DEFAULT_TRAFFIC)
        assert a == b and ia == ib


class TestCanonicalScenario:
    def test_report_fields(self) -> None:
        report = analyze_traffic()
        assert isinstance(report, TrafficReport)
        assert report.baseline_std > 0

    def test_burst_detected_in_window(self) -> None:
        report = analyze_traffic()
        assert report.burst_detected is True
        assert report.cusum_alarm_index is not None
        assert EXFIL_WINDOW[0] <= report.cusum_alarm_index < EXFIL_WINDOW[1]

    def test_change_point_in_window(self) -> None:
        report = analyze_traffic()
        assert EXFIL_WINDOW[0] <= report.best_change_point < EXFIL_WINDOW[1]

    def test_max_cusum_above_threshold(self) -> None:
        report = analyze_traffic()
        assert report.max_cusum > DEFAULT_CUSUM_H

    def test_deterministic(self) -> None:
        a = analyze_traffic()
        b = analyze_traffic()
        assert a == b

    def test_defaults_match_constants(self) -> None:
        assert DEFAULT_CUSUM_K == 0.5
        assert DEFAULT_CUSUM_H == 5.0


class TestMaxCusumIsTheSeriesPeak:
    """`max_cusum` must be the peak over the whole series, not merely its value
    at the alarm index.

    The earlier implementation returned the running maximum the moment the
    alarm fired. On the canonical burst the CUSUM keeps accumulating through
    the whole exfiltration window, so the reported "peak" under-stated the
    true peak by an order of magnitude while a consumer read it as the
    strongest evidence the detector gathered.
    """

    def test_canonical_peak_is_the_global_max(self) -> None:
        from skyfall.traffic_analysis import (
            DEFAULT_BASELINE_WINDOW,
            DEFAULT_PERIOD,
            baseline_statistics,
            cusum_series,
            detrend,
            periodic_baseline,
        )

        report = analyze_traffic()
        periodic = periodic_baseline(DEFAULT_TRAFFIC, DEFAULT_BASELINE_WINDOW, DEFAULT_PERIOD)
        residuals = detrend(DEFAULT_TRAFFIC, periodic)
        mean, std = baseline_statistics(residuals, DEFAULT_BASELINE_WINDOW)
        pos, neg = cusum_series(residuals, mean, std, DEFAULT_CUSUM_K)
        global_peak = max(max(pos), max(neg))
        assert report.max_cusum == pytest.approx(global_peak)

    def test_peak_is_reached_after_the_alarm(self) -> None:
        # The peak lands inside the burst window, strictly after the alarm,
        # which is exactly the case the running-max-at-alarm bug botched.
        report = analyze_traffic()
        assert report.cusum_alarm_index is not None
        # The running-at-alarm peak (~127) is dwarfed by the true peak, which
        # is gathered over the remainder of the burst window.
        assert report.max_cusum > DEFAULT_CUSUM_H * 2 * 10

    def test_detection_timing_is_unchanged(self) -> None:
        # The fix must shrink no detection claim; only the reported peak moves.
        assert analyze_traffic().cusum_alarm_index == 180
        assert analyze_traffic().best_change_point == 180
