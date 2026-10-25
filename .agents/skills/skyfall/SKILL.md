---
name: skyfall
description: Skyfall (2012) SILVA mission package — cyber intrusion paths, legacy exposure audit, estate choke-point defense, BOND-API MissionProvider.
version: 0.1.0
author: docxology
license: MIT
tags: [bond, film, mission, cyber-ops, legacy-audit, estate-defense, thin-orchestrator]
---

# skyfall

Project-scoped skill for this BOND film package. Load this when working inside
the project.

## When to Use

- Working inside the `skyfall` package — running the mission, editing the
  domain core, or regenerating manuscript/tokens/figure.
- Verifying the BOND guardrails hold after changes (see the shared preamble).

## Quick Reference

```bash
cd bond-skyfall
uv sync --extra dev
uv run python scripts/run_mission.py all --json          # five-stage SILVA run
uv run python scripts/00_preflight.py skyfall             # discovery/protocol check
uv run python scripts/z_generate_manuscript_variables.py  # tokens + figure
uv run pytest tests/ --cov=src --cov-fail-under=90        # zero-mock >90% gate
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
```

## Domain core

- `src/skyfall/cyber_ops.py` — network intrusion paths: DFS enumeration, BFS
  shortest, Dijkstra cheapest, per-hop survival simulation.
- `src/skyfall/traffic_analysis.py` — periodic-baseline CUSUM change-point
  detection of the exfiltration burst (+ EWMA, change-point likelihood).
- `src/skyfall/exfiltration.py` — Edmonds–Karp max-flow and min-cut severance.
- `src/skyfall/legacy_audit.py` — closed-form exposure score, fleet audit,
  greedy remediation.
- `src/skyfall/patch_strategy.py` — greedy severity-first patch scheduling,
  cumulative-exposure reduction.
- `src/skyfall/estate_defense.py` — island flood-fill topology, Tarjan
  articulation (choke) points, defender assignment.
- `src/skyfall/mission.py` — the BOND-API `MissionProvider` adapter (film
  `skyfall`, codename `SILVA`) + `register_gadgets` (six gadgets). The facade
  does NOT eagerly import mission, so pure modules load without bond_api.

## Pitfalls

- The six domain modules (`cyber_ops`, `traffic_analysis`, `exfiltration`,
  `legacy_audit`, `patch_strategy`, `estate_defense`) must **not** import
  `bond_api`; only `mission.py` (and manuscript/figures) bind to the protocol,
  and the `skyfall` facade stays eager-free so pure imports leave zero
  `bond_api` loaded.
- Run `uv sync --extra dev` after editing `pyproject.toml` before pytest.
- After `ruff check`, run `ruff format` (format --check flags otherwise).
- Manuscript metrics are `{{VARIABLE}}`-injected, never hand-authored.
- `output/` is git-ignored (regenerable).
- No mocks; fixed scenario constants; no wall-clock in persisted metrics.

## Cross-refs

- Project contract: [`AGENTS.md`](../../../AGENTS.md)
- README: [`README.md`](../../../README.md)
- TODO: [`TODO.md`](../../../TODO.md)
