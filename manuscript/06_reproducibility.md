# Reproducibility

## Determinism guarantees

Every metric in this manuscript is deterministic by construction:

- **Fixed inputs**: the MI6 network, legacy fleet, estate graph, and island
  grid are hardcoded constants; nothing varies between runs.
- **No randomness**: the mission draws no random numbers; `{{SILVA_SEED}}` is
  recorded solely in provenance.
- **No wall clock anywhere in the artifacts**: no generated value is read from
  the clock. The build stamp `SILVA_BUILD_DATE` ({{SILVA_BUILD_DATE}}) is the
  committed `paper.date` field of `manuscript/config.yaml`, so it changes only
  when someone edits and commits that file.

Because of the last point the guarantee is byte-level, not merely
value-level: running `scripts/z_generate_manuscript_variables.py` twice writes
byte-identical `output/manuscript/*.md`, `output/data/manuscript_variables.json`,
and `output/figures/*.png`. The one environment input is the interpreter —
`PYTHON_VERSION` is injected into the setup section, so the byte-identity claim
is scoped to repeated runs on a fixed Python version, and a different
interpreter changes exactly that one field.

## Verification gates

| Gate | Command | What it asserts |
| --- | --- | --- |
| Coverage floor | `uv run pytest tests/ --cov=src --cov-fail-under=90` | line + branch coverage on `src/` stays at or above the floor; zero failures, zero skips |
| Byte-identical regeneration | `tests/test_manuscript_variables.py::TestRegenerationIsByteIdentical` | two full runs of the generator script, with real time passing between them, write byte-identical artifact trees, and no artifact contains a wall-clock instant |
| No mocks | `rg -n 'MagicMock\|mocker\.patch\|unittest\.mock\|create_autospec' tests/` | no mock framework anywhere in the suite |
| Protocol purity | `tests/test_mission.py::TestPureCoreIsolation` | a fresh subprocess importing every domain module leaves `bond_api` out of `sys.modules` |
| Lint / types | `uv run ruff check src/ scripts/` · `uv run mypy src/` | style and type cleanliness on shipped code |
| Lineage | `rg -n "template[_]code_project" .` | no exemplar strings outside docs that explain the lineage |

Rather than quoting a coverage percentage that would go stale the moment a line
moves, this section names the gate. The measured figure is whatever the command
above prints on the checkout you are holding; the guarantee is that it is not
below the floor, because the run fails otherwise.

## Manuscript-metric integrity

The manuscript's variable-token values are produced by
`skyfall.manuscript_variables.generate_variables()` and enforced from both
directions:

- **Forward** — a live test asserts every injected token used in the numbered
  sections exists in the generated map, so a section can never render a raw
  brace.
- **Reverse** — a scanning test asserts the results, methodology, abstract, and
  conclusion contain no bare numerals outside tokens, inline code, and math.
  A hand-typed metric fails the suite. (Four-digit calendar years are exempt:
  a film release year is a literal, not a measurement, and no code change can
  make it drift.)

Together these mean a number in this manuscript is either injected from the
code that computed it, or the suite is red.
