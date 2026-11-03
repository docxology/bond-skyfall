# Skyfall — SILVA (PROJECT BOND mission package)

Skyfall (2012) · mission codename **SILVA**. A deterministic mission-software
package modeling the cyberattack on MI6, the exfiltration of the NATO agent
list, the legacy-system exposure audit, the patch schedule, and the Skyfall
estate defense plan. Implements the frozen BOND-API `MissionProvider` contract.

## Film → software mapping

The film is the spec; the code is the implementation. Six threat surfaces from
the 2012 story, each posed as a problem with an exact deterministic answer.

| In the film | As a computation |
| --- | --- |
| Silva reaches MI6's deepest systems through aging, poorly-segmented connections | Directed-graph reachability: enumerate every simple intrusion path, find the minimum-hop and minimum-difficulty routes |
| The NATO agent list is exfiltrated in a burst | Change-point detection: residualize the daily traffic rhythm, then run a two-sided CUSUM control chart |
| The transfer has to be cut off | Max-flow / min-cut: the smallest link set whose severance stops the outward flow |
| MI6 still runs on infrastructure built for an older threat | Weighted multi-factor exposure scoring across an aging fleet, aggregated to a fleet risk |
| The backlog cannot all be fixed at once | Greedy severity-first scheduling under a daily patching budget |
| The confrontation moves to the Skyfall estate | Articulation-point (choke-point) analysis of the approach graph plus defender assignment; flood-fill topology of Silva's island hideout |

## Modules

| Module | Concept | Algorithms |
| --- | --- | --- |
| `src/skyfall/cyber_ops.py` | Cyberattack on MI6 (network intrusion paths) | DFS simple-path enumeration, BFS shortest, Dijkstra cheapest, per-hop survival simulation |
| `src/skyfall/traffic_analysis.py` | Agent-list exfiltration burst detection | Periodic-baseline residualization, two-sided CUSUM, EWMA, two-segment change-point likelihood |
| `src/skyfall/exfiltration.py` | Severing the outward transfer | Edmonds–Karp max-flow, residual-graph min cut, severance plan |
| `src/skyfall/legacy_audit.py` | Legacy-system vulnerability audit | Shared four-factor risk model, weighted exposure score, fleet tiers, greedy budgeted remediation |
| `src/skyfall/patch_strategy.py` | Legacy patch scheduling | Greedy severity-first scheduling under a daily budget, cumulative severity-day exposure |
| `src/skyfall/estate_defense.py` | Island hideout topology + estate choke-point defense | Flood-fill island topology, iterative Tarjan articulation points, defender assignment |
| `src/skyfall/mission.py` | BOND-API `MissionProvider` adapter (`SILVA`) | Five-stage lifecycle + six-gadget registry |
| `src/skyfall/manuscript_variables.py` | Manuscript token hydration | Deterministic metrics derived from the domain core |
| `src/skyfall/figures/` | Estate-defense map + traffic-detection chart | Deterministic matplotlib (Agg), byte-identical PNGs |

The six domain modules import nothing from `bond_api` — they are stdlib-only
and usable standalone. `mission.py` is the sole protocol adapter.

## MissionProvider surface

`src/skyfall/mission.py` exposes the frozen contract the rest of the BOND
fleet consumes:

```python
from bond_api.protocol import ReconRequest
from skyfall.mission import MissionProvider, register_gadgets

provider = MissionProvider()                        # zero-arg; discovery uses this form
brief    = provider.brief()                         # -> bond_api.protocol.MissionBrief
report   = provider.recon(ReconRequest(goal="..."))  # -> ReconReport
plan     = provider.plan(brief)                     # -> MissionPlan
outcome  = provider.execute(plan)                   # -> MissionOutcome (carries Provenance)
debrief  = provider.debrief(outcome)                # -> Debrief
```

`register_gadgets(registry)` binds six gadgets under the `skyfall` slug:
`intrusion_analyzer`, `traffic_detector`, `severance_planner`,
`legacy_auditor`, `patch_scheduler`, `estate_planner`. Module path, class name,
method names, and gadget names are all part of the frozen surface — see
[`docs/architecture.md`](docs/architecture.md).

`MissionProvider` also accepts a keyword-only `network=` override; it defaults
to the canonical MI6 network, so discovery is unaffected.

## Install and run

```bash
cd bond-skyfall
uv sync --extra dev

uv run python scripts/run_mission.py {brief|recon|plan|execute|debrief|all} [--json]
uv run python scripts/00_preflight.py skyfall
uv run python scripts/z_generate_manuscript_variables.py
```

`uv sync` works in a standalone clone: `[tool.uv.sources]` points `bond-api` at
the vendored copy under `vendor/bond-api`, whose bytes are recorded in
`vendor/bond-api/PROVENANCE.json` and checked by `scripts/vendor.py`. The six
domain modules are stdlib-only; only `mission.py` and `tests/test_mission.py`
need `bond_api`:

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Gates

All three must pass before any claim that the package is done.

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
```

Coverage is enforced as a floor rather than advertised as a figure: the run
prints the live number and fails below 90% on line *and* branch coverage.

`ruff check` takes its rule selection from the PROJECT BOND suite root — this
package ships no `[tool.ruff]` and inherits `line-length = 120` from there — so
a standalone clone must point ruff at the suite's settings; `ruff format
--check --line-length 120` is the portable half of that gate.

## Reproducible outcomes

Fixed inputs, no random draws, and no wall clock — the build stamp comes from
the committed `paper.date` config field, so running the generator twice writes
byte-identical trees under `output/` (on a fixed interpreter; `PYTHON_VERSION`
is the one environment field the artifacts carry). Every outcome below is
asserted by the test suite and injected into the manuscript as a token, so
prose cannot drift from the code:

- Entry `internet` → target `registry`: six simple intrusion paths; the
  minimum-hop and minimum-difficulty routes coincide, and both avoid the
  expensive legacy-directory pivot.
- Traffic detector: the exfiltration burst is caught at the first hour of the
  burst window, and the independent maximum-likelihood change point agrees.
- Severance: max flow equals min cut; the plan cuts two egress links. The
  equality is pinned across an enumerated family of networks, not just this one.
- Legacy fleet of five systems audited to a critical fleet risk; the patch
  schedule clears the whole backlog and removes most of the cumulative exposure.
- Three estate choke points, fully covered by the four-defender team.

Run `uv run python scripts/z_generate_manuscript_variables.py` and read
`output/data/manuscript_variables.json` for the exact values on your checkout.

## Documentation

| Path | Contents |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Package identity, threat surfaces, protocol integration, reproducibility |
| [`TODO.md`](TODO.md) | Remaining work and declared-but-unbound integration points |
| [`docs/`](docs/) | Architecture, agent instructions, testing philosophy |
| [`manuscript/`](manuscript/) | The scientific write-up; every metric token-injected |

## Repository

Canonical remote: <https://github.com/docxology/bond-skyfall> (`origin`, default
branch `main`). Commit inside this package only — never reach into a sibling
BOND package.
