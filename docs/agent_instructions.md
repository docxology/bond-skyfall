# Agent Instructions — skyfall (SILVA)

Read this before modifying the package. These are hard constraints, not
suggestions; violations fail the gates.

## Hard rules

1. **Scope is this package only.** Work inside
   `projects/working/bond/skyfall/`. Never touch a sibling BOND package, the
   bond root files, or the template repo.
2. **Local-only.** There is no remote. Never push. Commit inside this package
   with path-scoped commits.
3. **Zero mocks.** No `unittest.mock`, `MagicMock`, `mocker.patch`, or
   `create_autospec` anywhere in `tests/`. Real data and real computation only.
   See `testing_philosophy.md` for the real-boundary substitutes.
4. **Coverage above the floor.** `uv run pytest tests/ --cov=src
   --cov-fail-under=90` measures line *and* branch coverage on `src/`. Do not
   quote a percentage in prose — cite the gate and let the run produce the
   number. No source module is omitted from the measurement; do not add an
   `omit` entry for anything but test files (a blanket `*/__init__.py` omit
   previously hid `figures/__init__.py` from every reported total).
5. **Deterministic.** Fixed inputs, no RNG, and no wall clock in any persisted
   artifact — not in a metric, not in a build label. The build stamp
   `SILVA_BUILD_DATE` comes from the committed `paper.date` field of
   `manuscript/config.yaml`. Never render `datetime.now()` into
   `output/`: two runs of the generator must produce byte-identical trees, and
   `TestRegenerationIsByteIdentical` will turn red if they do not.
6. **The pure domain core must not import `bond_api`.** `cyber_ops`,
   `traffic_analysis`, `exfiltration`, `legacy_audit`, `patch_strategy`, and
   `estate_defense` are standalone. `mission.py` is the only protocol adapter.
   The `skyfall` facade must not eagerly import `mission` — doing so breaks the
   isolation test.
7. **Thin orchestrators.** Business logic lives in `src/`; `scripts/` do argv
   shaping and forwarding, nothing else.
8. **Manuscript metrics are injected.** Never hand-author a derived number in
   prose. Add the variable to `src/skyfall/manuscript_variables.py`, reference
   the token, and regenerate. The reverse-direction scanner will fail the suite
   on a bare numeral in the results narrative.
9. **No lineage strings.** `rg "template[_]code_project" .` must return nothing
   in source; bracket-split the pattern in any doc that has to mention the gate.
10. **Type hints, ruff, and mypy clean** on `src/`, `scripts/`, and `tests/`.

## The frozen protocol surface

`bond-cli`, the coordinator's reconcile, and the orchestrator consume these
across packages. Changing any of them breaks discovery for the whole fleet:

- module path `skyfall.mission`, class name `MissionProvider`, zero-argument
  construction, and the module-level `provider` instance;
- the five stage methods `brief` / `recon` / `plan` / `execute` / `debrief`
  with their protocol return types;
- `register_gadgets(registry)` and the six gadget names
  (`intrusion_analyzer`, `traffic_detector`, `severance_planner`,
  `legacy_auditor`, `patch_scheduler`, `estate_planner`).

Deepen **inside** the package — new modules, richer mission internals, extra
result keys, extra gadgets. Never rename or remove what is listed above. An
optional keyword-only constructor argument is acceptable (that is how the
network override was added) because `MissionProvider()` still works.

## Working the change

1. Read `architecture.md` for where the code belongs.
2. Write the test first and **watch it fail**. If it passes before your change,
   it is not testing your change.
3. Implement in `src/`, with type hints and a docstring stating what the
   function guarantees.
4. If you added or changed a number that appears in the manuscript, add or
   update the token — never edit the prose figure directly.
5. Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`.
6. Run all three gates.
7. Update `README.md`, `AGENTS.md`, and `TODO.md` if the change alters what the
   package does or what remains to be done. Delete completed TODO items rather
   than leaving stale "next steps".

## Traps this package has already hit

- **A theorem asserted only on the canonical case.** The max-flow min-cut check
  passed on the acyclic default network while the underlying reachability walk
  was wrong. If you assert a universal property, enumerate a family and pin the
  family's size.
- **A documented tie-break that compared one character.** The remediation
  ranker's ordering silently depended on dict insertion order. If a docstring
  claims a total order, test that reordering the input does not change the
  output.
- **Guards that cannot fire.** Three were deleted (a re-check behind a
  dataclass validator, twice; an `inf`-sentinel branch). They read as coverage
  while providing none. If a guard is genuinely wanted, give it a testable seam
  instead — see `require_reachable()` and `MissionProvider(network=...)`.
- **Prose drift.** A methodology sentence cited the exfiltration-window token
  where it meant the baseline window, rendering a factually wrong parenthetical.
  Check that a token means what the sentence around it says.

## Verification checklist

```bash
cd projects/working/bond/skyfall
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/00_preflight.py skyfall
uv run python scripts/z_generate_manuscript_variables.py
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # must be clean after your commit
```

If `uv` reports `Failed to initialize cache`, that is a sandbox restriction, not
a package failure — re-run with the sandbox disabled.
