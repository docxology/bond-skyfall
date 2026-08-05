# Testing Philosophy — skyfall (SILVA)

## Zero-Mock Policy

Every test exercises real algorithms and real data. No `unittest.mock`,
`MagicMock`, `mocker.patch`, or `create_autospec`. Coverage is enforced via
`pyproject.toml` (`--cov=src --cov-fail-under=90`).

## Test inventory

| File | Covers | Style |
| --- | --- | --- |
| `test_cyber_ops.py` | Network, path enumeration, BFS/Dijkstra, probability, simulation | real graph fixtures |
| `test_traffic_analysis.py` | periodic baseline, CUSUM, EWMA, change-point likelihood, canonical burst | real time-series fixtures |
| `test_exfiltration.py` | Edmonds-Karp max-flow, min-cut, theorem, severance plan | real capacity fixtures |
| `test_legacy_audit.py` | LegacySystem, exposure score, fleet audit, remediation | closed-form checks |
| `test_patch_strategy.py` | Vulnerability, cumulative exposure, greedy schedule, reduction | real backlog fixtures |
| `test_estate_defense.py` | IslandGrid, topology, choke points, defense plan, coverage | grid/graph fixtures |
| `test_mission.py` | MissionProvider lifecycle, protocol, gadgets, pure-core isolation | real provider + subprocess |
| `test_manuscript_variables.py` | token map, resolve tree, live cross-ref gate | real config + sections |
| `test_figures.py` | deterministic PNG rendering (estate + traffic) | real matplotlib (Agg) |
| `test_scripts_smoke.py` | CLI subprocess runs | `sys.executable` + `cwd=root` |

`conftest.py` pins `MPLBACKEND=Agg` and adds `src/` to `sys.path`. The pure-core
isolation test runs a fresh subprocess asserting that importing every domain
module leaves `bond_api` out of `sys.modules`.

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
