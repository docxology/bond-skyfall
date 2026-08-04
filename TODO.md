# TODO — skyfall (SILVA)

## Built (phase 2)

- **Cyber ops** (`src/skyfall/cyber_ops.py`): MI6 HQ directed-graph model,
  simple-path enumeration, BFS shortest path, Dijkstra cheapest path,
  per-hop survival simulation. Real data (fixed `DEFAULT_NETWORK`).
- **Legacy audit** (`src/skyfall/legacy_audit.py`): closed-form exposure score
  (age/patch/protocol/surface), fleet aggregation + risk tiers, greedy
  budgeted remediation. Real data (fixed `default_legacy_fleet()`).
- **Estate defense** (`src/skyfall/estate_defense.py`): island flood-fill
  topology (reachable/perimeter/hideout), Tarjan articulation (choke) points,
  defender assignment + coverage. Real data (fixed `DEFAULT_ESTATE`,
  `default_island()`).
- **Protocol adapter** (`src/skyfall/mission.py`): frozen `bond_api`
  `MissionProvider` (film `skyfall`, codename `SILVA`), five-stage lifecycle,
  `register_gadgets()`.
- **Manuscript + figures**: `manuscript_variables.py` `{{TOKEN}}` hydration;
  deterministic estate-defense figure (`figures/`).
- Thin scripts: `run_mission.py`, `00_preflight.py`,
  `z_generate_manuscript_variables.py`.

## Declared integration points (not yet bound)

- **bond-utilities provenance**: `bond_utilities.mission_io.record_provenance_outcome`
  is declared as a dev dependency and is importable; the mission currently
  carries its own in-protocol `Provenance` (per the frozen `bond_api`
  `MissionOutcome`). **Acceptance**: when a suite-level orchestrator expects
  outcome persistence via `bond_utilities.mission_io`, add a thin
  `persist_outcome()` call in `mission.py`/a script and re-verify determinism.
- **Orchestrator discovery**: the package already satisfies
  `bond_api.discovery` (`skyfall.mission` + `MissionProvider`). **Acceptance**:
  run `scripts/00_preflight.py skyfall` and have `bond-orchestrator` discover
  `skyfall` from its `src/`; nothing further required in-repo.

## Not implemented (deliberately out of scope)

- Live/stochastic intrusion simulation (would break determinism).
- Physical estate simulation (would break determinism and add deps).

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
```
