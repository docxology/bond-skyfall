# Manuscript Syntax Notes

## Citation syntax

Use Pandoc `@key` for narrative citations and `[@key]` for parenthetical
citations, matching keys in `references.bib`. Example:
`Tarjan's articulation algorithm [@even2011graph]`.

## Figure syntax

Figures are referenced by `@fig:label` / `[@fig:label]` in prose and defined
with a Pandoc image line including a `{#fig:label}` attribute:

```markdown
![Skyfall estate choke-point defense plan](../output/figures/estate_defense.png){#fig:estate_defense}
```

## {{TOKEN}} protocol

`{{VARIABLE_NAME}}` tokens are substituted by
`scripts/z_generate_manuscript_variables.py` (via
`skyfall.manuscript_variables.generate_variables`). Numbered sections
(`NN_*.md`) must only use tokens the generator produces; the live
cross-reference test enforces this. Sidecar files (this guide, AGENTS.md,
README.md) may illustrate literal `{{VARIABLE}}` placeholders without
tripping the gate (the cross-check scans `[0-9][0-9]_*.md` only).
