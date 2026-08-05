# Skyfall — SILVA (PROJECT BOND film package)

## Identity

- **Film**: Skyfall (2012)
- **Mission codename**: SILVA
- **Slug**: `skyfall`
- **Package**: `src/skyfall/`

## What this package does

The SILVA mission models six linked threat surfaces from the 2012 film,
each as a real, deterministic computational problem:

1. **Cyberattack on MI6 simulation — network intrusion paths**
   (`src/skyfall/cyber_ops.py`): the HQ network as a directed graph; simple
   intrusion-path enumeration (DFS), minimum-hop reachability (BFS),
   minimum-difficulty reachability (Dijkstra), and a per-hop survival
   simulation of a chosen path.
2. **Traffic change-point detection** (`src/skyfall/traffic_analysis.py`):
   the agent-list exfiltration burst caught by a periodic-baseline CUSUM
   control chart (with EWMA smoothing and change-point likelihood).
3. **Exfiltration severance** (`src/skyfall/exfiltration.py`): the outward
   data transfer as a capacitated flow — Edmonds–Karp max-flow plus the
   min-cut severance plan.
4. **Legacy-system vulnerability audit — aging-infrastructure exposure**
   (`src/skyfall/legacy_audit.py`): closed-form per-system exposure scores
   (age, patch level, protocol vintage, open services), fleet aggregation and
   risk-tiering, and prioritized, budgeted remediation.
5. **Patch scheduling** (`src/skyfall/patch_strategy.py`): a deterministic
   greedy scheduler that spends a daily patching budget on the highest-
   severity known vulnerabilities, minimizing cumulative fleet exposure.
6. **Island hideout topology + estate defense plan — Skyfall choke points**
   (`src/skyfall/estate_defense.py`): flood-fill island reachability /
   perimeter / hideout, Tarjan articulation (choke) points of the estate
   approach graph, and defender assignment for full choke-point coverage.

## Protocol integration

`src/skyfall/mission.py` implements the frozen `bond_api.MissionProvider`
contract (film `skyfall`, codename `SILVA`) and `register_gadgets()` binds six
gadgets (intrusion / traffic / severance / audit / patch / estate) into
`bond_api.registry.GadgetRegistry`. The orchestration discovery convention
expects this module importable as `skyfall.mission` exposing
`MissionProvider`, which it does.

The pure domain modules import nothing from `bond_api` — they are standalone
(stdlib + math only), so the film's core remains usable even if the path
dependency is unavailable. `mission.py` is the thin protocol adapter, and the
`skyfall` facade deliberately does not eagerly import it (see `src/AGENTS.md`).

## Reproducibility

- Fixed scenario constants: the MI6 network, legacy fleet, estate graph, and
  island grid are hardcoded and never vary.
- No random draws; `SILVA_SEED = 11` recorded only in provenance.
- No wall-clock in any persisted metric (the sole exception is
  `GENERATION_TIMESTAMP`, a build label).
- The flagship estate-defense figure renders byte-identically across runs.

## Local-only

This is a PROJECT BOND working tree — there is no remote and nothing is ever
pushed. Commit your own work inside this package only.
