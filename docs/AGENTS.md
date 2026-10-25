# docs/ — Agent-Facing Documentation Hub

Index and constraint summary for the skyfall (SILVA) mission package docs.
Start with `agent_instructions.md`; this file is the one-screen version.

| File | Purpose |
| --- | --- |
| `README.md` | Map of the docs, package summary, verification commands |
| `agent_instructions.md` | Read-first behavioral rules, checklist, known traps |
| `architecture.md` | Module boundaries, dependency direction, the `MissionProvider` implementation |
| `testing_philosophy.md` | Zero-mock policy, test inventory, determinism, anti-vacuity doctrine |

## Core constraints

- **Scope is this package.** Never touch a sibling BOND package, the bond root
  files, or the template repo.
- **Published package.** Canonical remote `docxology/bond-skyfall`, branch
  `main`. Commit inside this package; never reach into the suite it was lifted
  from.
- **The pure domain core never imports `bond_api`.** `cyber_ops`,
  `traffic_analysis`, `exfiltration`, `legacy_audit`, `patch_strategy`, and
  `estate_defense` are stdlib-only. `mission.py` is the sole protocol adapter,
  and the `skyfall` facade deliberately does not eagerly import it.
- **`scripts/` are thin orchestrators.** Argv shaping and forwarding only;
  business logic lives in `src/`.
- **Manuscript metrics are injected**, never hand-authored. A bare numeral in
  the results narrative fails the suite.
- **Zero mocks. Deterministic. Coverage above the floor**
  (`--cov-fail-under=90`; run the gate for the live figure rather than trusting
  a number quoted in prose).
- **The protocol surface is frozen.** `mission.py` must keep exposing
  `MissionProvider` with `brief`/`recon`/`plan`/`execute`/`debrief`, plus
  `register_gadgets()` and the six gadget names. bond-cli, the coordinator, and
  the orchestrator consume them across packages. Deepen *inside* the package;
  never break discovery.

## The standing lesson

Two real defects in this package survived a fully green suite because every
test exercised only the canonical scenario, on which both bugs were invisible.
When you add a guarantee, add the test that would fail if the guarantee were
false — then confirm it actually fails before you make it pass. See
`testing_philosophy.md`.
