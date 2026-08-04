# docs/ — Agent-Facing Documentation Hub

Index for the skyfall (SILVA) mission package docs. Start with
`agent_instructions.md`.

| File | Purpose |
| --- | --- |
| `README.md` | Quick navigation + verification commands |
| `agent_instructions.md` | Read-first behavioral rules for agents |
| `architecture.md` | Module boundaries, dependency direction |
| `testing_philosophy.md` | Zero-mock policy, test inventory, determinism |

## Core constraints (summary)

- Pure domain core never imports `bond_api`.
- `scripts/` are thin orchestrators only.
- Manuscript metrics are `{{VARIABLE}}`-injected, never hand-authored.
- Zero mocks; ≥90% coverage; deterministic throughout.
