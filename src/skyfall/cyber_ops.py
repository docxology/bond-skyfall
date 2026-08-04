"""Cyber operations against MI6's headquarters network (the SILVA intrusion).

The mission's cyber layer models the MI6 (SIS) operations network as a
directed graph of hosts and routing segments. An adversary — the SILVA attack
cell — enters at an exposed edge and works toward a high-value target (the
operations database / black-site registry). This module computes, entirely
deterministically:

* every simple intrusion path from an entry host to a target host
  (:func:`intrusion_paths`, depth-first enumeration);
* the minimum-hop intrusion path (:func:`shortest_intrusion_path`, BFS);
* the minimum-difficulty intrusion path under per-edge traversal costs
  (:func:`cheapest_intrusion_path`, Dijkstra);
* the cumulative probability that a given path is traversed without the
  intrusion being contained, as the product of per-edge survival
  probabilities (:func:`path_success_probability`);
* a step-by-step attack simulation over a chosen path
  (:func:`simulate_intrusion`).

The network is a frozen dataclass built from an adjacency map; all algorithms
operate on string node ids so the module is pure, importable without the
BOND protocol, and fully deterministic.

Skyfall lineage: the 2012 film portrays a coordinated external cyber assault
on MI6's headquarters — a single adversary reaching the deepest, most
sensitive systems through a chain of aging, poorly-segmented connections.
This module turns that story into a concrete reachability and path-finding
problem.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable

__all__ = [
    "Network",
    "Node",
    "IntrusionPath",
    "build_network",
    "intrusion_paths",
    "shortest_intrusion_path",
    "cheapest_intrusion_path",
    "path_success_probability",
    "simulate_intrusion",
    "DEFAULT_NETWORK",
    "DEFAULT_ENTRY",
    "DEFAULT_TARGET",
]


@dataclass(frozen=True)
class Node:
    """A single host or routing segment in the MI6 network.

    ``role`` is a human label (e.g. "firewall", "database"); ``exposure`` is a
    scalar in ``[0, 1]`` describing how exposed the node is to a remote
    adversary (higher = more exposed / easier to pivot through).
    """

    name: str
    role: str
    exposure: float = 0.5

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Node.name must be a non-empty string")
        if not self.role.strip():
            raise ValueError("Node.role must be a non-empty string")
        if not 0.0 <= self.exposure <= 1.0:
            raise ValueError("Node.exposure must be in [0, 1]")


@dataclass(frozen=True)
class Network:
    """A directed network of nodes and directed routing edges.

    ``nodes`` maps a node name to its :class:`Node`; ``edges`` maps a source
    name to a tuple of reachable destination names. ``edge_cost`` maps an
    ``(source, destination)`` pair to a positive traversal difficulty.
    """

    nodes: dict[str, Node] = field(default_factory=dict)
    edges: dict[str, tuple[str, ...]] = field(default_factory=dict)
    edge_cost: dict[tuple[str, str], float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, node in self.nodes.items():
            if name != node.name:
                raise ValueError(f"network node key {name!r} does not match Node.name {node.name!r}")
        for src, dsts in self.edges.items():
            if src not in self.nodes:
                raise ValueError(f"edge source {src!r} is not a known node")
            for dst in dsts:
                if dst not in self.nodes:
                    raise ValueError(f"edge destination {dst!r} is not a known node")
        for (src, dst), cost in self.edge_cost.items():
            if cost <= 0:
                raise ValueError(f"edge cost for ({src}, {dst}) must be positive, got {cost!r}")

    def neighbours(self, node: str) -> tuple[str, ...]:
        """Return the ordered out-neighbours of ``node`` (empty if unknown)."""
        return self.edges.get(node, ())

    def hop_cost(self, src: str, dst: str) -> float:
        """Return the traversal difficulty of an edge (defaults to 1.0)."""
        return self.edge_cost.get((src, dst), 1.0)


@dataclass(frozen=True)
class IntrusionPath:
    """A single intrusion path: an ordered tuple of host names."""

    hosts: tuple[str, ...]

    @property
    def hops(self) -> int:
        """Number of routing segments traversed (len(hosts) - 1)."""
        return len(self.hosts) - 1

    def __post_init__(self) -> None:
        if not self.hosts:
            raise ValueError("IntrusionPath.hosts must be non-empty")


def build_network(
    nodes: Iterable[Node],
    edges: dict[str, Iterable[str]],
    edge_cost: dict[tuple[str, str], float] | None = None,
    default_exposure: float | None = None,
) -> Network:
    """Build a :class:`Network` from a node iterable and an adjacency map.

    Any node named in ``edges`` but not provided explicitly is created with
    role ``"host"`` and exposure ``default_exposure`` (or 0.5).

    Args:
        nodes: The explicit nodes (may be empty to rely on edge discovery).
        edges: Source name -> iterable of destination names.
        edge_cost: Optional ``(src, dst)`` -> difficulty map.
        default_exposure: Exposure assigned to implicitly-created nodes.

    Returns:
        A validated :class:`Network`.
    """
    node_map: dict[str, Node] = {}
    for node in nodes:
        node_map[node.name] = node
    exposure = default_exposure if default_exposure is not None else 0.5
    for src, dsts in edges.items():
        node_map.setdefault(src, Node(name=src, role="host", exposure=exposure))
        for dst in dsts:
            node_map.setdefault(dst, Node(name=dst, role="host", exposure=exposure))
    adjacency = {src: tuple(dsts) for src, dsts in edges.items()}
    return Network(nodes=node_map, edges=adjacency, edge_cost=dict(edge_cost or {}))


def intrusion_paths(network: Network, entry: str, target: str) -> list[IntrusionPath]:
    """Enumerate every simple path from ``entry`` to ``target`` (DFS).

    Neighbours are traversed in deterministic (sorted) order so the result is
    stable. A simple path never revisits a node, bounding the search.

    Returns:
        A list of :class:`IntrusionPath` ordered by first-visit during DFS.
    """
    if entry not in network.nodes or target not in network.nodes:
        return []
    paths: list[IntrusionPath] = []

    def _dfs(current: str, visited: set[str], trail: list[str]) -> None:
        if current == target:
            paths.append(IntrusionPath(hosts=tuple(trail)))
            return
        for nxt in sorted(network.neighbours(current)):
            if nxt in visited:
                continue
            visited.add(nxt)
            trail.append(nxt)
            _dfs(nxt, visited, trail)
            trail.pop()
            visited.discard(nxt)

    visited = {entry}
    _dfs(entry, visited, [entry])
    return paths


def shortest_intrusion_path(network: Network, entry: str, target: str) -> IntrusionPath | None:
    """Return a minimum-hop path from ``entry`` to ``target`` (breadth-first).

    Any shortest path satisfies the mission's core reachability question; the
    first one found in deterministic neighbour order is returned.

    Returns:
        An :class:`IntrusionPath` with minimal hops, or ``None`` if unreachable.
    """
    if entry not in network.nodes or target not in network.nodes:
        return None
    if entry == target:
        return IntrusionPath(hosts=(entry,))
    prev: dict[str, str | None] = {entry: None}
    queue: deque[str] = deque([entry])
    found: str | None = None
    while queue:
        current = queue.popleft()
        for nxt in sorted(network.neighbours(current)):
            if nxt in prev:
                continue
            prev[nxt] = current
            if nxt == target:
                found = nxt
                break
            queue.append(nxt)
        if found is not None:
            break
    if found is None:
        return None
    # Reconstruct the path back to the entry.
    hosts: list[str] = []
    node: str | None = found
    while node is not None:
        hosts.append(node)
        node = prev[node]
    return IntrusionPath(hosts=tuple(reversed(hosts)))


def cheapest_intrusion_path(network: Network, entry: str, target: str) -> IntrusionPath | None:
    """Return the minimum-difficulty path under per-edge traversal costs.

    Uses Dijkstra's algorithm on the directed graph with
    :meth:`Network.hop_cost` as the (positive) edge weight. Deterministic tie
    breaking via sorted neighbour order.

    Returns:
        An :class:`IntrusionPath` minimizing total difficulty, or ``None``.
    """
    if entry not in network.nodes or target not in network.nodes:
        return None
    if entry == target:
        return IntrusionPath(hosts=(entry,))
    # (cost, node, path) priority queue; tuples compare deterministically.
    heap: list[tuple[float, str, tuple[str, ...]]] = [(0.0, entry, (entry,))]
    best: dict[str, float] = {entry: 0.0}
    while heap:
        cost, current, path = heapq.heappop(heap)
        if cost > best.get(current, float("inf")):
            continue
        if current == target:
            return IntrusionPath(hosts=path)
        for nxt in sorted(network.neighbours(current)):
            new_cost = cost + network.hop_cost(current, nxt)
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                heapq.heappush(heap, (new_cost, nxt, path + (nxt,)))
    return None


def path_success_probability(network: Network, path: IntrusionPath, base_survival: float = 0.8) -> float:
    """Return the probability the intrusion traverses ``path`` uncontained.

    Each hop survives with probability ``base_survival * (1 - dst_exposure)``
    folded through the destination's exposure; the cumulative probability is
    the product over hops. Lower exposure (harder to pivot) ⇒ lower success.

    Args:
        network: The network whose node exposures parameterize the model.
        path: The intrusion path to evaluate.
        base_survival: Baseline per-hop survival before exposure discounting.

    Returns:
        A probability in ``[0, 1]`` (0 for a single-node path, which is the
        degenerate "already there" case).
    """
    if len(path.hosts) < 2:
        return 0.0
    prob = 1.0
    for dst in path.hosts[1:]:
        exposure = network.nodes[dst].exposure
        hop_prob = base_survival * (1.0 - exposure)
        prob *= max(0.0, min(1.0, hop_prob))
    return prob


def simulate_intrusion(
    network: Network,
    path: IntrusionPath,
    base_survival: float = 0.8,
    containment_hops: int = 6,
) -> dict[str, object]:
    """Simulate a step-by-step intrusion along ``path``.

    Returns a deterministic dict describing the traversal: the path, cumulative
    survival probability after each hop, whether any hop exceeded the
    ``containment_hops`` budget (a mid-route tripwire), and a verdict string.

    Args:
        network: The network being traversed.
        path: The intrusion path under study.
        base_survival: Per-hop survival baseline.
        containment_hops: Hop index at which the intrusion is considered to
            have run long enough to risk containment (deterministic gate).

    Returns:
        A dict with keys ``path``, ``hop_survival``, ``contained``,
        ``verdict``, ``hops``.
    """
    if not path.hosts:
        raise ValueError("cannot simulate an empty intrusion path")
    hop_survival: list[float] = []
    cum = 1.0
    for idx, dst in enumerate(path.hosts):
        if idx == 0:
            hop_survival.append(1.0)
            continue
        exposure = network.nodes[dst].exposure
        cum *= max(0.0, min(1.0, base_survival * (1.0 - exposure)))
        hop_survival.append(cum)
    contained = len(path.hosts) - 1 > containment_hops
    verdict = "contained" if contained else "reached_target"
    return {
        "path": path.hosts,
        "hop_survival": hop_survival,
        "contained": contained,
        "verdict": verdict,
        "hops": path.hops,
    }


#: The canonical MI6 HQ network used by the flagship mission. Node roles and
#: exposures are fixed so every result is reproducible.
DEFAULT_NETWORK: Network = build_network(
    nodes=[
        Node("internet", "external"),
        Node("demarc", "firewall", exposure=0.2),
        Node("dmz_mail", "mail_relay", exposure=0.5),
        Node("vpn_gateway", "vpn", exposure=0.4),
        Node("intranet_hub", "core_switch", exposure=0.3),
        Node("legacy_ldap", "legacy_directory", exposure=0.9),
        Node("ops_db", "operations_database", exposure=0.3),
        Node("registry", "black_site_registry", exposure=0.1),
        Node("field_terminal", "field_workstation", exposure=0.7),
    ],
    edges={
        "internet": ("demarc",),
        "demarc": ("dmz_mail", "vpn_gateway"),
        "dmz_mail": ("intranet_hub",),
        "vpn_gateway": ("intranet_hub",),
        "intranet_hub": ("legacy_ldap", "ops_db", "field_terminal"),
        "legacy_ldap": ("ops_db",),
        "ops_db": ("registry",),
        "field_terminal": ("ops_db",),
    },
    edge_cost={
        ("internet", "demarc"): 2.0,
        ("demarc", "dmz_mail"): 3.0,
        ("demarc", "vpn_gateway"): 4.0,
        ("dmz_mail", "intranet_hub"): 1.0,
        ("vpn_gateway", "intranet_hub"): 1.0,
        ("intranet_hub", "legacy_ldap"): 5.0,
        ("intranet_hub", "ops_db"): 2.0,
        ("intranet_hub", "field_terminal"): 1.0,
        ("legacy_ldap", "ops_db"): 1.0,
        ("ops_db", "registry"): 1.0,
        ("field_terminal", "ops_db"): 1.0,
    },
)

#: The canonical adversary entry point.
DEFAULT_ENTRY = "internet"
#: The canonical high-value target (the deepest, most sensitive system).
DEFAULT_TARGET = "registry"
