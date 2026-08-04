# Software and Scenario

## Package identity

- **Package**: skyfall ({{SILVA_TITLE}})
- **Codename**: {{SILVA_CODENAME}}
- **Package version**: {{SILVA_VERSION}} · mission version {{SILVA_MISSION_VERSION}}
- **Deterministic seed**: {{SILVA_SEED}}
- **Python**: {{PYTHON_VERSION}} · generated {{GENERATION_TIMESTAMP}}

## Scenario configuration

The scenario is fixed so results are reproducible: entry host
`{{SILVA_ENTRY}}`, target `{{SILVA_TARGET}}`, a defending team of
`{{SILVA_NUM_DEFENDERS}}` call signs, a remediation budget of three legacy
actions, per-hop survival baseline 0.8, and a containment budget of six hops.

## Running the mission

From the package directory:

```bash
uv sync --extra dev
uv run python scripts/run_mission.py all --json      # full five-stage run
uv run python scripts/00_preflight.py skyfall         # discovery/protocol check
uv run python scripts/z_generate_manuscript_variables.py  # hydrate tokens + figure
uv run pytest tests/ --cov=src --cov-fail-under=90    # zero-mock gate
```

The pure domain modules (`skyfall.cyber_ops`, `skyfall.legacy_audit`,
`skyfall.estate_defense`) import nothing from `bond_api` and remain usable in
isolation if the path dependency is ever unavailable; `skyfall.mission` is the
thin adapter to the frozen protocol.
