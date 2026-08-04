# Introduction

## The SILVA threat

Skyfall (2012) dramatizes a coordinated external assault on MI6: a single
adversary — Silva — reaches the Service's deepest and most sensitive systems
through a chain of aging, poorly-segmented connections, and ultimately forces
the confrontation onto home ground at the Skyfall estate. This package turns
that story into three well-posed computational problems, each with a real
deterministic algorithm and real data:

1. **Network intrusion paths** (`skyfall.cyber_ops`) — model the MI6 HQ
   network as a directed graph and ask: by which routes can an adversary reach
   the high-value target, and which is shortest / cheapest?
2. **Legacy-system exposure audit** (`skyfall.legacy_audit`) — quantify how
   the aging infrastructure's age, missing patches, obsolete protocols, and
   open services combine into a scalar exposure, and how to spend a finite
   remediation budget.
3. **Island topology + estate defense** (`skyfall.estate_defense`) — compute
   the reachable topology of Silva's island hideout and the articulation
   (choke) points of the Skyfall estate, then assign a limited defending team.

## Design principles

The package follows the PROJECT BOND guardrails: the pure domain modules are
infrastructure-free and importable without the BOND protocol; `mission.py` is
a thin adapter to the frozen `bond_api` contract; scripts are thin
orchestrators; tests are real-computation and zero-mock with ≥90% coverage.
Every number reported in this manuscript is injected from
`skyfall.manuscript_variables.generate_variables()` — never hand-authored.
