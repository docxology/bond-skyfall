# Agent Instructions — skyfall (SILVA)

Read this before modifying the package. These are hard constraints, not
suggestions; violations fail the project gates.

## Hard rules

1. **Scope = this package only.** Work inside
   `projects/working/bond/skyfall/`. Never touch sibling BOND packages, bond
   root files, or the template repo.
2. **Local-only.** There is no remote. Never push.
3. **Zero mocks.** No `unittest.mock`, `MagicMock`, `mocker.patch`,
   `create_autospec` anywhere in `tests/`. Real data + computation only.
4. **Coverage ≥ 90%** on `src/` (line + branch):
   `uv run pytest tests/ --cov=src --cov-fail-under=90`.
5. **Deterministic.** Fixed seeds; no untracked RNG; no wall-clock in
   persisted metrics (the sole exception is `GENERATION_TIMESTAMP`, a build
   label).
6. **Pure domain core.** `src/skyfall/cyber_ops.py`, `legacy_audit.py`,
   `estate_defense.py` must not import `bond_api`; they are standalone.
   `mission.py` (and manuscript/figures via it) is the protocol adapter.
7. **Thin orchestrators.** Business logic lives in `src/`; `scripts/` are thin
   CLIs (argv shaping + forwarding).
8. **Manuscript metrics are injected.** Never hand-author a derived number in
   prose; use `{{VARIABLE}}` tokens resolved by
   `scripts/z_generate_manuscript_variables.py`.
9. **No lineage strings.** `rg "template[_]code_project" .` must return zero
   in source; bracket-split the pattern in docs that reference the gate.
10. **Type hints + ruff + mypy clean** on `src/` and `scripts/`.

## Verification checklist (run before done)

```bash
cd projects/working/bond/skyfall
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # clean after commit
```

## Protocol integration

`src/skyfall/mission.py` exposes a `MissionProvider` class (film slug
`skyfall`, codename `SILVA`) implementing the frozen `bond_api` contract, and
`register_gadgets()` binds the film's gadgets into `bond_api.registry`.
Discovery imports `<slug>.mission` and instantiates `MissionProvider`.
