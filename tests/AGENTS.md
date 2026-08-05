# tests/ — Skyfall test suite

Zero-mock, deterministic tests over real data and computation, targeting
≥90% line+branch coverage on `src/`.

| File | Covers |
| --- | --- |
| `test_cyber_ops.py` | network, paths, BFS/Dijkstra, probability, simulation |
| `test_traffic_analysis.py` | periodic baseline, CUSUM, EWMA, change-point likelihood |
| `test_exfiltration.py` | max-flow, min-cut, severance plan |
| `test_legacy_audit.py` | exposure score, fleet audit, remediation |
| `test_patch_strategy.py` | cumulative exposure, greedy schedule, reduction |
| `test_estate_defense.py` | island topology, choke points, defense plan |
| `test_mission.py` | MissionProvider lifecycle, protocol, gadgets, pure-core isolation |
| `test_manuscript_variables.py` | token map, resolve tree, live cross-ref gate |
| `test_figures.py` | deterministic PNG rendering (estate + traffic) |
| `test_scripts_smoke.py` | CLI subprocess runs |

`conftest.py` pins `MPLBACKEND=Agg` and adds `src/` to `sys.path`.

Run: `uv run pytest tests/ --cov=src --cov-fail-under=90`
