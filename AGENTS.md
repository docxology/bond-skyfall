# Skyfall — SILVA (PROJECT BOND film package)

## Identity

- **Film**: Skyfall (2012)
- **Mission codename**: SILVA
- **Slug**: `skyfall`
- **Package**: `src/skyfall/`

## What this package does

The SILVA mission models six linked threat surfaces from the 2012 film,
each as a real, deterministic computational problem:

1. **Cyberattack on MI6 simulation — network intrusion paths**
   (`src/skyfall/cyber_ops.py`): the HQ network as a directed graph; simple
   intrusion-path enumeration (DFS), minimum-hop reachability (BFS),
   minimum-difficulty reachability (Dijkstra), and a per-hop survival
   simulation of a chosen path.
2. **Traffic change-point detection** (`src/skyfall/traffic_analysis.py`):
   the agent-list exfiltration burst caught by a periodic-baseline CUSUM
   control chart (with EWMA smoothing and change-point likelihood).
3. **Exfiltration severance** (`src/skyfall/exfiltration.py`): the outward
   data transfer as a capacitated flow — Edmonds–Karp max-flow plus the
   min-cut severance plan.
4. **Legacy-system vulnerability audit — aging-infrastructure exposure**
   (`src/skyfall/legacy_audit.py`): closed-form per-system exposure scores
   (age, patch level, protocol vintage, open services), fleet aggregation and
   risk-tiering, and prioritized, budgeted remediation.
5. **Patch scheduling** (`src/skyfall/patch_strategy.py`): a deterministic
   greedy scheduler that spends a daily patching budget on the highest-
   severity known vulnerabilities, minimizing cumulative fleet exposure.
6. **Island hideout topology + estate defense plan — Skyfall choke points**
   (`src/skyfall/estate_defense.py`): flood-fill island reachability /
   perimeter / hideout, Tarjan articulation (choke) points of the estate
   approach graph, and defender assignment for full choke-point coverage.

## Protocol integration

`src/skyfall/mission.py` implements the frozen `bond_api.MissionProvider`
contract (film `skyfall`, codename `SILVA`) and `register_gadgets()` binds six
gadgets (intrusion / traffic / severance / audit / patch / estate) into
`bond_api.registry.GadgetRegistry`. The orchestration discovery convention
expects this module importable as `skyfall.mission` exposing
`MissionProvider`, which it does. Stage-by-stage detail, and the exact list of
what may not change, are in `docs/architecture.md`.

`MissionProvider.execute()` reports `success` honestly: it is `True` only when
the primary objective could actually be modelled. A provider bound to a network
in which the target is unreachable returns `success=False` with an explicit
`"unreachable"` verdict rather than a well-formed outcome wrapping a stub.

The pure domain modules import nothing from `bond_api` — they are standalone
(stdlib + math only), so the film's core remains usable even if the path
dependency is unavailable. `mission.py` is the thin protocol adapter, and the
`skyfall` facade deliberately does not eagerly import it (see `src/AGENTS.md`);
a subprocess test enforces that.

## Build, test, verify

```bash
cd bond-skyfall
uv sync --extra dev          # requires the PROJECT BOND suite checkout

# Gates — all three must pass.
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# Protocol + artifact checks.
uv run python scripts/00_preflight.py skyfall
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py all --json

# Hygiene.
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short
```

Coverage is a floor (90%, line + branch on `src/`), not an advertised figure —
run the gate for the live number rather than trusting one quoted in prose. A
`Failed to initialize cache` error from `uv` is a sandbox restriction, not a
package failure; re-run with the sandbox disabled.

## Reproducibility

- Fixed scenario constants: the MI6 network, traffic series, exfiltration flow
  network, legacy fleet, vulnerability backlog, estate graph, and island grid
  are hardcoded and never vary.
- No random draws; `SILVA_SEED = 11` is recorded only in provenance, and the
  provenance test asserts it.
- No wall clock in any persisted artifact. The build stamp `SILVA_BUILD_DATE`
  is read from the committed `paper.date` field of `manuscript/config.yaml`;
  nothing calls `datetime.now()`.
- Two full runs of `scripts/z_generate_manuscript_variables.py`, with real time
  passing between them, write byte-identical trees under `output/` — asserted
  by `TestRegenerationIsByteIdentical`, which runs the real script twice rather
  than injecting a fixed clock. The scope is a fixed interpreter:
  `PYTHON_VERSION` is injected into the setup section, so a different Python
  changes that one field.
- Both figures render byte-identically across runs, asserted by comparing bytes
  from two renders.
- Every manuscript metric is injected from `manuscript_variables.py`; the suite
  fails on an unresolved token *and* on a bare numeral in the results prose.

## Repository

Canonical remote: `https://github.com/docxology/bond-skyfall`, branch `main`.
Commit your own work inside this package only — never a sibling BOND package.
`uv sync` resolves `bond-api` from the vendored copy at `vendor/bond-api`, so it works
outside the suite checkout; see `README.md`.
