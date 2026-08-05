"""Network traffic change-point detection for the MI6 HQ exfiltration.

The SILVA mission's detection layer watches the flow of traffic across MI6's
headquarters network. In the 2012 film the adversary does not break in
loudly — the damage is a *burst*: a sudden, concentrated transfer of the NATO
agent list out of the building's systems. This module implements the
classical statistical machinery for catching exactly that signature:

* :func:`periodic_baseline` — because HQ traffic follows a daily rhythm, the
  detector first estimates a per-hour-of-day baseline mean from a clean
  pre-incident window;
* :func:`detrend` — subtracts that periodic baseline, leaving a zero-mean
  residual series (a naive CUSUM on raw periodic traffic false-alarms on the
  rhythm itself — the residualization is the fix);
* :func:`cusum_series` / :func:`cusum_detection` — the cumulative-sum (CUSUM)
  control chart of Page (1954) over the residual series: it accumulates
  standardized deviations and raises an alarm when the accumulated evidence
  crosses a decision threshold ``h``;
* :func:`ewma_series` — the exponentially weighted moving average for a
  smoothed view of the same residuals;
* :func:`change_point_likelihood` — the two-segment normal likelihood split
  that locates the single most likely change point in the series.

The canonical scenario (``DEFAULT_TRAFFIC``) is a deterministic 10-day hourly
packet series: a mild daily rhythm plus a sustained burst across hours
``180..189`` (the agent-list exfiltration window). All functions are pure,
stdlib-only, and byte-deterministic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "TrafficReport",
    "periodic_baseline",
    "detrend",
    "baseline_statistics",
    "cusum_series",
    "cusum_detection",
    "ewma_series",
    "change_point_likelihood",
    "DEFAULT_TRAFFIC",
    "DEFAULT_BASELINE_WINDOW",
    "DEFAULT_PERIOD",
    "DEFAULT_CUSUM_K",
    "DEFAULT_CUSUM_H",
    "EXFIL_WINDOW",
]


@dataclass(frozen=True)
class TrafficReport:
    """Outcome of analyzing a traffic series for an exfiltration burst."""

    baseline_mean: float
    baseline_std: float
    cusum_alarm_index: int | None
    max_cusum: float
    ewma_final: float
    best_change_point: int
    likelihood_improvement: float

    @property
    def burst_detected(self) -> bool:
        """True when the CUSUM chart fired an alarm."""
        return self.cusum_alarm_index is not None


def periodic_baseline(
    series: tuple[float, ...],
    baseline_window: int,
    period: int = 24,
) -> tuple[float, ...]:
    """Return the per-phase baseline means of the first ``baseline_window`` samples.

    Samples are grouped by ``sample_index % period`` (hour of day for the
    default 24-hour period) and each phase's mean is computed over the clean
    baseline window. This captures the daily rhythm without any randomness.

    Raises:
        ValueError: if ``baseline_window`` is not positive, exceeds the series
            length, or ``period`` is not positive.
    """
    if baseline_window <= 0:
        raise ValueError("baseline window must be positive")
    if baseline_window > len(series):
        raise ValueError("baseline window exceeds series length")
    if period <= 0:
        raise ValueError("period must be positive")
    sums = [0.0] * period
    counts = [0] * period
    for idx in range(baseline_window):
        phase = idx % period
        sums[phase] += series[idx]
        counts[phase] += 1
    return tuple((sums[p] / counts[p]) if counts[p] else 0.0 for p in range(period))


def detrend(
    series: tuple[float, ...],
    baseline: tuple[float, ...],
) -> tuple[float, ...]:
    """Subtract the periodic baseline, returning residual traffic.

    Raises:
        ValueError: if the baseline is empty.
    """
    if not baseline:
        raise ValueError("baseline must not be empty")
    return tuple(series[idx] - baseline[idx % len(baseline)] for idx in range(len(series)))


def baseline_statistics(series: tuple[float, ...], window: int) -> tuple[float, float]:
    """Return ``(mean, std)`` of the first ``window`` samples of ``series``.

    Uses the population standard deviation so the result is a pure function of
    the fixed input series.

    Raises:
        ValueError: if ``window`` is not positive or exceeds the series length.
    """
    if window <= 0:
        raise ValueError("baseline window must be positive")
    if window > len(series):
        raise ValueError("baseline window exceeds series length")
    segment = series[:window]
    mean = sum(segment) / window
    variance = sum((x - mean) ** 2 for x in segment) / window
    return mean, math.sqrt(variance)


def cusum_series(
    series: tuple[float, ...],
    mean: float,
    std: float,
    k: float = 0.5,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return the positive and negative CUSUM accumulations.

    ``s_pos[t] = max(0, s_pos[t-1] + (x_t - mean)/std - k)`` and
    ``s_neg[t] = max(0, s_neg[t-1] - (x_t - mean)/std - k)``.

    Args:
        series: The observed (residual) samples.
        mean: Baseline mean.
        std: Baseline standard deviation (must be > 0).
        k: Reference value (allowance) in standardized units.

    Returns:
        A pair of tuples ``(s_pos, s_neg)`` aligned with ``series``.

    Raises:
        ValueError: if ``std <= 0``.
    """
    if std <= 0:
        raise ValueError("standard deviation must be positive")
    s_pos: list[float] = []
    s_neg: list[float] = []
    pos = 0.0
    neg = 0.0
    for x in series:
        z = (x - mean) / std
        pos = max(0.0, pos + z - k)
        neg = max(0.0, neg - z - k)
        s_pos.append(pos)
        s_neg.append(neg)
    return tuple(s_pos), tuple(s_neg)


def cusum_detection(
    series: tuple[float, ...],
    mean: float,
    std: float,
    k: float = 0.5,
    h: float = 5.0,
) -> tuple[int | None, float]:
    """Run the CUSUM chart and return the first alarm index and max CUSUM.

    An alarm fires at the first index where either accumulation exceeds
    ``h`` (the decision interval in standardized units).

    Returns:
        ``(alarm_index, max_cusum)``; ``alarm_index`` is ``None`` when no
        alarm fires within the series.
    """
    s_pos, s_neg = cusum_series(series, mean, std, k)
    max_cusum = 0.0
    for idx in range(len(series)):
        max_cusum = max(max_cusum, s_pos[idx], s_neg[idx])
        if s_pos[idx] > h or s_neg[idx] > h:
            return idx, max_cusum
    return None, max_cusum


def ewma_series(series: tuple[float, ...], alpha: float) -> tuple[float, ...]:
    """Return the exponentially weighted moving average of ``series``.

    ``ewma[0] = x_0`` and ``ewma[t] = alpha * x_t + (1 - alpha) * ewma[t-1]``.

    Raises:
        ValueError: if ``series`` is empty or ``alpha`` is outside ``(0, 1]``.
    """
    if not series:
        raise ValueError("series must not be empty")
    if not 0.0 < alpha <= 1.0:
        raise ValueError("alpha must be in (0, 1]")
    out: list[float] = []
    value = series[0]
    out.append(value)
    for x in series[1:]:
        value = alpha * x + (1.0 - alpha) * value
        out.append(value)
    return tuple(out)


def change_point_likelihood(
    series: tuple[float, ...],
) -> tuple[int, float]:
    """Locate the most likely single change point via two-segment likelihood.

    For every split ``t`` in ``1 .. n-1`` the improvement over the single
    global mean is proportional to the combined squared deviation:

    ``I(t) = n1 * (mu1 - mu_global)^2 + n2 * (mu2 - mu_global)^2``

    with ``mu1``/``mu2`` the segment means. The split maximizing ``I(t)`` is
    the best change point; ties resolve to the earlier index. Computed with
    running sums in O(n).

    Returns:
        ``(best_t, improvement)``.
    """
    n = len(series)
    if n < 2:
        raise ValueError("change-point detection needs at least two samples")
    prefix: list[float] = []
    running = 0.0
    for x in series:
        running += x
        prefix.append(running)
    total = running
    global_mean = total / n

    best_t = 1
    best_improvement = -1.0
    for t in range(1, n):
        n1 = t
        n2 = n - t
        sum1 = prefix[t - 1]
        sum2 = total - sum1
        mu1 = sum1 / n1
        mu2 = sum2 / n2
        improvement = n1 * (mu1 - global_mean) ** 2 + n2 * (mu2 - global_mean) ** 2
        if improvement > best_improvement:
            best_improvement = improvement
            best_t = t
    return best_t, best_improvement


def _build_default_traffic() -> tuple[float, ...]:
    """Construct the deterministic 10-day hourly traffic series.

    Baseline is a 24-hour sinusoidal rhythm around 100 with a slow upward
    drift; hours 180..189 carry the exfiltration burst (+45 packets/hour).
    """
    samples: list[float] = []
    for hour in range(240):
        # Daily rhythm plus a small deterministic quasi-noise wobble (not RNG:
        # a fixed non-harmonic sinusoid, so the residual std is honest but the
        # series stays byte-reproducible).
        value = 100.0 + 8.0 * math.sin(2.0 * math.pi * hour / 24.0) + 0.5 * math.sin(hour * 1.7)
        if 180 <= hour < 190:
            value += 45.0
        samples.append(value)
    return tuple(samples)


#: The deterministic 10-day traffic scenario (240 hourly samples).
DEFAULT_TRAFFIC: tuple[float, ...] = _build_default_traffic()

#: Baseline window: first 7 days (168 hours) are pre-incident traffic.
DEFAULT_BASELINE_WINDOW = 168

#: Daily period (hours) used for the periodic baseline.
DEFAULT_PERIOD = 24

#: CUSUM reference value (allowance) in standardized units.
DEFAULT_CUSUM_K = 0.5

#: CUSUM decision interval in standardized units.
DEFAULT_CUSUM_H = 5.0

#: The exfiltration burst window (inclusive start, exclusive end) used by
#: tests and the manuscript to check the detector's timing.
EXFIL_WINDOW = (180, 190)


def analyze_traffic(
    series: tuple[float, ...] = DEFAULT_TRAFFIC,
    *,
    baseline_window: int = DEFAULT_BASELINE_WINDOW,
    period: int = DEFAULT_PERIOD,
    cusum_k: float = DEFAULT_CUSUM_K,
    cusum_h: float = DEFAULT_CUSUM_H,
) -> TrafficReport:
    """Run the full detection pipeline and return a :class:`TrafficReport`.

    Pipeline: estimate the periodic baseline over the clean window, detrend
    the whole series, compute residual baseline statistics, run the CUSUM
    chart, the EWMA, and the change-point likelihood on the residuals.

    Args:
        series: The traffic series to analyze.
        baseline_window: Number of leading samples used for baseline stats.
        period: Hour-of-day period for the periodic baseline.
        cusum_k: CUSUM reference value.
        cusum_h: CUSUM decision interval.

    Returns:
        A frozen report with residual baseline stats, the alarm index, the max
        CUSUM, the final EWMA, and the best change point.
    """
    periodic = periodic_baseline(series, baseline_window, period)
    residuals = detrend(series, periodic)
    mean, std = baseline_statistics(residuals, baseline_window)
    alarm, max_cusum = cusum_detection(residuals, mean, std, cusum_k, cusum_h)
    ewma = ewma_series(residuals, 0.2)
    best_t, improvement = change_point_likelihood(residuals)
    return TrafficReport(
        baseline_mean=mean,
        baseline_std=std,
        cusum_alarm_index=alarm,
        max_cusum=max_cusum,
        ewma_final=ewma[-1],
        best_change_point=best_t,
        likelihood_improvement=improvement,
    )
