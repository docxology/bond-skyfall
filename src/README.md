# src/ — README

skyfall (SILVA) source tree. Pure domain core (`cyber_ops`, `legacy_audit`,
`estate_defense`) is standalone and must not import `bond_api`; `mission.py`
adapts it to the frozen BOND-API protocol. See `AGENTS.md`.
