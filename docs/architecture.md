# Architecture — skyfall (SILVA)

## Layer topology

The package is four concentric layers. Dependencies point strictly inward;
nothing in an inner layer knows an outer layer exists.

| Layer | Modules | Responsibility | Imports `bond_api`? |
| --- | --- | --- | --- |
| **0 · Pure domain core** | `cyber_ops`, `traffic_analysis`, `exfiltration`, `legacy_audit`, `patch_strategy`, `estate_defense` | Graph, statistical, and scheduling algorithms over fixed real data | **No** — stdlib + `math` only |
| **1 · Protocol adapter** | `mission.py` | Implements the frozen `bond_api` `MissionProvider`; registers gadgets | Yes |
| **2 · Presentation** | `manuscript_variables.py`, `figures/` | Token hydration and deterministic matplotlib rendering | Transitively, via `mission` |
| **3 · Orchestrators** | `scripts/run_mission.py`, `scripts/00_preflight.py`, `scripts/z_generate_manuscript_variables.py` | Thin CLIs — argv shaping and forwarding only | Yes |

The Layer-0 purity is a tested invariant, not a convention:
`tests/test_mission.py::TestPureCoreIsolation` runs a fresh subprocess that
imports every domain module and asserts `bond_api` is absent from
`sys.modules`. This is why `skyfall/__init__.py` imports the six domain modules
but deliberately does **not** import `mission` — an eager facade import would
pull the protocol into every consumer and silently break the guarantee. The
discovery contract imports `skyfall.mission` directly and never goes through
the facade.

## Module by module

### `cyber_ops.py` — the intrusion model

Models the MI6 HQ network as a directed graph of hosts and routing segments.

- `Node` / `Network` / `IntrusionPath` — frozen dataclasses; `Network`
  validates that every edge endpoint is a known node and every edge cost is
  positive.
- `build_network()` — constructs a `Network` from an explicit node iterable
  plus an adjacency map, implicitly creating any node named only in `edges`.
- `intrusion_paths()` — depth-first enumeration of **every simple path** from
  entry to target; neighbours are visited in sorted order, so the result is
  stable, and a visited-set bounds the search on cyclic graphs.
- `shortest_intrusion_path()` — BFS minimum-hop route.
- `cheapest_intrusion_path()` — Dijkstra over `Network.hop_cost`, discarding
  stale heap entries when a node is re-reached more cheaply.
- `path_success_probability()` — product over hops of
  `base_survival × (1 − exposure(dest))`.
- `simulate_intrusion()` — hop-by-hop walk returning cumulative survival, a
  containment verdict, and the hop count.
- `DEFAULT_NETWORK`, `DEFAULT_ENTRY`, `DEFAULT_TARGET`,
  `DEFAULT_BASE_SURVIVAL`, `DEFAULT_CONTAINMENT_HOPS` — the frozen scenario.
  The last two are named constants precisely so the manuscript can cite them as
  tokens instead of hand-authoring the values.

### `traffic_analysis.py` — the exfiltration detector

HQ traffic follows a daily rhythm, so a naive CUSUM alarms on the rhythm
itself. The pipeline residualizes first.

- `periodic_baseline()` — per-phase (hour-of-day) means over a clean
  pre-incident window.
- `detrend()` — subtracts that baseline, leaving a zero-mean residual series.
- `baseline_statistics()` — population mean and standard deviation of the
  residual baseline window.
- `cusum_series()` / `cusum_detection()` — Page's two-sided cumulative-sum
  control chart; the alarm is the first index where either accumulation
  crosses the decision interval `h`.
- `ewma_series()` — exponentially weighted moving average of the residuals.
- `change_point_likelihood()` — O(n) two-segment normal likelihood split,
  locating the single most likely change point independently of the CUSUM.
- `analyze_traffic()` — runs the whole pipeline, returning a frozen
  `TrafficReport`.

### `exfiltration.py` — containment as a min cut

- `edmonds_karp()` — max flow via BFS augmenting paths, pushing each path's
  exact bottleneck.
- `min_cut_edges()` — the minimum cut separating source from sink. Residual
  reachability is walked over the **residual graph including reverse arcs**;
  a forward-only walk under-approximates the source side and can report a cut
  larger than the max flow. This was a real defect in this module, and it is
  now pinned by an enumerated sweep rather than by the canonical scenario.
- `severance_plan()` — renders the cut as ordered `sever <src> -> <dst>`
  directives.
- `analyze_exfiltration()` — the full analysis over `DEFAULT_FLOW_NETWORK`.

### `legacy_audit.py` — aging-infrastructure exposure

- `risk_factors()` — the four normalized factors (age, unpatched share,
  protocol vintage, open-service surface), saturating per `EXPOSURE_SCALES`.
  **Single definition**, consumed by both the score and the ranker so the two
  cannot disagree about the model.
- `exposure_score()` — the `EXPOSURE_WEIGHTS`-weighted sum of those factors.
- `_tier()` / `EXPOSURE_THRESHOLDS` — tier assignment; the open-ended top tier
  is returned by falling out of the loop rather than by an unreachable
  sentinel comparison.
- `audit_fleet()` → `FleetAudit` — per-system scores, tier membership and
  counts, mean/max exposure, critical count, and a coarse `risk()` label.
- `prioritize_remediation()` — greedy descent picking the system whose dominant
  *weighted* factor offers the largest reduction, ties broken on the **whole**
  system id so the ranking does not depend on fleet insertion order.

### `patch_strategy.py` — scheduling the backlog

- `Vulnerability` — id, system, severity, discovery day, patch effort.
- `fleet_exposure()` — cumulative severity-days with no patching.
- `schedule_patches()` — greedy: each day spends the daily budget on the
  highest-severity already-discovered unpatched vulnerabilities, ties broken
  lexicographically by id.
- `exposure_with_schedule()` — severity-days accrued until each patch lands.
- `reduction()` → `PatchSummary` — schedule versus the no-patching baseline.
- `analyze_patch_schedule()` — the canonical run.

### `estate_defense.py` — physical defense

- `IslandGrid` / `island_topology()` — flood fill over a passable cell grid
  with a single beachhead, returning reachable cells, perimeter, the hideout
  (farthest reachable cell), and the corridor length.
- `EstateGraph` — undirected approach graph. Road symmetry is **enforced at
  construction**: Tarjan's search assumes undirected adjacency, so a one-sided
  road would yield a plausible-but-wrong choke-point set rather than an error.
- `choke_points()` — iterative Tarjan articulation-point search with explicit
  stacks (no recursion depth limit), returning sorted cut vertices.
- `estate_defense_plan()` / `defense_coverage()` — assigns defenders to the
  highest-degree choke points first and reports any left uncovered.

### `manuscript_variables.py` and `figures/`

`generate_variables()` computes the full token map from the domain modules plus
`manuscript/config.yaml`; `resolve_manuscript_tree()` copies each `NN_*.md`
section into `output/manuscript/` with tokens substituted, failing in strict
mode on any leftover brace. `require_reachable()` is the strict-mode gate,
extracted as its own function so it can be tested directly rather than sitting
as a branch no test could enter.

`figures/` renders the estate-defense map and the traffic detection chart
headlessly (Agg) with fixed styling, so both PNGs are byte-identical across
runs — a property the test suite asserts by rendering twice and comparing
bytes.

## How `mission.py` implements the frozen `MissionProvider`

`bond_api.protocol.MissionProvider` is a `@runtime_checkable` structural
Protocol: any object exposing the five stage methods with matching signatures
satisfies it. `skyfall.mission.MissionProvider` is a plain class — it does not
inherit from the protocol — and `tests/test_mission.py` asserts
`isinstance(provider, ProtocolProvider)` so the structural match is verified
rather than assumed.

`bond_api.discovery.load_provider(slug, search_paths=[src])` imports
`<slug>.mission` and instantiates the top-level name `MissionProvider`. Three
things must therefore stay stable, and they are what "the frozen surface"
means: the module path `skyfall.mission`, the class name `MissionProvider`,
and zero-argument construction. The class also carries `film = "skyfall"` and a
module-level `provider` instance.

| Stage | Returns | What SILVA does |
| --- | --- | --- |
| `brief()` | `MissionBrief` | Declares codename `SILVA`, six objectives (intrude, detect, cut, audit, patch, defend), five `Asset`s sized from the live domain data, and two `Constraint`s (determinism, purity). |
| `recon(ReconRequest)` | `ReconReport` | Eight `Finding`s: entry, target, simple-path count, burst window, fleet size, patch backlog, choke-point count, and the caller's goal echoed back. |
| `plan(MissionBrief)` | `MissionPlan` | Six `Step`s, one per threat surface, each naming the domain function it will invoke and its parameters. |
| `execute(MissionPlan)` | `MissionOutcome` | Runs all six analyses against the real domain modules and packs them into `results` under `intrusion` / `detection` / `severance` / `legacy` / `patch_schedule` / `estate`, with a `Provenance` carrying the package version, `SILVA_SEED`, a SHA-256 `input_hash` over the frozen inputs (see below), and `wall_time_s = 0.0` (no wall-clock enters a persisted metric). |
| `debrief(MissionOutcome)` | `Debrief` | Five standing lessons, plus up to three conditional lessons appended when coverage is incomplete, the burst went undetected, or the patch schedule cleared less than half the backlog exposure. |

Three design points worth knowing before you edit:

- **`input_hash` is total over the inputs, and that is enforced.**
  `_scenario_payload()` writes out *every field of every input record* the
  execute stage consumes — node names, roles and exposures, every edge and
  edge cost, entry and target, estate positions and roads, the island grid
  cells, the flow network's nodes, edges, capacities and terminals, every
  legacy system's age / patch level / protocol era / open services /
  classification, every vulnerability's severity, discovery day and effort,
  all 240 traffic samples, the defender call signs, and the named scalar knobs
  (base survival, containment hops, baseline window, CUSUM `k` and `h`, period,
  daily budget, horizon, exfil window, remediation budget, seed). Floats are
  rendered with `repr`, which round-trips exactly. It hashes the network the
  provider is actually bound to, not `DEFAULT_NETWORK` unconditionally.
  An earlier version hashed only identifier *sets* plus four scalars: changing
  a node's exposure or adding +1000 to every traffic sample moved the reported
  results while leaving the digest identical. `TestInputHashSensitivity` in
  `tests/test_mission.py` now mutates one field at a time — sixteen distinct
  fields — and asserts the digest changes, with a same-inputs-same-digest
  positive control. Reverting the payload to the old identifier-set form turns
  sixteen of those nineteen tests red.

- **`execute` reports honest success.** `MissionOutcome.success` reflects
  whether the primary objective could actually be modelled. It used to be
  hard-coded `True`, which meant an unreachable target still produced a
  well-formed outcome carrying a stubbed simulation — a consumer had no way to
  tell the analysis never ran.
- **The network is injectable, keyword-only.**
  `MissionProvider(*, network: Network | None = None)` defaults to
  `DEFAULT_NETWORK`, so `MissionProvider()` — the form discovery uses — is
  unchanged. The override exists so the degraded path can be exercised by a
  real network instead of being left as an untestable fallback.

`register_gadgets(registry)` binds six deterministic zero-argument callables
under the `skyfall` slug: `intrusion_analyzer`, `traffic_detector`,
`severance_planner`, `legacy_auditor`, `patch_scheduler`, `estate_planner`.
The orchestrator looks these up by name, so **the names are part of the frozen
surface** — add gadgets freely, but do not rename or remove one.

## Dependency direction

```
scripts/  →  skyfall.mission  →  pure domain core
                   ↑                     ↑
      skyfall.manuscript_variables, skyfall.figures
```

Nothing imports upward. The pure core can be lifted into any Python
environment and imported without `bond_api` present.

## Adding a capability

1. Add the algorithm to the relevant pure module (or a new Layer-0 module),
   with full type hints, a docstring, and no randomness.
2. Write the zero-mock test **first**, and confirm it fails before the
   implementation exists.
3. Surface it through `mission.py` (a result key, a gadget) and/or
   `manuscript_variables.py` (a token) as needed — never break the frozen
   surface.
4. Add a figure only if it earns one; keep it deterministic.
5. Regenerate the manuscript tree and figures, then run all three gates.
6. Keep `scripts/` as glue.
