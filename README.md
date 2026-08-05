# Skyfall — SILVA (PROJECT BOND mission package)

Skyfall (2012) · mission codename **SILVA**. A deterministic mission-software
package modeling the cyberattack on MI6, the legacy-system exposure audit, the
patch schedule, and the Skyfall estate defense plan. Implements the frozen
BOND-API `MissionProvider` contract.

## Modules

| Module | Concept | Algorithms |
| --- | --- | --- |
| `src/skyfall/cyber_ops.py` | Cyberattack on MI6 (network intrusion paths) | DFS path enum, BFS shortest, Dijkstra cheapest, per-hop survival sim |
| `src/skyfall/traffic_analysis.py` | Exfiltration burst detection | periodic-baseline CUSUM, EWMA, change-point likelihood |
| `src/skyfall/exfiltration.py` | Agent-list severance | Edmonds–Karp max-flow, min-cut |
| `src/skyfall/legacy_audit.py` | Legacy-system vulnerability audit | closed-form exposure score, fleet tiers, greedy remediation |
| `src/skyfall/patch_strategy.py` | Legacy patch scheduling | greedy severity-first scheduling, cumulative exposure |
| `src/skyfall/estate_defense.py` | Island hideout topology + Skyfall choke-point defense | flood-fill island, Tarjan articulation points, defender assignment |
| `src/skyfall/mission.py` | BOND-API `MissionProvider` adapter (`SILVA`) | six-stage lifecycle + gadgets |
| `src/skyfall/manuscript_variables.py` | `{{TOKEN}}` hydration | deterministic metrics from domain core |
| `src/skyfall/figures/` | Estate + traffic figures | deterministic matplotlib (Agg) |

## Scripts

```bash
uv run python scripts/run_mission.py {brief|recon|plan|execute|debrief|all} [--json]
uv run python scripts/00_preflight.py skyfall
uv run python scripts/z_generate_manuscript_variables.py
```

## Reproducible outcomes

- Entry `internet` → target `registry`: 6 simple intrusion paths, 5 min-hop,
  deterministic survival probabilities.
- Traffic detector: burst detected at hour 180 (window 180–189), max CUSUM
  127.6.
- Severance: max flow = min cut = 8.0; cut the two egress links.
- Legacy fleet of 5 systems; patch schedule clears 12 vulnerabilities with an
  89% exposure reduction.
- 3 estate choke points; coverage 1.00 with the 4-defender team.

## Local-only

No remote. Commit inside this package only. See `AGENTS.md` for the guardrails
and `docs/` for agent instructions.
