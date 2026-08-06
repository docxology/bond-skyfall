"""Tests for skyfall.estate_defense — island topology and choke-point defense.

Real graph and grid algorithms only (zero mocks). Exercises flood-fill island
topology, Tarjan articulation-point detection, defense planning, and coverage
scoring.
"""

from __future__ import annotations

import pytest

from skyfall.estate_defense import (
    DEFAULT_ESTATE,
    DefensePlan,
    EstateGraph,
    IslandGrid,
    IslandTopology,
    betweenness_centrality,
    choke_points,
    defense_coverage,
    default_island,
    estate_defense_plan,
    island_topology,
)


class TestIslandGrid:
    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            IslandGrid(width=0, height=3, cell=tuple([False] * 0), entry=(0, 0))
        with pytest.raises(ValueError):
            IslandGrid(width=2, height=2, cell=tuple([True] * 3), entry=(0, 0))
        with pytest.raises(ValueError):
            IslandGrid(width=2, height=2, cell=tuple([True] * 4), entry=(5, 5))
        with pytest.raises(ValueError):
            IslandGrid(width=2, height=2, cell=tuple([False] * 4), entry=(0, 0))

    def test_passability_and_neighbours(self) -> None:
        g = IslandGrid(width=2, height=2, cell=(True, True, False, True), entry=(0, 0))
        assert g.is_passable(0, 0) is True
        assert g.is_passable(1, 0) is False
        assert g.neighbours(0, 0) == ((0, 1),)  # right neighbour only

    def test_default_island(self) -> None:
        island = default_island()
        assert island.is_passable(*island.entry)


class TestIslandTopology:
    def test_default_island_corridor(self) -> None:
        topo = island_topology(default_island())
        assert topo.corridor_length == 8
        assert topo.hideout == (2, 6)
        assert topo.reachable and topo.perimeter > 0

    def test_all_passable(self) -> None:
        g = IslandGrid(width=3, height=3, cell=tuple([True] * 9), entry=(0, 0))
        topo = island_topology(g)
        # 3x3 fully connected orthogonal grid: 4-edge cells on corners etc.
        assert len(topo.reachable) == 9
        assert topo.corridor_length == 4

    def test_disconnected(self) -> None:
        g = IslandGrid(width=2, height=2, cell=(True, False, False, True), entry=(0, 0))
        topo = island_topology(g)
        assert len(topo.reachable) == 1

    def test_validation_empty_reachable(self) -> None:
        with pytest.raises(ValueError):
            IslandTopology(island=default_island(), reachable=(), perimeter=0, hideout=(0, 0), corridor_length=0)


class TestEstateGraph:
    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            EstateGraph(positions={"a": (-1, 0)}, roads={"a": ()})
        with pytest.raises(ValueError):
            EstateGraph(positions={"a": (0, 0)}, roads={"b": ()})
        with pytest.raises(ValueError):
            EstateGraph(positions={"a": (0, 0)}, roads={"a": ("ghost",)})

    def test_neighbours(self) -> None:
        assert DEFAULT_ESTATE.neighbours("moors") == ("roadgate",)
        assert DEFAULT_ESTATE.neighbours("ghost") == ()


class TestChokePoints:
    def test_default_estate(self) -> None:
        points = choke_points(DEFAULT_ESTATE)
        assert points == ("field", "mansion", "roadgate")

    def test_known_articulation(self) -> None:
        # Chain graph: every intermediate is an articulation point.
        chain = EstateGraph(
            positions={"a": (0, 0), "b": (1, 0), "c": (2, 0), "d": (3, 0)},
            roads={"a": ("b",), "b": ("a", "c"), "c": ("b", "d"), "d": ("c",)},
        )
        assert choke_points(chain) == ("b", "c")

    def test_cycle_graph_no_articulation(self) -> None:
        cycle = EstateGraph(
            positions={"a": (0, 0), "b": (1, 0), "c": (1, 1), "d": (0, 1)},
            roads={"a": ("b", "d"), "b": ("a", "c"), "c": ("b", "d"), "d": ("c", "a")},
        )
        assert choke_points(cycle) == ()

    def test_disconnected_estate(self) -> None:
        disconnected = EstateGraph(
            positions={"a": (0, 0), "b": (1, 0)},
            roads={"a": (), "b": ()},
        )
        assert choke_points(disconnected) == ()


class TestDefense:
    def test_default_plan_fully_covered(self) -> None:
        plan = estate_defense_plan(DEFAULT_ESTATE, ("Mallory", "Tanner", "Q", "Eve"))
        assert plan.defenders_used == 3
        assert plan.uncovered == ()
        assert defense_coverage(plan) == 1.0

    def test_under_defended(self) -> None:
        plan = estate_defense_plan(DEFAULT_ESTATE, ("Mallory",))
        assert plan.defenders_used == 1
        assert len(plan.uncovered) == 2
        assert defense_coverage(plan) == pytest.approx(1 / 3)

    def test_no_choke_points(self) -> None:
        cycle = EstateGraph(
            positions={"a": (0, 0), "b": (1, 0), "c": (1, 1)},
            roads={"a": ("b",), "b": ("a", "c"), "c": ("b",)},
        )
        # triangle would have none, but this is a chain => b is articulation
        plan = estate_defense_plan(cycle, ("Q",))
        assert defense_coverage(plan) == 1.0

    def test_empty_defenders_blocked(self) -> None:
        with pytest.raises(ValueError):
            estate_defense_plan(DEFAULT_ESTATE, ("",))

    def test_coverage_empty_plan(self) -> None:
        assert defense_coverage(DefensePlan(assigned={}, covered=(), uncovered=(), defenders_used=0)) == 0.0

    def test_covered_uncovered_sorting(self) -> None:
        plan = estate_defense_plan(DEFAULT_ESTATE, ("Mallory",))
        assert plan.covered == ("field",)  # highest-degree choke point first


class TestRoadSymmetryInvariant:
    """Tarjan's search assumes an undirected adjacency; enforce it.

    A one-sided road used to be accepted and silently produced a wrong
    choke-point set rather than an error — the worst kind of failure for a
    defensive plan.
    """

    def test_one_sided_road_rejected(self) -> None:
        with pytest.raises(ValueError, match="not mirrored"):
            EstateGraph(
                positions={"a": (0, 0), "b": (1, 0)},
                roads={"a": ("b",), "b": ()},
            )

    def test_missing_reverse_entry_rejected(self) -> None:
        with pytest.raises(ValueError, match="not mirrored"):
            EstateGraph(positions={"a": (0, 0), "b": (1, 0)}, roads={"a": ("b",)})

    def test_canonical_estate_is_symmetric(self) -> None:
        for src, connected in DEFAULT_ESTATE.roads.items():
            for dst in connected:
                assert src in DEFAULT_ESTATE.roads[dst]


class TestDefensePlanWithoutChokePoints:
    """A graph with no articulation points yields an explicitly empty plan."""

    def test_triangle_has_no_choke_points(self) -> None:
        triangle = EstateGraph(
            positions={"a": (0, 0), "b": (1, 0), "c": (1, 1)},
            roads={"a": ("b", "c"), "b": ("a", "c"), "c": ("a", "b")},
        )
        assert choke_points(triangle) == ()
        plan = estate_defense_plan(triangle, ("Q", "Eve"))
        assert plan.assigned == {}
        assert plan.covered == ()
        assert plan.uncovered == ()
        assert plan.defenders_used == 0
        # No choke points means nothing to cover: coverage is 0/0, reported 0.0.
        assert defense_coverage(plan) == 0.0


def _path_graph() -> EstateGraph:
    """The E2 distinguishing graph: a path where every internal node has equal
    degree (2) but the centre carries the most shortest-path traffic."""
    return EstateGraph(
        positions={"a": (0, 0), "b": (1, 0), "c": (2, 0), "d": (3, 0), "e": (4, 0)},
        roads={
            "a": ("b",),
            "b": ("a", "c"),
            "c": ("b", "d"),
            "d": ("c", "e"),
            "e": ("d",),
        },
    )


class TestBetweenness:
    def test_line_middle_is_most_central(self) -> None:
        bc = betweenness_centrality(_path_graph())
        assert bc["c"] > bc["b"] > 0.0
        assert bc["c"] == pytest.approx(2.0 / 3.0, abs=1e-9)
        assert bc["a"] == pytest.approx(0.0)

    def test_all_values_in_unit_interval(self) -> None:
        for value in betweenness_centrality(DEFAULT_ESTATE).values():
            assert 0.0 <= value <= 1.0

    def test_canonical_estate_is_stable(self) -> None:
        a = betweenness_centrality(DEFAULT_ESTATE)
        b = betweenness_centrality(DEFAULT_ESTATE)
        assert a == b

    def test_two_node_graph_has_no_betweenness(self) -> None:
        g = EstateGraph(positions={"a": (0, 0), "b": (1, 0)}, roads={"a": ("b",), "b": ("a",)})
        assert betweenness_centrality(g) == {"a": 0.0, "b": 0.0}


class TestDefenseRank:
    def test_unknown_rank_raises(self) -> None:
        with pytest.raises(ValueError, match="rank"):
            estate_defense_plan(DEFAULT_ESTATE, ("Q",), rank="bogus")

    def test_degree_and_betweenness_disagree_on_path(self) -> None:
        """Degree sees every internal node as equally important (degree 2) and
        falls back to id order; betweenness correctly ranks the centre first."""
        by_degree = estate_defense_plan(_path_graph(), ("d0",), rank="degree")
        by_between = estate_defense_plan(_path_graph(), ("d0",), rank="betweenness")
        assert by_degree.assigned == {"b": "d0"}  # lexicographic tie-break
        assert by_between.assigned == {"c": "d0"}  # real traffic centre
        assert by_degree.assigned != by_between.assigned

    def test_degree_default_unchanged(self) -> None:
        # rank="degree" is the default; canonical estate still covers `field` first.
        plan = estate_defense_plan(DEFAULT_ESTATE, ("Mallory",))
        assert plan.covered == ("field",)
