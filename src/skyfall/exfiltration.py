"""Data exfiltration analysis: max-flow and min-cut over the HQ network.

The SILVA mission's containment layer asks a dual question to the path
enumeration of :mod:`skyfall.cyber_ops`: the adversary is not merely *moving
through* the MI6 network — data is *leaving* it. The NATO agent list held in
the registry is exfiltrated outward, hop by hop, toward the internet. This
module models that outward transfer as a capacitated flow problem:

* :func:`edmonds_karp` — computes the maximum exfiltration rate from the
  registry (source) to the internet (sink) using BFS augmenting paths,
  returning the max-flow value and the per-edge flow;
* :func:`min_cut_edges` — after the max flow saturates the residual graph,
  the set of edges crossing the reachable/non-reachable cut is the minimum
  collection of links that must be severed to stop the exfiltration
  (the max-flow min-cut theorem guarantees its total capacity equals the max
  flow);
* :func:`severance_plan` — names that cut as an ordered list of link
  severances (the mission's containment decision).

Edmonds–Karp pushes exactly the BFS path's bottleneck at every augmentation,
so the residual stays consistent and the min-cut value equals the max flow.
All iteration is deterministic (sorted neighbour order), the capacities are
fixed constants, and the module imports nothing but the standard library.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "FlowNetwork",
    "FlowResult",
    "CutResult",
    "edmonds_karp",
    "min_cut_edges",
    "severance_plan",
    "DEFAULT_FLOW_NETWORK",
    "EXFIL_SOURCE",
    "EXFIL_SINK",
]


@dataclass(frozen=True)
class FlowNetwork:
    """A directed capacitated network.

    ``edges`` maps a source node to its out-neighbours; ``capacity`` maps an
    ``(src, dst)`` pair to a positive capacity.
    """

    nodes: tuple[str, ...]
    edges: dict[str, tuple[str, ...]]
    capacity: dict[tuple[str, str], float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.nodes:
            raise ValueError("FlowNetwork.nodes must be non-empty")
        for src, dsts in self.edges.items():
            if src not in self.nodes:
                raise ValueError(f"edge source {src!r} is not a network node")
            for dst in dsts:
                if dst not in self.nodes:
                    raise ValueError(f"edge destination {dst!r} is not a network node")
        for (src, dst), cap in self.capacity.items():
            if cap <= 0:
                raise ValueError(f"capacity for ({src}, {dst}) must be positive, got {cap!r}")

    def out_neighbours(self, node: str) -> tuple[str, ...]:
        """Return the deterministic out-neighbour order of ``node``."""
        return self.edges.get(node, ())

    def cap(self, src: str, dst: str) -> float:
        """Return the capacity of an edge (0 when the edge is absent)."""
        return self.capacity.get((src, dst), 0.0)


@dataclass(frozen=True)
class FlowResult:
    """Max-flow solution: total flow value plus per-edge flows."""

    value: float
    flow: dict[tuple[str, str], float]


@dataclass(frozen=True)
class CutResult:
    """Min-cut solution: cut capacity plus the ordered severance edge list."""

    value: float
    edges: tuple[tuple[str, str], ...]


def edmonds_karp(
    network: FlowNetwork,
    source: str,
    sink: str,
) -> FlowResult:
    """Compute the maximum flow from ``source`` to ``sink`` (Edmonds–Karp).

    BFS finds the shortest augmenting path in the residual graph; each
    augmentation pushes exactly that path's bottleneck capacity. Neighbours
    are visited in deterministic (sorted) order.

    Args:
        network: The capacitated network.
        source: Flow source node.
        sink: Flow sink node.

    Returns:
        A :class:`FlowResult` with the total flow value and per-edge flows.

    Raises:
        ValueError: if source/sink are unknown or identical.
    """
    if source not in network.nodes or sink not in network.nodes:
        raise ValueError("source and sink must be network nodes")
    if source == sink:
        raise ValueError("source and sink must differ")

    # Residual capacity map; start from the declared capacities.
    residual: dict[tuple[str, str], float] = {
        (src, dst): network.cap(src, dst)
        for src in network.nodes
        for dst in network.out_neighbours(src)
        if network.cap(src, dst) > 0
    }
    flow: dict[tuple[str, str], float] = {}

    def _bfs() -> tuple[dict[str, str | None], float]:
        prev: dict[str, str | None] = {source: None}
        queue: deque[str] = deque([source])
        while queue:
            current = queue.popleft()
            for nxt in sorted(network.out_neighbours(current)):
                if nxt in prev:
                    continue
                capacity = residual.get((current, nxt), 0.0)
                if capacity > 0:
                    prev[nxt] = current
                    queue.append(nxt)
        if sink not in prev:
            return prev, 0.0
        # Bottleneck along the BFS tree path (deterministic walk-back).
        bottleneck = float("inf")
        node = sink
        while True:
            parent: str | None = prev[node]
            if parent is None:
                break
            bottleneck = min(bottleneck, residual.get((parent, node), 0.0))
            node = parent
        return prev, bottleneck

    total = 0.0
    while True:
        prev, bottleneck = _bfs()
        if bottleneck <= 0:
            break
        node = sink
        while True:
            parent: str | None = prev[node]
            if parent is None:
                break
            residual[(parent, node)] = residual.get((parent, node), 0.0) - bottleneck
            # Reverse edge for augmenting later.
            residual[(node, parent)] = residual.get((node, parent), 0.0) + bottleneck
            flow[(parent, node)] = flow.get((parent, node), 0.0) + bottleneck
            node = parent
        total += bottleneck
    return FlowResult(value=total, flow=flow)


def min_cut_edges(
    network: FlowNetwork,
    source: str,
    sink: str,
) -> CutResult:
    """Return the minimum cut separating ``source`` from ``sink``.

    Computes the max flow, then BFS-reaches every node still reachable in the
    residual graph — **including the reverse arcs induced by pushed flow** —
    and takes the cut to be the original edges leaving that reachable set. By
    the max-flow min-cut theorem its total capacity equals the max-flow value,
    which :func:`min_cut_edges` guarantees for every network, not merely for
    the acyclic canonical one.

    Returns:
        A :class:`CutResult` whose ``edges`` are ordered (source node, then
        destination node) deterministically.
    """
    result = edmonds_karp(network, source, sink)
    # Rebuild the final residual to determine reachability.
    residual: dict[tuple[str, str], float] = {
        (src, dst): network.cap(src, dst)
        for src in network.nodes
        for dst in network.out_neighbours(src)
        if network.cap(src, dst) > 0
    }
    for (src, dst), amount in result.flow.items():
        residual[(src, dst)] = residual.get((src, dst), 0.0) - amount
        residual[(dst, src)] = residual.get((dst, src), 0.0) + amount

    # Reachability must follow the *residual* graph, which includes the reverse
    # arcs created by pushed flow. Walking only the original forward edges
    # under-approximates the source side of the cut: any edge carrying flow
    # *into* that under-approximated set is then counted as a cut edge, and the
    # reported cut value exceeds the max flow, breaking the theorem this
    # function documents. See tests/test_exfiltration.py::TestMinCut for the
    # enumerated positive control that pins this.
    residual_adjacency: dict[str, list[str]] = {}
    for (src, dst), capacity in residual.items():
        if capacity > 0:
            residual_adjacency.setdefault(src, []).append(dst)

    reachable: set[str] = {source}
    queue: deque[str] = deque([source])
    while queue:
        current = queue.popleft()
        for nxt in sorted(residual_adjacency.get(current, ())):
            if nxt in reachable:
                continue
            reachable.add(nxt)
            queue.append(nxt)

    cut_edges = [
        (u, v)
        for u in network.nodes
        for v in network.out_neighbours(u)
        if u in reachable and v not in reachable and network.cap(u, v) > 0
    ]
    cut_edges.sort()
    cut_value = sum(network.cap(u, v) for u, v in cut_edges)
    return CutResult(value=cut_value, edges=tuple(cut_edges))


def severance_plan(cut: CutResult) -> tuple[str, ...]:
    """Render a min-cut as a human-readable ordered severance plan.

    Args:
        cut: The min-cut to render.

    Returns:
        An ordered tuple of ``"sever <src> -> <dst>"`` directives.
    """
    return tuple(f"sever {u} -> {v}" for u, v in cut.edges)


def _build_default_flow_network() -> FlowNetwork:
    """Construct the canonical exfiltration capacity network.

    The registry (agent list) is the source; the internet is the sink. The
    inner network mirrors :data:`skyfall.cyber_ops.DEFAULT_NETWORK`'s
    topology, with capacities expressing how much data can move per unit time
    across each hop.
    """
    nodes = (
        "registry",
        "ops_db",
        "legacy_ldap",
        "intranet_hub",
        "dmz_mail",
        "vpn_gateway",
        "demarc",
        "internet",
    )
    edges = {
        "registry": ("ops_db",),
        "ops_db": ("intranet_hub", "legacy_ldap"),
        "legacy_ldap": ("intranet_hub",),
        "intranet_hub": ("dmz_mail", "vpn_gateway"),
        "dmz_mail": ("demarc",),
        "vpn_gateway": ("demarc",),
        "demarc": ("internet",),
        "internet": (),
    }
    capacity = {
        ("registry", "ops_db"): 10.0,
        ("ops_db", "intranet_hub"): 8.0,
        ("ops_db", "legacy_ldap"): 3.0,
        ("legacy_ldap", "intranet_hub"): 5.0,
        ("intranet_hub", "dmz_mail"): 7.0,
        ("intranet_hub", "vpn_gateway"): 4.0,
        ("dmz_mail", "demarc"): 4.0,
        ("vpn_gateway", "demarc"): 4.0,
        ("demarc", "internet"): 9.0,
    }
    return FlowNetwork(nodes=nodes, edges=edges, capacity=capacity)


#: The canonical exfiltration capacity network (fixed constants).
DEFAULT_FLOW_NETWORK: FlowNetwork = _build_default_flow_network()

#: The exfiltration source (the registry holding the agent list).
EXFIL_SOURCE = "registry"

#: The exfiltration sink (the internet / adversary's collection point).
EXFIL_SINK = "internet"


def analyze_exfiltration(
    network: FlowNetwork = DEFAULT_FLOW_NETWORK,
    source: str = EXFIL_SOURCE,
    sink: str = EXFIL_SINK,
) -> dict[str, Any]:
    """Run the full exfiltration analysis: max flow + min-cut severance plan.

    Args:
        network: The capacitated network to analyze.
        source: Data source node.
        sink: Data sink node.

    Returns:
        A dict with ``max_flow``, ``min_cut_value``, ``cut_edges`` and
        ``severance``.
    """
    flow = edmonds_karp(network, source, sink)
    cut = min_cut_edges(network, source, sink)
    return {
        "max_flow": round(flow.value, 4),
        "min_cut_value": round(cut.value, 4),
        "cut_edges": cut.edges,
        "severance": severance_plan(cut),
    }
