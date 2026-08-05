"""Island hideout topology and the Skyfall estate defense plan.

The SILVA mission's physical-defense layer covers two linked problems from the
2012 film:

* **Silva's island hideout topology.** The abandoned island compound is
  modeled as a grid of passable cells with a single fortified approach
  corridor. :class:`IslandGrid` computes reachable area (flood fill), the
  island's perimeter, and the distance from every reachable cell back to the
  single entry — the "contested corridor" through which any assault must
  travel.

* **The Skyfall estate defense plan.** The estate's approach is modeled as an
  undirected graph of positions connected by roads/trails. Articulation
  points (cut vertices) are the estate's **choke points** — positions whose
  loss severs every route from the moors to the mansion. :func:`choke_points`
  finds them with Tarjan's algorithm, and :func:`estate_defense_plan` assigns
  a limited set of defenders to cover every choke point.

All algorithms are deterministic, pure, and independent of the BOND protocol.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "IslandGrid",
    "EstateGraph",
    "island_topology",
    "choke_points",
    "estate_defense_plan",
    "defense_coverage",
    "default_island",
    "DEFAULT_ESTATE",
]


@dataclass(frozen=True)
class IslandGrid:
    """A rectangular island cell grid with a single beachhead entry.

    ``cell`` is True for passable terrain; ``entry`` is the (row, col) landing
    point. The hideout (Silva's fortified core) is the farthest reachable cell
    from the entry, reached along the narrow approach corridor.
    """

    width: int
    height: int
    cell: tuple[bool, ...]
    entry: tuple[int, int]

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("island grid must have positive dimensions")
        if len(self.cell) != self.width * self.height:
            raise ValueError("cell map length must equal width * height")
        if not 0 <= self.entry[0] < self.height or not 0 <= self.entry[1] < self.width:
            raise ValueError("entry cell lies outside the grid")
        if not self.is_passable(*self.entry):
            raise ValueError("entry cell must be passable")

    def _idx(self, row: int, col: int) -> int:
        return row * self.width + col

    def is_passable(self, row: int, col: int) -> bool:
        """Return whether a cell is within bounds and passable."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        return self.cell[self._idx(row, col)]

    def neighbours(self, row: int, col: int) -> tuple[tuple[int, int], ...]:
        """Return passable orthogonal neighbours of a cell, deterministically."""
        result: list[tuple[int, int]] = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = row + dr, col + dc
            if self.is_passable(nr, nc):
                result.append((nr, nc))
        return tuple(result)


@dataclass(frozen=True)
class IslandTopology:
    """Computed topology of an island grid."""

    island: IslandGrid
    reachable: tuple[tuple[int, int], ...]
    perimeter: int
    hideout: tuple[int, int]
    corridor_length: int

    def __post_init__(self) -> None:
        if not self.reachable:
            raise ValueError("island topology must have at least the entry cell reachable")


def island_topology(island: IslandGrid) -> IslandTopology:
    """Flood-fill compute reachable area, perimeter, and the hideout.

    The hideout is the reachable cell whose BFS distance from the entry is
    greatest (ties resolved to the lexicographically smallest), and the
    corridor length is exactly that distance.

    Args:
        island: The island grid to analyze.

    Returns:
        An :class:`IslandTopology`.
    """
    # ``IslandGrid.__post_init__`` already rejects an impassable entry, so no
    # re-check is performed here: a guard that cannot fire reads as coverage it
    # does not provide.
    entry = island.entry
    visited: set[tuple[int, int]] = {entry}
    queue: deque[tuple[int, int]] = deque([entry])
    dist: dict[tuple[int, int], int] = {entry: 0}
    perimeter = 0
    while queue:
        cell = queue.popleft()
        neighbours = island.neighbours(*cell)
        perimeter += 4 - len(neighbours)
        for nxt in neighbours:
            if nxt not in visited:
                visited.add(nxt)
                dist[nxt] = dist[cell] + 1
                queue.append(nxt)
    reachable = tuple(sorted(visited))
    hideout = max(dist, key=lambda c: (dist[c], c))
    return IslandTopology(
        island=island,
        reachable=reachable,
        perimeter=perimeter,
        hideout=hideout,
        corridor_length=dist[hideout],
    )


@dataclass(frozen=True)
class EstateGraph:
    """An undirected estate approach graph.

    ``positions`` maps a position name to its (row, col) or label coordinate;
    ``roads`` maps a position to the tuple of connected positions. Edges are
    symmetric: ``(a, b)`` implies ``(b, a)``, and that invariant is *enforced*
    at construction — Tarjan's articulation search assumes an undirected
    adjacency, so a one-sided road would silently yield a wrong choke-point
    set rather than an error.
    """

    positions: dict[str, tuple[int, int]]
    roads: dict[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        for name, (row, col) in self.positions.items():
            if row < 0 or col < 0:
                raise ValueError(f"position {name!r} has invalid coordinates")
        for a, connected in self.roads.items():
            if a not in self.positions:
                raise ValueError(f"road source {a!r} is not a known position")
            for b in connected:
                if b not in self.positions:
                    raise ValueError(f"road destination {b!r} is not a known position")
                if a not in self.roads.get(b, ()):
                    raise ValueError(f"road {a!r} -> {b!r} is not mirrored by {b!r} -> {a!r}")

    def neighbours(self, node: str) -> tuple[str, ...]:
        """Return the connected positions of ``node`` (empty if unknown)."""
        return self.roads.get(node, ())


#: The canonical Skyfall estate approach network. The mansion sits at the
#: centre; the moors (attackers) connect through the single narrow access.
DEFAULT_ESTATE: EstateGraph = EstateGraph(
    positions={
        "moors": (0, 0),
        "roadgate": (1, 0),
        "field": (2, 1),
        "mansion": (3, 2),
        "grounds_east": (2, 3),
        "grounds_north": (2, 4),
        "lake_path": (4, 3),
    },
    roads={
        "moors": ("roadgate",),
        "roadgate": ("moors", "field"),
        "field": ("roadgate", "mansion", "grounds_east"),
        "mansion": ("field", "grounds_north", "lake_path"),
        "grounds_east": ("field", "grounds_north"),
        "grounds_north": ("grounds_east", "mansion"),
        "lake_path": ("mansion",),
    },
)


def choke_points(graph: EstateGraph) -> tuple[str, ...]:
    """Find the estate's choke points (articulation points) via Tarjan's DFS.

    A position is a choke point when removing it disconnects the graph — i.e.
    every path between two other positions must pass through it. These are the
    single-points-of-failure the estate defense must hold.

    Args:
        graph: The estate approach graph.

    Returns:
        A tuple of choke-point names in deterministic (sorted) order.
    """
    # Iterative Tarjan articulation-point search using explicit stacks.
    from collections import defaultdict

    ids: dict[str, int] = {}
    low: dict[str, int] = {}
    parent: dict[str, str | None] = {}
    is_artic: set[str] = set()
    children: dict[str, int] = defaultdict(int)
    counter = 0

    for root in sorted(graph.positions):
        if root in ids:
            continue
        # DFS stack of (node, iterator_index).
        order: list[str] = [root]
        parent[root] = None
        ids[root] = counter
        low[root] = counter
        counter += 1
        children[root] = 0
        index: dict[str, int] = {root: 0}
        while order:
            node = order[-1]
            neighbours = sorted(graph.neighbours(node))
            if index[node] < len(neighbours):
                nxt = neighbours[index[node]]
                index[node] += 1
                if nxt not in ids:
                    parent[nxt] = node
                    children[node] += 1
                    ids[nxt] = counter
                    low[nxt] = counter
                    counter += 1
                    order.append(nxt)
                    index[nxt] = 0
                elif nxt != parent[node]:
                    low[node] = min(low[node], ids[nxt])
            else:
                order.pop()
                par = parent[node]
                if par is not None:
                    low[par] = min(low[par], low[node])
                    if low[node] >= ids[par] and par not in is_artic:
                        if par != root or children[par] > 1:
                            is_artic.add(par)
        # Root is an articulation point iff it has > 1 DFS children.
        if children[root] > 1:
            is_artic.add(root)
    return tuple(sorted(is_artic))


@dataclass(frozen=True)
class DefensePlan:
    """A defense assignment: defenders placed at estate choke points."""

    assigned: dict[str, str]
    covered: tuple[str, ...]
    uncovered: tuple[str, ...]
    defenders_used: int


def defense_coverage(plan: DefensePlan) -> float:
    """Return the fraction of choke points covered by the plan in ``[0, 1]``."""
    total = len(plan.covered) + len(plan.uncovered)
    if total == 0:
        return 0.0
    return len(plan.covered) / total


def estate_defense_plan(
    graph: EstateGraph,
    defenders: Iterable[str],
) -> DefensePlan:
    """Assign a limited team of defenders to cover the estate's choke points.

    Defenders are assigned greedily: each choke point receives one defender,
    in descending choke-point importance. If there are more choke points than
    defenders, the least-critical remain uncovered (reported explicitly).

    Args:
        graph: The estate approach graph.
        defenders: Ordered list of defender call signs (or station names).

    Returns:
        A :class:`DefensePlan` mapping choke point -> assigned defender, with
        the covered and uncovered choke-point lists.
    """
    points = choke_points(graph)
    if not points:
        return DefensePlan(assigned={}, covered=(), uncovered=(), defenders_used=0)
    defender_list = list(defenders)
    # Rank choke points by graph centrality: number of connected positions.
    degree = {name: len(graph.neighbours(name)) for name in points}
    ranked = sorted(points, key=lambda p: (-degree[p], p))
    assigned: dict[str, str] = {}
    for idx, point in enumerate(ranked[: len(defender_list)]):
        defender = defender_list[idx]
        if not defender.strip():
            raise ValueError("defender call signs must be non-empty strings")
        assigned[point] = defender
    covered = tuple(sorted(assigned))
    uncovered = tuple(p for p in points if p not in assigned)
    return DefensePlan(
        assigned=assigned,
        covered=covered,
        uncovered=uncovered,
        defenders_used=len(assigned),
    )


#: The canonical island topology for the SILVA hideout scenario (a narrow
#: approach corridor from a single beachhead to a fortified core).
def default_island() -> IslandGrid:
    """Return the canonical Silva island grid (rows x cols, corridor + core)."""
    width, height = 7, 3
    # Row 0 is water (barrier) except the entry; row 1 is a narrow corridor;
    # row 2 is the fortified core.
    cells: list[bool] = []
    for row in range(height):
        for col in range(width):
            if row == 0:
                passable = col == 0  # only the beachhead in the top row
            elif row == 1:
                passable = True  # the approach corridor spans the row
            else:
                passable = col >= 4  # the fortified core at the far end
            cells.append(passable)
    return IslandGrid(width=width, height=height, cell=tuple(cells), entry=(0, 0))
