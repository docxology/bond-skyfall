# Software and Scenario

## Package identity

- **Package**: skyfall ({{SILVA_TITLE}})
- **Codename**: {{SILVA_CODENAME}}
- **Package version**: {{SILVA_VERSION}} · mission version {{SILVA_MISSION_VERSION}}
- **Deterministic seed**: {{SILVA_SEED}}
- **Python**: {{PYTHON_VERSION}} · generated {{GENERATION_TIMESTAMP}}

## Scenario configuration

The scenario is fixed so results are reproducible. Every parameter below is a
named constant in `src/skyfall/`, surfaced here as an injected token rather
than transcribed by hand.

| Parameter | Value | Source constant |
| --- | --- | --- |
| Entry host | `{{SILVA_ENTRY}}` | `cyber_ops.DEFAULT_ENTRY` |
| Target | `{{SILVA_TARGET}}` | `cyber_ops.DEFAULT_TARGET` |
| Network size | {{SILVA_NUM_NETWORK_NODES}} nodes | `cyber_ops.DEFAULT_NETWORK` |
| Per-hop survival baseline | {{SILVA_BASE_SURVIVAL}} | `cyber_ops.DEFAULT_BASE_SURVIVAL` |
| Containment budget | {{SILVA_CONTAINMENT_HOPS}} hops | `cyber_ops.DEFAULT_CONTAINMENT_HOPS` |
| Traffic series | {{SILVA_TRAFFIC_SAMPLES}} hourly samples | `traffic_analysis.DEFAULT_TRAFFIC` |
| Baseline window / period | {{SILVA_BASELINE_WINDOW}} / {{SILVA_TRAFFIC_PERIOD}} hours | `traffic_analysis.DEFAULT_BASELINE_WINDOW`, `DEFAULT_PERIOD` |
| CUSUM allowance / interval | {{SILVA_CUSUM_K}} / {{SILVA_CUSUM_H}} | `traffic_analysis.DEFAULT_CUSUM_K`, `DEFAULT_CUSUM_H` |
| Exfiltration network | {{SILVA_NUM_FLOW_NODES}} nodes | `exfiltration.DEFAULT_FLOW_NETWORK` |
| Legacy fleet | {{SILVA_FLEET_SIZE}} systems | `legacy_audit.default_legacy_fleet` |
| Exposure weights | {{SILVA_EXPOSURE_WEIGHTS}} | `legacy_audit.EXPOSURE_WEIGHTS` |
| Exposure saturation scales | {{SILVA_EXPOSURE_SCALES}} | `legacy_audit.EXPOSURE_SCALES` |
| Remediation budget | {{SILVA_REMEDIATION_BUDGET}} actions | `mission.REMEDIATION_BUDGET` |
| Patch horizon / daily budget | {{SILVA_HORIZON_DAYS}} days / {{SILVA_DAILY_BUDGET}} | `patch_strategy.DEFAULT_HORIZON_DAYS`, `DEFAULT_DAILY_BUDGET` |
| Estate | {{SILVA_NUM_ESTATE_POSITIONS}} positions | `estate_defense.DEFAULT_ESTATE` |
| Defending team | {{SILVA_NUM_DEFENDERS}} call signs | `mission.DEFENDERS` |

## Running the mission

From the package directory:

```bash
uv sync --extra dev
uv run python scripts/run_mission.py all --json      # full five-stage run
uv run python scripts/00_preflight.py skyfall         # discovery/protocol check
uv run python scripts/z_generate_manuscript_variables.py  # hydrate tokens + figure
uv run pytest tests/ --cov=src --cov-fail-under=90    # zero-mock gate
```

The pure domain modules (`skyfall.cyber_ops`, `skyfall.traffic_analysis`,
`skyfall.exfiltration`, `skyfall.legacy_audit`, `skyfall.patch_strategy`,
`skyfall.estate_defense`) import nothing from `bond_api` and remain usable in
isolation if the path dependency is ever unavailable; `skyfall.mission` is the
thin adapter to the frozen protocol.
