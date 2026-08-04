# Manuscript — skyfall (SILVA)

Quick reference for the SILVA mission manuscript.

- **Sections**: `00_abstract.md` through `07_scope_and_related_work.md` plus
  `99_references.md`.
- **Config**: `config.yaml` — paper metadata + `mission:`/`scenario:` params.
- **Tokens**: `{{VARIABLE}}` resolved by
  `scripts/z_generate_manuscript_variables.py` (strict mode).
- **Figures**: the estate-defense plan renders to
  `output/figures/estate_defense.png`; reference via `@fig:estate_defense`.

Run the full hydration with:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```
