# src/ — Skyfall (SILVA) source tree

## Layout

| Module | Role | Imports bond_api? |
| --- | --- | --- |
| `skyfall/cyber_ops.py` | Pure domain: network intrusion paths | No |
| `skyfall/traffic_analysis.py` | Pure domain: CUSUM burst detection | No |
| `skyfall/exfiltration.py` | Pure domain: max-flow / min-cut severance | No |
| `skyfall/legacy_audit.py` | Pure domain: legacy exposure audit | No |
| `skyfall/patch_strategy.py` | Pure domain: patch scheduling | No |
| `skyfall/estate_defense.py` | Pure domain: island + estate defense | No |
| `skyfall/mission.py` | Protocol adapter: `MissionProvider` | Yes |
| `skyfall/manuscript_variables.py` | `{{TOKEN}}` hydration | (via mission) |
| `skyfall/figures/` | Deterministic estate + traffic figures | (via mission) |

## Boundary rule

The pure domain modules must never import `bond_api` or `infrastructure`.
`mission.py` is the only seam to the frozen protocol, and the `skyfall` facade
does NOT eagerly import it — so `import skyfall.cyber_ops` (or any pure module)
works with zero `bond_api` loaded, and the core stays usable even if the
bond-api path dependency is unavailable. Use
`from skyfall.mission import MissionProvider` when the provider is needed
(the discovery contract imports `skyfall.mission` directly and never goes
through the facade).
