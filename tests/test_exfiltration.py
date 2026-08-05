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


class TestMinCutTheoremSweep:
    """Enumerated positive control for the max-flow min-cut theorem.

    `min_cut_edges` previously walked only the *forward* network edges when
    computing residual reachability. That under-approximates the source side
    of the cut whenever flow enters it on an edge from an unreached node, and
    the reported cut value then exceeds the max flow. The sweep below is the
    guard: it enumerates a family of five-node networks — including ones whose
    max flow strictly requires the reverse residual arcs — and pins the
    theorem on every one of them.
    """

    @staticmethod
    def _network(capacity: dict[tuple[str, str], float]) -> FlowNetwork:
        names = ("s", "a", "b", "c", "t")
        edges: dict[str, tuple[str, ...]] = {}
        for name in names:
            edges[name] = tuple(sorted(dst for (src, dst) in capacity if src == name))
        return FlowNetwork(nodes=names, edges=edges, capacity=dict(capacity))

    def test_regression_diamond_with_backflow(self) -> None:
        """The exact network that broke the old forward-only reachability.

        s->a and s->b feed a shared bottleneck c->t. Saturating c->t leaves
        `a` reachable only through the reverse arc induced by the flow on
        a->c; the forward-only walk reported a cut of 6.0 against a max flow
        of 3.0.
        """
        capacity = {
            ("s", "a"): 3.0,
            ("s", "b"): 2.0,
            ("a", "c"): 3.0,
            ("b", "c"): 3.0,
            ("c", "t"): 3.0,
        }
        network = self._network(capacity)
        flow = edmonds_karp(network, "s", "t")
        cut = min_cut_edges(network, "s", "t")
        assert flow.value == pytest.approx(3.0)
        assert cut.value == pytest.approx(3.0)
        assert cut.edges == (("c", "t"),)

    def test_theorem_holds_across_enumerated_family(self) -> None:
        """Every network in the deterministic family satisfies value(cut) == value(flow)."""
        candidate_edges = (
            ("s", "a"),
            ("s", "b"),
            ("s", "c"),
            ("a", "b"),
            ("a", "c"),
            ("a", "t"),
            ("b", "a"),
            ("b", "c"),
            ("b", "t"),
            ("c", "a"),
            ("c", "t"),
        )
        # Deterministic capacity assignment: a fixed repeating 1/2/3 cycle
        # indexed by edge position, and a fixed bitmask sweep over subsets.
        checked = 0
        for mask in range(1, 1 << len(candidate_edges)):
            if bin(mask).count("1") != 5:
                continue
            capacity = {edge: float((idx % 3) + 1) for idx, edge in enumerate(candidate_edges) if mask & (1 << idx)}
            network = self._network(capacity)
            flow = edmonds_karp(network, "s", "t")
            cut = min_cut_edges(network, "s", "t")
            assert cut.value == pytest.approx(flow.value), f"theorem violated on {capacity}"
            checked += 1
        # A vacuous sweep would pass trivially; pin the population size.
        assert checked == 462

    def test_family_contains_nonzero_flows(self) -> None:
        """Positive control: the sweep is not dominated by zero-flow networks."""
        capacity = {("s", "a"): 2.0, ("a", "t"): 3.0}
        network = self._network(capacity)
        assert edmonds_karp(network, "s", "t").value == pytest.approx(2.0)


class TestFlowNetworkValidation:
    def test_unknown_edge_source_raises(self) -> None:
        with pytest.raises(ValueError, match="edge source"):
            FlowNetwork(nodes=("a", "b"), edges={"ghost": ("b",)}, capacity={})

    def test_cap_of_absent_edge_is_zero(self) -> None:
        assert DEFAULT_FLOW_NETWORK.cap("registry", "internet") == 0.0

    def test_out_neighbours_of_unknown_node(self) -> None:
        assert DEFAULT_FLOW_NETWORK.out_neighbours("ghost") == ()
