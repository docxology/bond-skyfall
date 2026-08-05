"""Tests for skyfall.figures — deterministic matplotlib rendering.

Renders the flagship estate-defense figure through real matplotlib (Agg) and
asserts the PNG artifact exists and is byte-identical across runs.
"""

from __future__ import annotations

from pathlib import Path

from skyfall.estate_defense import DEFAULT_ESTATE, DefensePlan
from skyfall.figures import (
    DEFAULT_FIGURE_OUTPUT,
    DEFAULT_TRAFFIC_FIGURE_OUTPUT,
    defense_coverage_fraction,
    render_estate_defense_figure,
    render_traffic_figure,
)


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
