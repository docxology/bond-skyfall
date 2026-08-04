# Testing Philosophy — skyfall (SILVA)

## Zero-Mock Policy

Every test exercises real algorithms and real data. No `unittest.mock`,
`MagicMock`, `mocker.patch`, or `create_autospec`. Coverage is enforced via
`pyproject.toml` (`--cov=src --cov-fail-under=90`).

## Test inventory

| File | Covers | Style |
| --- | --- | --- |
| `test_cyber_ops.py` | Network, path enumeration, BFS/Dijkstra, probability, simulation | real graph fixtures |
| `test_legacy_audit.py` | LegacySystem, exposure score, fleet audit, remediation | closed-form checks |
| `test_estate_defense.py` | IslandGrid, topology, choke points, defense plan, coverage | grid/graph fixtures |
| `test_mission.py` | MissionProvider lifecycle, protocol, gadgets | real provider |
| `test_manuscript_variables.py` | token map, resolve tree, live cross-ref gate | real config + sections |
| `test_figures.py` | deterministic PNG rendering | real matplotlib (Agg) |
| `test_scripts_smoke.py` | CLI subprocess runs | `sys.executable` + `cwd=root` |

## Determinism

- Fixed scenario constants (network, fleet, estate, island) — nothing varies.
- No RNG draws; `SILVA_SEED` recorded only in provenance.
- Figure PNGs are asserted byte-identical across runs.
- The live manuscript-token cross-reference test ties sections to generated
  variables.

## Running

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```
