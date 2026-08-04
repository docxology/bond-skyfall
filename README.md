# Skyfall — SILVA (PROJECT BOND mission package)

Skyfall (2012) · mission codename **SILVA**. A deterministic mission-software
package modeling the cyberattack on MI6, the legacy-system exposure audit,
and the Skyfall estate defense plan. Implements the frozen BOND-API
`MissionProvider` contract.

## Modules

| Module | Concept | Algorithms |
| --- | --- | --- |
| `src/skyfall/cyber_ops.py` | Cyberattack on MI6 (network intrusion paths) | DFS path enum, BFS shortest, Dijkstra cheapest, per-hop survival sim |
| `src/skyfall/legacy_audit.py` | Legacy-system vulnerability audit | closed-form exposure score, fleet tiers, greedy remediation |
| `src/skyfall/estate_defense.py` | Island hideout topology + Skyfall choke-point defense | flood-fill island, Tarjan articulation points, defender assignment |
| `src/skyfall/mission.py` | BOND-API `MissionProvider` adapter (`SILVA`) | five-stage lifecycle + gadgets |
| `src/skyfall/manuscript_variables.py` | `{{TOKEN}}` hydration | deterministic metrics from domain core |
| `src/skyfall/figures/` | Estate defense figure | deterministic matplotlib (Agg) |

## Scripts

```bash
uv run python scripts/run_mission.py {brief|recon|plan|execute|debrief|all} [--json]
uv run python scripts/00_preflight.py skyfall
uv run python scripts/z_generate_manuscript_variables.py
```

## Reproducible outcomes

- Entry `internet` → target `registry`: 6 simple intrusion paths, 5 min-hop,
  deterministic survival probabilities.
- Legacy fleet of 5 systems (mean exposure + tier counts in manuscript tokens).
- 3 estate choke points; coverage 1.00 with the 4-defender team.

## Local-only

No remote. Commit inside this package only. See `AGENTS.md` for the guardrails
and `docs/` for agent instructions.
