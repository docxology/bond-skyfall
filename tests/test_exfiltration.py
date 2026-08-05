"""Tests for skyfall.exfiltration — Edmonds-Karp max-flow / min-cut severance.

Real capacitated network and computation only (zero mocks). Exercises the
flow algorithm, the min-cut computation, the max-flow/min-cut theorem, and
the canonical severance plan.
"""

from __future__ import annotations

import pytest

from skyfall.exfiltration import (
    DEFAULT_FLOW_NETWORK,
    EXFIL_SINK,
    EXFIL_SOURCE,
    CutResult,
    FlowNetwork,
    FlowResult,
    analyze_exfiltration,
    edmonds_karp,
    min_cut_edges,
    severance_plan,
)


def _chain() -> FlowNetwork:
    return FlowNetwork(
        nodes=("s", "a", "b", "t"),
        edges={"s": ("a", "b"), "a": ("t",), "b": ("t",)},
        capacity={
            ("s", "a"): 3.0,
            ("s", "b"): 2.0,
            ("a", "t"): 3.0,
            ("b", "t"): 2.0,
        },
    )


class TestFlowNetwork:
    def test_empty_nodes_raises(self) -> None:
        with pytest.raises(ValueError):
            FlowNetwork(nodes=(), edges={}, capacity={})

    def test_unknown_source_raises(self) -> None:
        with pytest.raises(ValueError):
            edmonds_karp(DEFAULT_FLOW_NETWORK, "ghost", EXFIL_SINK)

    def test_unknown_sink_raises(self) -> None:
        with pytest.raises(ValueError):
            edmonds_karp(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, "ghost")

    def test_same_source_sink_raises(self) -> None:
        with pytest.raises(ValueError):
            edmonds_karp(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SOURCE)

    def test_nonpositive_capacity_raises(self) -> None:
        with pytest.raises(ValueError):
            FlowNetwork(
                nodes=("a", "b"),
                edges={"a": ("b",)},
                capacity={("a", "b"): 0.0},
            )

    def test_unknown_edge_destination_raises(self) -> None:
        with pytest.raises(ValueError):
            FlowNetwork(nodes=("a",), edges={"a": ("ghost",)}, capacity={})


class TestEdmondsKarp:
    def test_parallel_edges_max_flow(self) -> None:
        result = edmonds_karp(_chain(), "s", "t")
        assert isinstance(result, FlowResult)
        assert result.value == pytest.approx(5.0)

    def test_canonical_max_flow(self) -> None:
        result = edmonds_karp(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SINK)
        assert result.value == pytest.approx(8.0)

    def test_zero_flow_when_disconnected(self) -> None:
        disconnected = FlowNetwork(
            nodes=("s", "t"),
            edges={"s": (), "t": ()},
            capacity={},
        )
        result = edmonds_karp(disconnected, "s", "t")
        assert result.value == pytest.approx(0.0)


class TestMinCut:
    def test_theorem_holds(self) -> None:
        flow = edmonds_karp(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SINK)
        cut = min_cut_edges(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SINK)
        assert isinstance(cut, CutResult)
        assert cut.value == pytest.approx(flow.value)

    def test_canonical_cut_edges(self) -> None:
        cut = min_cut_edges(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SINK)
        assert cut.value == pytest.approx(8.0)
        assert cut.edges == (("dmz_mail", "demarc"), ("intranet_hub", "vpn_gateway"))

    def test_severance_plan_renders(self) -> None:
        cut = min_cut_edges(DEFAULT_FLOW_NETWORK, EXFIL_SOURCE, EXFIL_SINK)
        plan = severance_plan(cut)
        assert len(plan) == 2
        assert plan[0].startswith("sever ")
        assert "dmz_mail" in plan[0]


class TestAnalyze:
    def test_canonical_summary(self) -> None:
        out = analyze_exfiltration()
        assert out["max_flow"] == pytest.approx(8.0)
        assert out["min_cut_value"] == pytest.approx(8.0)
        assert len(out["severance"]) == 2

    def test_deterministic(self) -> None:
        a = analyze_exfiltration()
        b = analyze_exfiltration()
        assert a == b
