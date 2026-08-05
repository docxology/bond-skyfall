# docs/ — skyfall (SILVA) documentation

Agent- and human-facing documentation for the **skyfall** mission package
(film: Skyfall, 2012 · codename **SILVA**), one film package in the PROJECT
BOND suite. This directory explains how the package is built, how to work
inside it safely, and why its tests are shaped the way they are. It does not
duplicate the manuscript: `manuscript/` is the scientific write-up, `docs/` is
the engineering contract.

## What is here

| File | Read it when |
| --- | --- |
| `README.md` (this file) | You want the map and the commands. |
| `agent_instructions.md` | Before you modify anything — hard constraints, verification checklist, and the traps this package has already fallen into. |
| `architecture.md` | You need the module-by-module layout, the dependency direction, and exactly how `mission.py` satisfies the frozen `bond_api` `MissionProvider`. |
| `testing_philosophy.md` | You are adding or changing a test, or wondering why a passing suite is not the same as a correct one. |
| `AGENTS.md` | You want the one-screen constraint summary. |

## Related documents outside this directory

| Path | Contents |
| --- | --- |
| `../README.md` | Package overview, module table, reproducible outcomes. |
| `../AGENTS.md` | Package identity, threat-surface descriptions, protocol integration. |
| `../TODO.md` | Remaining work and declared-but-unbound integration points. |
| `../manuscript/` | The scientific write-up; every metric token-injected. |
| `../src/AGENTS.md`, `../tests/AGENTS.md`, `../scripts/AGENTS.md` | Per-directory rules. |

## The package in one paragraph

Skyfall (2012) dramatizes one adversary reaching MI6's deepest systems through
a chain of aging, poorly-segmented connections, exfiltrating the NATO agent
list, and forcing a final confrontation at the Skyfall estate. This package
turns that narrative into six well-posed, deterministic computational problems
— intrusion-path enumeration, traffic change-point detection, max-flow/min-cut
severance, legacy exposure auditing, patch scheduling, and choke-point defense
planning — each with a real algorithm, real fixed data, and no randomness.

## Commands

```bash
cd projects/working/bond/skyfall
uv sync --extra dev

# Gates. All three must pass before any claim of "done".
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# Run the mission.
uv run python scripts/run_mission.py all --json
uv run python scripts/00_preflight.py skyfall

# Regenerate manuscript tokens, the resolved section tree, and both figures.
uv run python scripts/z_generate_manuscript_variables.py
```

`uv` cannot write its cache under a restrictive sandbox. A `Failed to
initialize cache` error is an environment restriction, not a package failure —
re-run with the sandbox disabled.

## Local-only

This is a PROJECT BOND working tree. There is no git remote and nothing is ever
pushed. Commit inside this package only.
