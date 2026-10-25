---
title: "Manuscript directory: skyfall"
type: "manuscript_guide"
version: "0.1.0"
---

# Manuscript (`manuscript/`)

This directory holds the SILVA mission manuscript. Every metric is injected
from `skyfall.manuscript_variables.generate_variables()` via
`scripts/z_generate_manuscript_variables.py` — never hand-authored in prose.

## {{TOKEN}} protocol

Numeric values derived from computed results **must** use `{{VARIABLE_NAME}}`
syntax. The pipeline is:

1. `scripts/z_generate_manuscript_variables.py` calls
   `skyfall.manuscript_variables.generate_variables()` (strict by default),
2. writes `output/data/manuscript_variables.json`,
3. resolves each `NN_*.md` section into `output/manuscript/`, failing in
   strict mode if any token remains unresolved,
4. renders the estate-defense figure to `output/figures/estate_defense.png`.

To add a token: add a key to `generate_variables()`, add an assertion in
`tests/test_manuscript_variables.py`, and reference it in a section.

The live cross-reference test (`test_live_manuscript_token_cross_reference`)
scans `manuscript/[0-9][0-9]_*.md` only, so sidecar guides may illustrate
literal `{{VARIABLE}}` placeholders without tripping it.

## Figure protocol

| Label | PNG | Generator |
| --- | --- | --- |
| `{#fig:estate_defense}` | `output/figures/estate_defense.png` | `skyfall.figures.render_estate_defense_figure` |
| `{#fig:traffic_detection}` | `output/figures/traffic_detection.png` | `skyfall.figures.render_traffic_figure` |

Referenced via `@fig:estate_defense` / `@fig:traffic_detection` and defined
with a Pandoc image line including the `{#fig:...}` attribute.

## Editing workflow

For behavioral changes: update the domain module, then regenerate the
manuscript variables and figure for the change to be reflected.
