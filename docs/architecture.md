# Architecture — skyfall (SILVA)

## Layers

| Layer | Module(s) | Responsibility | Imports bond_api? |
| --- | --- | --- | --- |
| Pure domain core | `skyfall/cyber_ops.py`, `skyfall/legacy_audit.py`, `skyfall/estate_defense.py` | Graph/scoring algorithms, real deterministic computation | No |
| Protocol adapter | `skyfall/mission.py` | Implements `bond_api` `MissionProvider`, registers gadgets | Yes |
| Manuscript | `skyfall/manuscript_variables.py`, `skyfall/figures/` | Token hydration + figure rendering | via mission |
| Orchestrators | `scripts/run_mission.py`, `scripts/00_preflight.py`, `scripts/z_generate_manuscript_variables.py` | Thin CLIs | Yes |
| Tests | `tests/` | Zero-mock, ≥90% coverage | Yes (mission tests) |

## Dependency direction

`scripts/` → `src/` → (pure core, no protocol). Nothing imports upward. The
pure domain core is fully standalone: it can be lifted into any Python
environment and imported without `bond_api`.

## Concept → module mapping

- **Network intrusion paths** (`cyber_ops.py`): DFS path enumeration, BFS
  shortest path, Dijkstra cheapest path, per-hop survival simulation.
- **Legacy vulnerability audit** (`legacy_audit.py`): closed-form exposure
  score (age/patch/protocol/surface), fleet aggregation, greedy remediation.
- **Island topology + estate defense** (`estate_defense.py`): flood-fill
  island reachability/perimeter/hideout, Tarjan articulation (choke) points,
  defender assignment.

## Adding a capability

Add the algorithm to the relevant pure module, expose it in
`mission.py`/`manuscript_variables.py` as needed, add a figure if it merits a
visual, write a zero-mock test, and regenerate the manuscript+tokens. Keep
`scripts/` as glue only.
