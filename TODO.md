# TODO — skyfall (SILVA)

Skyfall (2012) · mission codename **SILVA**. A deterministic, stdlib-only
mission package modelling six threat surfaces from the film — MI6 network
intrusion paths, agent-list exfiltration burst detection, max-flow/min-cut
severance, legacy-fleet exposure audit, budgeted patch scheduling, and estate
choke-point defense — behind the frozen `bond_api.MissionProvider` contract in
`src/skyfall/mission.py`.

**Verified state (measured 2026-08-05 on this checkout, commit `49b6b2058`):**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **217 passed,
100.00% coverage (996 statements, 362 branches, 0 missed) across all 10 source
modules**, including `src/skyfall/figures/__init__.py`. `ruff check`, `ruff
format --check` (30 files), and `mypy src/ scripts/` (13 files) are clean;
`scripts/00_preflight.py skyfall` reports `OK: skyfall discoverable, 5/5
provider methods bound, 11 protocol dataclasses`. Working tree clean.

Both findings in `../output/verify/skyfall.json` have been remediated and were
re-checked this session — they are **not** carried below:

- *Provenance overclaim.* `_scenario_payload()` (`src/skyfall/mission.py:115+`)
  now serialises every field of every input, and
  `tests/test_mission.py::TestInputHashSensitivity` mutates sixteen distinct
  fields plus a same-inputs positive control and a
  `test_production_hash_is_the_payload_digest` binding to the shipped call path.
- *Coverage omit laundering.* `pyproject.toml:45-54` no longer omits
  `*/__init__.py`; `src/skyfall/figures/__init__.py` measures 74/74 statements
  and 18/18 branches, so the previously-uncovered false arm of the
  `cusum_alarm_index` branch is now exercised.

## Open work

### Correctness

**None open.** Checked this session: full suite green at 100.00% line+branch;
ruff, ruff-format and mypy clean; preflight passes; `git status --short` empty;
both audit findings in `../output/verify/skyfall.json` re-verified as fixed in
code, not just in prose; the `manuscript/03_results.md` wording flagged as an
uncommitted third-party edit in `../output/verify/skyfall.unresolved.json` is
now committed (`518a2ec`) and is factually correct — `legacy_ldap` does carry
the highest `exposure` (0.9) in `cyber_ops.DEFAULT_NETWORK`
(`src/skyfall/cyber_ops.py:357`).

### Verification

Claims that hold today but are not bound by a test that can fail.

| # | Item |
| --- | --- |
| V1 | **The exfiltration flow network hand-restates the intrusion topology.** `_build_default_flow_network()` (`src/skyfall/exfiltration.py:250-289`) writes out its own node tuple and adjacency as literals; its docstring (`:254-255`) claims it "mirrors `skyfall.cyber_ops.DEFAULT_NETWORK`'s topology". It does — reversed, minus `field_terminal` — but nothing enforces it, and `tests/test_exfiltration.py` never imports `cyber_ops`, so editing one network silently desynchronises the other. **Done when:** either the flow network is derived from `cyber_ops.DEFAULT_NETWORK` (reverse the edges, drop the terminal leaf), or a test asserts node-set and edge-direction agreement *and* fails when a node is added to only one of the two. **Command:** `uv run pytest tests/test_exfiltration.py -k topology -v` |
| V2 | **Figure byte-determinism is asserted only within one interpreter.** `tests/test_figures.py:31-36` and `:56-61` render twice inside the same process, so any dependence on hash-randomised iteration order is invisible to them; `AGENTS.md:94-95` states the stronger cross-run claim. Manually confirmed today: two subprocesses at `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2` both produce `sha256 dc24fab1…5e3e97` for `render_estate_defense_figure`. **Done when:** a test renders each figure in two subprocesses with different `PYTHONHASHSEED` values and compares bytes. **Command:** `uv run pytest tests/test_figures.py -k hashseed -v` |
| V3 | **Orchestrator round-trip never exercised.** Discovery is verified only *locally*, from inside this package (`scripts/00_preflight.py:31`, `load_provider(slug, search_paths=[SRC])`). `bond-orchestrator` has never bound `skyfall`: it is absent from `../_omnibus/output_canonical/omnibus_report.json`, whose chain is `goldfinger → goldeneye → no_time_to_die`. **Done when:** `bond-orchestrator` discovers `skyfall`, runs all five stages, and looks up all six gadget names (`intrusion_analyzer`, `traffic_detector`, `severance_planner`, `legacy_auditor`, `patch_scheduler`, `estate_planner`). Nothing further should be needed in-repo; if it is, that is a defect in the frozen surface and belongs in `docs/architecture.md`. **Command:** run the orchestrator against this `src/` from `../bond-orchestrator`; then `uv run python scripts/00_preflight.py skyfall` must still pass unchanged. |
| V4 | **`bond-utilities` is a declared, unused dev dependency.** `pyproject.toml:31` requires `bond-utilities>=0.1.0` and `:36` pins its path, but `grep -rn bond_utilities src/ scripts/ tests/ docs/` returns nothing — the mission carries its own in-protocol `Provenance` (per the frozen `bond_api.MissionOutcome`) and never writes it anywhere durable. A declared dependency nothing imports is an unbound claim. **Done when:** either the dependency is dropped from `pyproject.toml`, or a `persist_outcome()` call exists (in `mission.py` or a script) with a test asserting the persisted payload is byte-identical across two runs and contains no wall-clock. **Command:** `grep -rn "bond_utilities" src/ scripts/ tests/` (non-empty, or the dep is gone from `pyproject.toml`), then `uv sync --all-extras && uv run pytest tests/ --cov=src --cov-fail-under=90` |

### Documentation

| # | Item |
| --- | --- |
| D1 | **`../ROSTER.md:52` carries a stale test count.** The bond-root roster records skyfall as `100.00% (197 tests)`. The coverage figure is correct and no longer laundered (the `omit` is gone), but the suite is **217** tests as of this session. The bond root is outside this package's write scope, so this cannot be fixed from here — it is carried over unresolved from `../output/verify/skyfall.unresolved.json`. **Done when:** row 23 of `../ROSTER.md` reads `100.00% (217 tests)`, or whatever a fresh run reports. **Command:** `cd .. && sed -n '52p' ROSTER.md` matches the tail of `cd skyfall && uv run pytest tests/ --cov=src --cov-fail-under=90`. |

### Extension

Genuine future work. Neither is a defect; both change modelled behaviour and
therefore change manuscript tokens.

| # | Item |
| --- | --- |
| E1 | **Patch scheduling ignores per-system coupling.** `schedule_patches()` (`src/skyfall/patch_strategy.py:143-156`) decrements `budget_left` by each vulnerability's full `patch_effort` independently, so two flaws on the same `system_id` cost two full budget units. Real maintenance windows amortise: the second patch on an already-open system is cheaper. **Done when:** a per-system batching discount exists, a test shows the produced schedule differs from the undiscounted one on a fleet with two flaws sharing a `system_id`, and the manuscript is updated through `manuscript_variables.py` tokens (never hand-edited). **Command:** `uv run pytest tests/test_patch_strategy.py -v && uv run python scripts/z_generate_manuscript_variables.py` |
| E2 | **Estate defense ranks choke points by degree alone.** `src/skyfall/estate_defense.py:302-303` ranks by `len(graph.neighbours(name))` with a lexicographic tie-break. Betweenness centrality is the better answer to "how much traffic must pass through here", which is the question the defender assignment is actually asking. **Done when:** a betweenness-ranked variant exists, a test distinguishes the two rankings on a graph where they disagree (a long path with a low-degree bridge), and whichever becomes the default has its reason recorded in `docs/architecture.md`. **Command:** `uv run pytest tests/test_estate_defense.py -k betweenness -v` |

## Known limitations (not bugs)

Boundaries the reproducibility guarantee sets, or scope the audit forced to be
stated honestly. Do not re-open these as defects.

- **No live or stochastic intrusion / exfiltration simulation.** Every result is
  closed-form or exhaustive over fixed inputs; a sampled simulation would break
  the determinism guarantee in `AGENTS.md:87-97`. The per-hop survival
  calculation is an analytic probability, not a Monte Carlo draw.
- **No physical simulation of the estate.** Same reason, plus it would add
  dependencies beyond stdlib + matplotlib.
- **Change-point detection is periodic-baseline CUSUM plus a two-segment
  likelihood.** Adaptive, non-periodic detectors are out of scope.
- **Exposure and severity weights are a stated model, not a measurement.** The
  four-factor scoring in `legacy_audit.py` is transparent and linear, and
  `manuscript/07_scope_and_related_work.md:13-15` scopes it explicitly as a
  model rather than a calibrated empirical risk estimate. Presenting it as a
  measurement of real infrastructure would be an overclaim — this is the
  softened form the scope pass settled on, and it is deliberate.
- **Figure byte-identity is version-scoped.** matplotlib writes its own version
  into PNG `Software` metadata, so byte-identity holds across runs on one
  installed matplotlib, not across upgrades. This is why the gate compares two
  renders rather than pinning a hash literal.
- **`GENERATION_TIMESTAMP` is the sole wall-clock in the package.** It is a
  build label and enters no computed result or persisted metric.
- **`../ROSTER.md` is not writable from here.** D1 records the drift; fixing it
  requires bond-root scope. Editing it from this package would violate the
  working boundary.

## Verification

Every gate, with its expected outcome on a clean checkout. If `uv` reports
`Failed to initialize cache`, that is a sandbox restriction, not a package
failure — re-run with the sandbox disabled.

```bash
cd projects/working/bond/skyfall
uv sync --all-extras          # a bare `uv sync` prunes pytest

uv run pytest tests/ --cov=src --cov-fail-under=90
# → 217 passed; TOTAL 996 stmts / 362 branches / 0 miss; 100.00%

uv run ruff check src/ scripts/ tests/
# → All checks passed!
uv run ruff format --check src/ scripts/ tests/
# → 30 files already formatted
uv run mypy src/ scripts/
# → Success: no issues found in 13 source files

uv run python scripts/00_preflight.py skyfall
# → OK: skyfall discoverable, 5/5 provider methods bound, 11 protocol dataclasses

uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py all --json

rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short             # → empty
```

Coverage is enforced as a floor, not advertised as a figure: read the number the
run prints rather than trusting one quoted in prose, including this file's.

## Local-only

PROJECT BOND working tree. No remote, nothing is ever pushed; commit inside this
package only.
