# src/ — Skyfall (SILVA) source tree

## Layout

| Module | Role | Imports bond_api? |
| --- | --- | --- |
| `skyfall/cyber_ops.py` | Pure domain: network intrusion paths | No |
| `skyfall/legacy_audit.py` | Pure domain: legacy exposure audit | No |
| `skyfall/estate_defense.py` | Pure domain: island + estate defense | No |
| `skyfall/mission.py` | Protocol adapter: `MissionProvider` | Yes |
| `skyfall/manuscript_variables.py` | `{{TOKEN}}` hydration | (via mission) |
| `skyfall/figures/` | Deterministic estate-defense figure | (via mission) |

## Boundary rule

The pure domain modules must never import `bond_api` or `infrastructure`.
`mission.py` is the only seam to the frozen protocol. Keeping the core
standalone means it remains usable even if the bond-api path dependency is
unavailable.
