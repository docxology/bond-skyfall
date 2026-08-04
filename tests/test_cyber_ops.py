"""Tests for skyfall.cyber_ops — network intrusion path analysis.

Real graph data and computation only (zero mocks). Exercises path
enumeration, BFS shortest path, Dijkstra cheapest path, success-probability,
and the step simulation against the canonical MI6 HQ network.
"""

from __future__ import annotations

import pytest

from skyfall.cyber_ops import (
    DEFAULT_ENTRY,
    DEFAULT_NETWORK,
    DEFAULT_TARGET,
    IntrusionPath,
    Node,
    build_network,
    cheapest_intrusion_path,
    intrusion_paths,
    path_success_probability,
    shortest_intrusion_path,
    simulate_intrusion,
)


class TestNetwork:
    def test_build_and_validate(self) -> None:
        net = build_network(
            [Node("a", "host"), Node("b", "host")],
            edges={"a": ["b"]},
        )
        assert net.neighbours("a") == ("b",)
        assert net.hop_cost("a", "b") == 1.0

    def test_node_key_mismatch(self) -> None:
        from skyfall.cyber_ops import Network as Net

        with pytest.raises(ValueError):
            Net(nodes={"mismatch": Node("x", "host")}, edges={})

    def test_implicit_node_creation(self) -> None:
        net = build_network([], edges={"a": ["b", "c"]}, default_exposure=0.3)
        assert set(net.nodes) == {"a", "b", "c"}
        assert net.nodes["b"].exposure == 0.3

    def test_node_validation(self) -> None:
        with pytest.raises(ValueError):
            Node("", "host")
        with pytest.raises(ValueError):
            Node("a", "")
        with pytest.raises(ValueError):
            Node("a", "h", exposure=1.5)
        with pytest.raises(ValueError):
            Node("a", "h", exposure=-0.1)

    def test_edge_destination_unknown(self) -> None:
        from skyfall.cyber_ops import Network as Net

        with pytest.raises(ValueError):
            Net(nodes={"a": Node("a", "h")}, edges={"a": ("ghost",)})

    def test_nonpositive_edge_cost(self) -> None:
        with pytest.raises(ValueError):
            build_network([Node("a", "h"), Node("b", "h")], edges={"a": ["b"]}, edge_cost={("a", "b"): 0})

    def test_empty_neighbours(self) -> None:
        assert DEFAULT_NETWORK.neighbours("unknown") == ()


class TestIntrusionPaths:
    def test_enumeration_len(self) -> None:
        paths = intrusion_paths(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert len(paths) == 6
        assert all(p.hosts[0] == "internet" and p.hosts[-1] == "registry" for p in paths)

    def test_determinism(self) -> None:
        a = intrusion_paths(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        b = intrusion_paths(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert [p.hosts for p in a] == [p.hosts for p in b]

    def test_unreachable(self) -> None:
        assert intrusion_paths(DEFAULT_NETWORK, "internet", "ghost") == []

    def test_path_validation(self) -> None:
        with pytest.raises(ValueError):
            IntrusionPath(hosts=())

    def test_hops(self) -> None:
        assert IntrusionPath(hosts=("a", "b", "c")).hops == 2


class TestShortestPath:
    def test_known_shortest(self) -> None:
        p = shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert p is not None
        assert p.hops == 5
        assert p.hosts == ("internet", "demarc", "dmz_mail", "intranet_hub", "ops_db", "registry")

    def test_trivial_same_node(self) -> None:
        p = shortest_intrusion_path(DEFAULT_NETWORK, "registry", "registry")
        assert p is not None and p.hosts == ("registry",)

    def test_unreachable_returns_none(self) -> None:
        assert shortest_intrusion_path(DEFAULT_NETWORK, "registry", "internet") is None

    def test_missing_node(self) -> None:
        assert shortest_intrusion_path(DEFAULT_NETWORK, "ghost", DEFAULT_TARGET) is None


class TestCheapestPath:
    def test_deterministic_cheapest(self) -> None:
        p = cheapest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert p is not None
        # The legacy-LDAP route is expensive; the direct route is cheaper.
        assert "legacy_ldap" not in p.hosts
        assert p.hosts[-1] == "registry"

    def test_trivial(self) -> None:
        p = cheapest_intrusion_path(DEFAULT_NETWORK, "x" if "x" in DEFAULT_NETWORK.nodes else "internet", "internet")
        assert p is not None and p.hosts == ("internet",)

    def test_missing_node(self) -> None:
        assert cheapest_intrusion_path(DEFAULT_NETWORK, "ghost", DEFAULT_TARGET) is None


class TestProbability:
    def test_cumulative_product(self) -> None:
        p = shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert p is not None
        prob = path_success_probability(DEFAULT_NETWORK, p)
        assert 0.0 <= prob <= 1.0
        # More hops and exposed nodes => lower probability than a direct check.
        single = path_success_probability(DEFAULT_NETWORK, IntrusionPath(hosts=("a",)))
        assert single == 0.0

    def test_lower_exposure_higher_success(self) -> None:
        # Lower-exposure destination (demarc 0.2) => higher survival than
        # the highly-exposed legacy LDAP pivot (0.9).
        safe = IntrusionPath(hosts=("internet", "demarc"))
        risky = IntrusionPath(hosts=("internet", "legacy_ldap"))
        assert path_success_probability(DEFAULT_NETWORK, safe) > path_success_probability(DEFAULT_NETWORK, risky)


class TestSimulate:
    def test_simulate_reaches_target(self) -> None:
        p = shortest_intrusion_path(DEFAULT_NETWORK, DEFAULT_ENTRY, DEFAULT_TARGET)
        assert p is not None
        sim = simulate_intrusion(DEFAULT_NETWORK, p)
        assert sim["verdict"] == "reached_target"
        assert sim["contained"] is False
        assert sim["hops"] == p.hops
        assert sim["path"] == p.hosts
        assert len(sim["hop_survival"]) == len(p.hosts)

    def test_simulation_contained_with_short_budget(self) -> None:
        p = IntrusionPath(hosts=("internet", "demarc", "dmz_mail", "intranet_hub", "ops_db", "registry"))
        sim = simulate_intrusion(DEFAULT_NETWORK, p, containment_hops=2)
        assert sim["contained"] is True
        assert sim["verdict"] == "contained"

    def test_single_node_no_hop_survival_hops(self) -> None:
        sim = simulate_intrusion(DEFAULT_NETWORK, IntrusionPath(hosts=("internet",)))
        assert sim["hops"] == 0
        assert sim["path"] == ("internet",)
        assert sim["hop_survival"] == [1.0]
