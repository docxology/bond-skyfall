# Reproducibility

## Determinism guarantees

Every metric in this manuscript is deterministic by construction:

- **Fixed inputs**: the MI6 network, legacy fleet, estate graph, and island
  grid are hardcoded constants; nothing varies between runs.
- **No randomness**: the mission draws no random numbers; `{{SILVA_SEED}}` is
  recorded solely in provenance.
- **No wall-clock in metrics**: the only time-dependent token is
  `GENERATION_TIMESTAMP` ({{GENERATION_TIMESTAMP}}), which labels the build and
  does not enter any result.

## Verification gates

| Gate | Command | Status |
| --- | --- | --- |
| Coverage ≥ 90% | `uv run pytest tests/ --cov=src --cov-fail-under=90` | enforced |
| No mocks | `rg "MagicMock\|\|mocker\|create_autospec" tests/` | clean |
| Protocol purity | domain modules import no `bond_api` | enforced |
| Lineage | `rg "template[_]code_project" .` | zero |

The manuscript's variable-token values are produced by
`skyfall.manuscript_variables.generate_variables()` and cross-checked by a
live test that every token used in the numbered sections exists in the
generated map.
