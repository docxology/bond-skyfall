# TODO — skyfall (SILVA)

Live remaining work only. Completed items are described in `README.md` and
`docs/architecture.md`, not carried here as a changelog.

## Open

### Declared-but-unbound integration points

- **bond-utilities provenance persistence.**
  `bond_utilities.mission_io.record_provenance_outcome` is declared as a dev
  dependency and is importable, but nothing in this package calls it: the
  mission carries its own in-protocol `Provenance` (per the frozen `bond_api`
  `MissionOutcome`) and never writes it anywhere durable.
  **Acceptance**: when a suite-level orchestrator requires outcome
  persistence, add a thin `persist_outcome()` call in `mission.py` or a script,
  assert the persisted payload is byte-identical across two runs, and confirm
  no wall-clock enters the persisted record.

- **Orchestrator round-trip.** The package satisfies `bond_api.discovery`
  locally (`scripts/00_preflight.py skyfall` passes), but discovery has not
  been exercised *from* `bond-orchestrator` against this `src/`.
  **Acceptance**: `bond-orchestrator` discovers `skyfall`, runs the five stages,
  and looks up all six gadgets by name. Nothing further should be required
  in-repo; if something is, it is a defect in the frozen surface and belongs
  in `docs/architecture.md`.

### Modelling gaps worth closing

- **Exfiltration network duplicates the intrusion topology by hand.**
  `exfiltration._build_default_flow_network()` restates the node set and
  adjacency of `cyber_ops.DEFAULT_NETWORK` as literals. The two are consistent
  today but nothing enforces it, so an edit to one can silently desynchronize
  the other. **Acceptance**: either derive the flow network from the intrusion
  network, or add a test asserting the node sets and edge directions agree.

- **Patch scheduling ignores per-system coupling.** `patch_strategy` treats
  vulnerabilities as independent, so patching two flaws on the same legacy
  system costs two full budget units. Real maintenance windows amortize.
  **Acceptance**: a per-system batching discount with a test showing the
  schedule changes, and the manuscript updated via tokens.

- **Estate defense ranks choke points by degree alone.** Betweenness would be
  the better centrality for "how much traffic must pass through here", and the
  current tie-break is lexicographic. **Acceptance**: a betweenness-ranked
  variant, a test distinguishing the two rankings on a graph where they differ,
  and a documented reason for whichever becomes the default.

## Deliberately out of scope

These are not gaps; they are boundaries the reproducibility guarantee sets.
Do not "fix" them.

- Live or stochastic intrusion / exfiltration simulation — would break
  determinism.
- Physical simulation of the estate — would break determinism and add
  dependencies.
- Adaptive (non-periodic) change-point detection beyond the two-segment
  likelihood.
- Empirically calibrated exposure or severity weights. The scoring model is
  stated, scoped, and cited as a *model*; presenting it as a measurement of
  real infrastructure would be an overclaim.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/00_preflight.py skyfall
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
```
