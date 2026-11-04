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

## Round-2 (2026-08-06)

**Baseline (this session, before any change):** `uv run pytest tests/ --cov=src
--cov-fail-under=90` → **225 passed, 0 failed, 0 skipped; 100.00% coverage**
(996 stmts / 362 branches). `ruff check`, `ruff format --check` (30 files), and
`mypy src/ scripts/` (13 files) all clean; preflight OK.

### Hostile-review findings fixed (each with a regression test)

| # | Finding | Fix | Test evidence |
| --- | --- | --- | --- |
| R1 | **`traffic_analysis.cusum_detection` under-reported `max_cusum`.** It returned the *running* maximum the moment it fired, so on the canonical burst — which keeps accumulating through the whole 10-hour window — it reported "127.6" as the peak while the true series peak was 1281.8 at hour 190, out by an order of magnitude. | `max_cusum` is now the true peak over the whole series; the alarm index is unchanged. | `test_traffic_analysis.py::TestMaxCusumIsTheSeriesPeak` (peak == global CUSUM max; peak lands after the alarm; detection timing still 180). `SILVA_MAX_CUSUM` 127.6 → 1281.8. |
| R2 | **V1: the exfiltration flow topology was hand-copied from the intrusion network**, drift-by-eye with nothing enforcing it. | Added `exfiltration.cyber_flow_topology()` deriving flow nodes/edges from `cyber_ops.DEFAULT_NETWORK` (reverse, drop `field_terminal`); `DEFAULT_FLOW_NETWORK` topology is built from it. | `test_exfiltration.py::TestFlowTopologyDerived` (derived == canonical node & directed-edge set; leaf dropped; an intrusion-node addition propagates to the derived topology). `max_flow`/min-cut (8.0) unchanged. |
| R3 | **V2: figure byte-determinism was asserted only within one interpreter.** | Cross-interpreter hashseed byte-identity tests added. | `test_figures.py::TestHashSeedByteIdentity` renders each figure in two subprocesses under `PYTHONHASHSEED=1` and `=2` and compares bytes. |
| R4 | **V4: `bond-utilities` was a declared, unused dev dependency** (nothing imported it). | Dropped it from `pyproject.toml` dev extras and `[tool.uv.sources]`; lock regenerated. | `grep bond_utilities|bond-utilities src/ scripts/ tests/ pyproject.toml` → empty. |
| R5 | **E1: patch scheduling ignored per-system coupling** (two flaws on one box cost two full budget units). | Added `patch_strategy.schedule_patches_coupled()` / `analyze_patch_schedule_coupled()` (2nd+ patch on an open system charged `system_discount`); default unchanged. | `test_patch_strategy.py::TestScheduleCoupled` (uncoupled splits two same-system flaws across days, coupled closes them same-day; schedules differ; reduction improves; discount validation). |
| R6 | **E2: estate choke points ranked by degree alone** (blind to traffic-through). | Added `estate_defense.betweenness_centrality()` (Brandes) and a `rank="degree"\|"betweenness"` option on `estate_defense_plan`; default unchanged. | `test_estate_defense.py::TestBetweenness`/`TestDefenseRank` (degree ties by id on a path and covers `b`; betweenness ranks the real traffic centre `c`; unit-interval; canonical agreement). |

### Manuscript
Every metric is injected from `skyfall.manuscript_variables` (never
hand-authored); the forward live-token gate and the reverse bare-numeral gate
both pass. Deepened to cover the exfiltration-topology derivation (R2), the
coupling-aware scheduler (R5), betweenness choke-point ranking (R6), and honest
scope notes that the extensions are model parameters. Added Brandes (2001) to
`references.bib` / `99_references.md`. New tokens: `SILVA_NUM_FLOW_EDGES`,
`SILVA_COUPLED_PATCHED_COUNT` / `_SCHEDULED` / `_REDUCTION`,
`SILVA_COUPLING_DISCOUNT`, `SILVA_TOP_BETWEENNESS_CHOKE`,
`SILVA_ESTATE_RANKING_AGREES`; `SILVA_MAX_CUSUM` is now 1281.8. The generator
now resolves **68** tokens (was 60).

### Gates (final, this session)
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **251 passed, 0 skipped,
0 failed; TOTAL 1102 stmts / 418 branches / 0 miss; 100.00%** (was 225 / 996 /
362, +26 tests | +106 stmts | +56 branches). `ruff check` clean; `ruff format
--check` 30 files clean; `mypy src/ scripts/` clean (13 files);
`scripts/00_preflight.py skyfall` → `OK`; `scripts/run_mission.py all --json`
runs.

### Carried forward (needs other scope)
- **V3** (orchestrator round-trip) lives in `bond-orchestrator`, not this
  package — remains open.
- **D1** (`ROSTER.md` test count) is bond-root, generated by
  `_phase_gen_roster.py`; the live count is now **251** — carried.

## Open work


### Correctness

**None open.** Checked in the 2026-08-06 session: full suite green at 100.00%
line+branch; ruff, ruff-format and mypy clean at that head; preflight passes;
`git status --short` empty;
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
| V5 | **Nothing binds the ruff configuration the lint gate reads, and the vendoring changed it — four passages still described the old one.** The package now ships a `[tool.ruff]` table holding only `extend-exclude = ["vendor"]`; ruff selects the *nearest* configuration and does not merge a parent's, so `ruff check` runs on ruff's defaults where it previously inherited the suite root's `line-length = 120`. Measured 2026-11-04 with ruff 0.16.1, in two trees whose `pyproject.toml` carries the same table in the same place and differs only in its body: with `extend-exclude = ["vendor"]` the effective `line_length` is **88**, `ruff format --check` reports **20 of 32 files** and `ruff check` **41** findings; with the body replaced by `line-length = 120` the effective length is **120**, `ruff format --check` reports **1 file** (`scripts/vendor.py`, the fleet-identical checker conformed to ruff's defaults) and `ruff check` **38** findings — the whole difference is three `I001` findings. At `ed44889b0a`, with a `line-length = 120` table added to its own `pyproject.toml`, the same commands report **38** findings and **0 files** to reformat, so the shadowing leaves the check row red at the same total apart from those three sort findings and moves the format row from clean to 20 files. (A first version of this control put the 120 setting in a synthetic parent `pyproject.toml` instead; that arm also moved isort's project root and reported 45 findings with 21 `I001`, so it was discarded as an artifact — recorded here rather than quietly replaced.) Four passages stated the inheritance and the suite-path requirement as current — as they stood at `d11d04e`: `README.md:100-103`, `docs/README.md:63-71`, `docs/agent_instructions.md:108-113` and `TODO.md:199-201` — and all four are corrected in this change. **Decided 2026-11-04 (orchestrator):** the minimal table stays — re-cutting the 27 recorded vendoring payloads is not worth the frozen blobs — and `scripts/vendor.py`'s conformance to ruff's defaults is a **named exception**, because the checker ships byte-identical in every film package. **Command:** `uv run ruff format --check src/ scripts/ tests/`; `uv run ruff check src/ scripts/ tests/` |

### Toolchain

| # | Item |
| --- | --- |
| T1 | **`ruff check` and `ruff format --check` are red on `main`, and were red before the vendoring change.** Measured 2026-11-03: **41** findings on `src/ scripts/ tests/`, 26 of them auto-fixable (`RUF022`, `RUF100`, `I001`), and **20** files `ruff format` would reformat. The counts are identical at the baseline commit `ed44889b0a` and at the vendoring branch's head, so that change adds no debt to this red baseline and is not merged on a green gate. Both ends were measured under ruff's defaults; under the inherited `line-length = 120` (measured by putting that setting in the package's own `pyproject.toml`, V5) the pre-vendoring head reports **38** findings and **0** files to reformat, and that setting is no longer the one in force. `mypy src/ scripts/` is clean. **Done when:** a format pass lands as one mechanical commit, then the remaining findings are resolved one at a time, with an explicit `noqa` and a reason at the site for the semantic ones — `PLW1510` adds `check=` to `subprocess.run` calls and `TRY004` changes the exception type callers see, and neither belongs inside a dependency change. **Command:** `uv run ruff check src/ scripts/ tests/`; `uv run ruff format --check src/ scripts/ tests/` |

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
- **There is no wall clock in the package.** The former `GENERATION_TIMESTAMP`
  token called `datetime.now()` and was rendered into
  `output/manuscript/05_experimental_setup.md`,
  `output/manuscript/06_reproducibility.md`, and
  `output/data/manuscript_variables.json`, so no two regenerations produced the
  same bytes even though the docs claimed determinism — and the only test on it
  injected a fixed `now`, which is why the breach survived. It is replaced by
  `SILVA_BUILD_DATE`, read from the committed `paper.date` field of
  `manuscript/config.yaml` by `manuscript_build_date()`, and bound by
  `tests/test_manuscript_variables.py::TestRegenerationIsByteIdentical`, which
  runs the real generator script twice with real time passing between the runs.
  The byte-identity scope is a fixed interpreter, since `PYTHON_VERSION` is
  still injected into the setup section.
- **`../ROSTER.md` is not writable from here.** D1 records the drift; fixing it
  requires bond-root scope, which a standalone clone does not have. Every `../`
  path in this file refers to the PROJECT BOND monorepo the package was lifted
  from — not to this repository.

## Verification

Every gate, with its expected outcome on a clean checkout. If `uv` reports
`Failed to initialize cache`, that is a sandbox restriction, not a package
failure — re-run with the sandbox disabled.

```bash
cd bond-skyfall
uv sync --all-extras          # a bare `uv sync` prunes pytest

uv run pytest tests/ --cov=src --cov-fail-under=90
# → measured 2026-11-04: 252 passed; TOTAL 1102 stmts / 418 branches / 0 miss; 100.00%

uv run ruff check src/ scripts/ tests/
# → measured 2026-11-04: rc=1, 41 findings under the defaults this package reads
#   since the vendoring's table; 38 with line-length = 120 in that table's place,
#   and 38 at the pre-vendoring head under that setting (T1, V5)
uv run ruff format --check src/ scripts/ tests/
# → measured 2026-11-04: rc=1, 20 of 32 files would be reformatted; with
#   line-length = 120 in the table's place only scripts/vendor.py, and 0 files at
#   the pre-vendoring head under that setting (V5)
uv run mypy src/ scripts/
# → measured 2026-11-04: Success: no issues found in 14 source files

uv run python scripts/00_preflight.py skyfall
# → OK: skyfall discoverable, 5/5 provider methods bound, 11 protocol dataclasses

uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_mission.py all --json

rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short             # → empty
```

Coverage is enforced as a floor, not advertised as a figure: read the number the
run prints rather than trusting one quoted in prose, including this file's.

## Repository

Canonical remote `https://github.com/docxology/bond-skyfall`, branch `main`.
Commit inside this package only. The `uv` commands above run in a standalone
clone: `bond-api` resolves to the vendored copy at `vendor/bond-api`.
