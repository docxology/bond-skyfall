# Methodology

## Network intrusion model (`skyfall.cyber_ops`)

The MI6 HQ network is a directed graph `G = (V, E)` of `{{SILVA_NUM_NETWORK_NODES}}`
nodes (hosts and routing segments). An adversary enters at `{{SILVA_ENTRY}}`
and seeks the high-value target `{{SILVA_TARGET}}`. Three reachability
questions are answered deterministically:

* **Simple-path enumeration** — a depth-first search over the directed graph
  enumerates every simple path from entry to target, bounding search by never
  revisiting a node. There are `{{SILVA_NUM_INTRUSION_PATHS}}` such paths.
* **Minimum-hop path** — breadth-first search from the entry returns a
  shortest path ({{SILVA_SHORTEST_HOPS}} hops).
* **Minimum-difficulty path** — Dijkstra's algorithm over per-edge traversal
  costs ({{SILVA_CHEAPEST_HOPS}} hops) finds the route that is least costly in
  aggregate, which need not be the shortest.

Each node carries an exposure in `[0, 1]`; the probability an intrusion
traverses a path uncontained is the product over hops of
`base_survival × (1 − exposure(dest))`. A step simulation walks the chosen
path hop-by-hop and reports whether it exceeds a containment budget.

## Legacy exposure model (`skyfall.legacy_audit`)

Each legacy system contributes four normalized risk factors — age
(`min(age/25, 1)`), unpatched share (`1 − patch_level`), protocol vintage
(`min(era/3, 1)`), and open-service surface (`min(services/6, 1)`) — combined
linearly with weights 0.25 / 0.35 / 0.20 / 0.20 into a scalar exposure in
`[0, 1]`. A fleet audit aggregates mean/max exposure, counts risk tiers, and
returns an overall fleet-risk label. Remediation is a deterministic greedy
descent: each pass patches the system whose dominant risk factor offers the
largest exposure reduction, under a fixed budget of `3` actions
(targets: {{SILVA_REMEDIATION_TARGETS}}).

## Estate defense model (`skyfall.estate_defense`)

The Skyfall estate approach is an undirected graph of positions connected by
roads/trails. **Articulation points** (cut vertices) — found with an iterative
Tarjan DFS — are positions whose removal disconnects the graph: the estate's
**choke points**, through which every route from the moors to the mansion must
pass. There are `{{SILVA_NUM_CHOKE_POINTS}}` choke points
({{SILVA_CHOKE_POINTS}}). A defense plan assigns the finite defending team
(`{{SILVA_NUM_DEFENDERS}}` defenders) to the highest-degree choke points first,
reporting any that remain uncovered (coverage {{SILVA_COVERAGE}}).

Silva's island hideout is a passable cell grid with a single beachhead; a
flood fill computes the reachable area, the perimeter, and the farthest
reachable cell — the hideout — whose BFS distance ({{SILVA_ISLAND_CORRIDOR}}
cells) is the contested approach corridor.
