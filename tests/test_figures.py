"""Tests for skyfall.figures — deterministic matplotlib rendering.

Renders the flagship estate-defense figure through real matplotlib (Agg) and
asserts the PNG artifact exists and is byte-identical across runs.
"""

from __future__ import annotations

import math
from pathlib import Path

from skyfall.estate_defense import DEFAULT_ESTATE, DefensePlan
from skyfall.figures import (
    DEFAULT_FIGURE_OUTPUT,
    DEFAULT_TRAFFIC_FIGURE_OUTPUT,
    defense_coverage_fraction,
    render_estate_defense_figure,
    render_traffic_figure,
)
from skyfall.traffic_analysis import analyze_traffic


class TestFigure:
    def test_render_creates_png(self, tmp_path: Path) -> None:
        out = tmp_path / "estate_defense.png"
        path = render_estate_defense_figure(output_path=out)
        assert out.is_file()
        assert path == out
        assert out.stat().st_size > 0

    def test_render_deterministic(self, tmp_path: Path) -> None:
        a = tmp_path / "a.png"
        b = tmp_path / "b.png"
        render_estate_defense_figure(output_path=a)
        render_estate_defense_figure(output_path=b)
        assert a.read_bytes() == b.read_bytes()

    def test_render_with_custom_defenders(self, tmp_path: Path) -> None:
        out = tmp_path / "custom.png"
        render_estate_defense_figure(graph=DEFAULT_ESTATE, defenders=("Q",), output_path=out)
        assert out.is_file()

    def test_default_output_path(self) -> None:
        assert DEFAULT_FIGURE_OUTPUT.name == "estate_defense.png"
        assert "output" in str(DEFAULT_FIGURE_OUTPUT)


class TestTrafficFigure:
    def test_render_creates_png(self, tmp_path: Path) -> None:
        out = tmp_path / "traffic_detection.png"
        path = render_traffic_figure(output_path=out)
        assert out.is_file()
        assert path == out
        assert out.stat().st_size > 0

    def test_render_deterministic(self, tmp_path: Path) -> None:
        a = tmp_path / "ta.png"
        b = tmp_path / "tb.png"
        render_traffic_figure(output_path=a)
        render_traffic_figure(output_path=b)
        assert a.read_bytes() == b.read_bytes()

    def test_default_output_path(self) -> None:
        assert DEFAULT_TRAFFIC_FIGURE_OUTPUT.name == "traffic_detection.png"

    def test_render_without_alarm_omits_alarm_line(self, tmp_path: Path) -> None:
        """A burst-free series raises no CUSUM alarm, so no alarm line is drawn.

        This exercises the ``report.cusum_alarm_index is None`` arm of the
        renderer, which the canonical (burst-carrying) series can never reach.
        The series is the documented baseline rhythm with the +45 packets/hour
        exfiltration burst removed — real samples, real detector, real render.
        """
        calm = tuple(
            100.0 + 8.0 * math.sin(2.0 * math.pi * hour / 24.0) + 0.5 * math.sin(hour * 1.7) for hour in range(240)
        )
        report = analyze_traffic(calm)
        assert report.cusum_alarm_index is None
        assert report.burst_detected is False

        out = tmp_path / "calm.png"
        assert render_traffic_figure(series=calm, output_path=out) == out
        assert out.stat().st_size > 0

        alarmed = tmp_path / "alarmed.png"
        render_traffic_figure(output_path=alarmed)
        assert out.read_bytes() != alarmed.read_bytes()


class TestCoverageFraction:
    def test_full_coverage(self) -> None:
        from skyfall.estate_defense import estate_defense_plan

        plan = estate_defense_plan(DEFAULT_ESTATE, ("Q", "Mallory", "Tanner", "Eve"))
        assert defense_coverage_fraction(plan) == 1.0

    def test_type_error_on_wrong_type(self) -> None:
        try:
            defense_coverage_fraction(object())
        except TypeError:
            return
        raise AssertionError("expected TypeError for non-DefensePlan")

    def test_defense_plan_empty(self) -> None:
        plan = DefensePlan(assigned={}, covered=(), uncovered=(), defenders_used=0)
        assert defense_coverage_fraction(plan) == 0.0


class TestHashSeedByteIdentity:
    """Figure bytes must not depend on hash-randomised iteration order.

    Renders each figure in two subprocesses with different PYTHONHASHSEED
    values and compares bytes — the cross-process form of the in-process
    determinism assertions, which is what AGENTS.md claims.
    """

    @staticmethod
    def _render(seed: str, tmp_path: Path, fn: str, out: Path) -> None:
        import os
        import subprocess
        import sys

        src_abs = Path(__file__).resolve().parent.parent / "src"
        code = (
            "import sys; sys.path.insert(0, " + repr(str(src_abs)) + "); "
            f"from skyfall.figures import {fn}; "
            f"{fn}(output_path=__import__('pathlib').Path(" + repr(str(out)) + "))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmp_path,
            env={**os.environ, "PYTHONHASHSEED": seed, "MPLBACKEND": "Agg"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

    def test_estate_figure_cross_hashseed(self, tmp_path: Path) -> None:
        a = tmp_path / "a.png"
        b = tmp_path / "b.png"
        self._render("1", tmp_path, "render_estate_defense_figure", a)
        self._render("2", tmp_path, "render_estate_defense_figure", b)
        assert a.read_bytes() == b.read_bytes()

    def test_traffic_figure_cross_hashseed(self, tmp_path: Path) -> None:
        a = tmp_path / "ta.png"
        b = tmp_path / "tb.png"
        self._render("1", tmp_path, "render_traffic_figure", a)
        self._render("2", tmp_path, "render_traffic_figure", b)
        assert a.read_bytes() == b.read_bytes()
