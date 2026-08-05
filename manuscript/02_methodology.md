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
`base_survival × (1 − exposure(dest))`, with a baseline survival of
{{SILVA_BASE_SURVIVAL}} per hop. A step simulation walks the chosen path
hop-by-hop and reports whether it exceeds the containment budget of
{{SILVA_CONTAINMENT_HOPS}} hops.

## Traffic change-point detection (`skyfall.traffic_analysis`)

HQ traffic follows a daily rhythm, so a naive CUSUM on the raw series
false-alarms on the rhythm itself. Over a {{SILVA_TRAFFIC_SAMPLES}}-hour
series, the detector first estimates a per-phase baseline :math:`\bar{x}_h`
across a period of {{SILVA_TRAFFIC_PERIOD}} hours, fitted on the clean
pre-incident window of the leading {{SILVA_BASELINE_WINDOW}} hours. It
subtracts that baseline to leave a zero-mean residual series, then runs the
two-sided CUSUM control chart of Page (1954):

:math:`S_t^+ = \max(0, S_{t-1}^+ + z_t - k), \quad S_t^- = \max(0, S_{t-1}^- - z_t - k)`

with :math:`z_t` the standardized residual, the allowance
:math:`k = {{SILVA_CUSUM_K}}`, and the decision interval
:math:`h = {{SILVA_CUSUM_H}}`. An alarm fires the first time either side
exceeds :math:`h`. The burst ({{SILVA_EXFIL_WINDOW}}) is detected at hour
{{SILVA_ALARM_INDEX}}, with a peak accumulation of {{SILVA_MAX_CUSUM}}
standardized units. :func:`change_point_likelihood` additionally locates the
most likely single change point by maximizing the two-segment normal
likelihood split (hour {{SILVA_BEST_CHANGE_POINT}}).

## Exfiltration severance (`skyfall.exfiltration`)

The outward transfer of the agent list is a capacitated flow problem on a
{{SILVA_NUM_FLOW_NODES}}-node projection of the HQ network. :func:`edmonds_karp`
computes the maximum exfiltration rate from the registry (source) to the
internet (sink) via BFS augmenting paths, pushing each path's exact
bottleneck. :func:`min_cut_edges` then finds the minimum cut separating source
from sink — the smallest link set that must be severed.

Residual reachability is walked over the **residual** graph, which includes the
reverse arcs induced by pushed flow, not merely the original forward edges.
That distinction is load-bearing rather than pedantic: a forward-only walk
under-approximates the source side of the cut whenever flow enters that side
from an unreached node, and the reported cut then exceeds the max flow,
breaking the very theorem the routine relies on. With the residual walk, the
cut value equals the max flow (both {{SILVA_MAX_FLOW}}) on every network, and
the property is pinned by an enumerated sweep rather than by the canonical
scenario alone. The severance plan is {{SILVA_SEVERANCE}}.

## Legacy exposure model (`skyfall.legacy_audit`)

Each legacy system contributes four normalized risk factors — age
(`min(age/age_scale, 1)`), unpatched share (`1 − patch_level`), protocol
vintage (`min(era/era_scale, 1)`), and open-service surface
(`min(services/service_scale, 1)`), saturating at
{{SILVA_EXPOSURE_SCALES}} respectively — combined linearly with weights
{{SILVA_EXPOSURE_WEIGHTS}} (age / unpatched / protocol / surface) into a
scalar exposure in `[0, 1]`. The factor model is defined once, in
:func:`risk_factors`, and consumed by both the score and the remediation
ranker so the two cannot disagree.

A fleet audit aggregates mean/max exposure, counts risk tiers, and returns an
overall fleet-risk label. Remediation is a deterministic greedy descent: each
pass patches the system whose dominant weighted risk factor offers the largest
exposure reduction — ties broken by the whole system id, so the ranking does
not depend on fleet insertion order — under a fixed budget of
{{SILVA_REMEDIATION_BUDGET}} actions (targets:
{{SILVA_REMEDIATION_TARGETS}}).

## Patch scheduling (`skyfall.patch_strategy`)

The maintenance layer schedules the {{SILVA_NUM_VULNERABILITIES}} known
vulnerabilities under a daily budget of {{SILVA_DAILY_BUDGET}} patch over a
{{SILVA_HORIZON_DAYS}}-day horizon. A deterministic greedy scheduler spends
each day's budget on the already-discovered, highest-severity unpatched
vulnerabilities (ties broken by id), and cumulative exposure is the
severity-days accrued until each patch lands. Against a no-patching baseline
of {{SILVA_PATCH_BASELINE}} severity-days, the schedule reduces exposure to
{{SILVA_PATCH_SCHEDULED}} — a {{SILVA_PATCH_REDUCTION}} reduction.

## Estate defense model (`skyfall.estate_defense`)

The Skyfall estate approach is an undirected graph of
{{SILVA_NUM_ESTATE_POSITIONS}} positions connected by roads/trails. The
undirected invariant is enforced at construction — a one-sided road would make
Tarjan's search report a plausible but wrong choke-point set rather than an
error, which is the worst possible failure mode for a defensive plan.

**Articulation points** (cut vertices) — found with an iterative Tarjan DFS —
are positions whose removal disconnects the graph: the estate's **choke
points**, through which every route from the moors to the mansion must pass.
There are `{{SILVA_NUM_CHOKE_POINTS}}` choke points ({{SILVA_CHOKE_POINTS}}).
A defense plan assigns the finite defending team (`{{SILVA_NUM_DEFENDERS}}`
defenders) to the highest-degree choke points first, reporting any that remain
uncovered ({{SILVA_DEFENDERS_USED}} posted, coverage {{SILVA_COVERAGE}}).

Silva's island hideout is a passable cell grid with a single beachhead; a
flood fill computes the reachable area ({{SILVA_ISLAND_REACHABLE}} cells), the
perimeter ({{SILVA_ISLAND_PERIMETER}}), and the farthest reachable cell — the
hideout — whose BFS distance ({{SILVA_ISLAND_CORRIDOR}} cells) is the
contested approach corridor.
