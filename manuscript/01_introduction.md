# Introduction

## The SILVA threat

Skyfall (2012) dramatizes a coordinated external assault on MI6: a single
adversary — Silva — reaches the Service's deepest and most sensitive systems
through a chain of aging, poorly-segmented connections, exfiltrates the NATO
agent list, and ultimately forces the confrontation onto home ground at the
Skyfall estate. This package turns that story into six well-posed
computational problems, each with a real deterministic algorithm and real data:

1. **Network intrusion paths** (`skyfall.cyber_ops`) — model the MI6 HQ
   network as a directed graph and ask: by which routes can an adversary reach
   the high-value target, and which is shortest / cheapest?
2. **Traffic change-point detection** (`skyfall.traffic_analysis`) — estimate
   a periodic (hour-of-day) baseline, residualize it, and run a CUSUM control
   chart to catch the exfiltration burst.
3. **Exfiltration severance** (`skyfall.exfiltration`) — treat the outward
   data transfer as a capacitated flow and compute the max-flow and the
   minimum cut (the smallest link set that must be severed).
4. **Legacy-system exposure audit** (`skyfall.legacy_audit`) — quantify how
   aging infrastructure's age, missing patches, obsolete protocols, and open
   services combine into a scalar exposure.
5. **Patch scheduling** (`skyfall.patch_strategy`) — schedule a finite daily
   patching budget to minimize cumulative fleet exposure over a horizon.
6. **Island topology + estate defense** (`skyfall.estate_defense`) — compute
   the reachable topology of Silva's island hideout and the articulation
   (choke) points of the Skyfall estate, then assign a limited defending team.

## Design principles

The package follows the PROJECT BOND guardrails: the pure domain modules are
infrastructure-free and importable without the BOND protocol; `mission.py` is
a thin adapter to the frozen `bond_api` contract; scripts are thin
orchestrators; tests are real-computation and zero-mock, held above a hard
coverage floor rather than to a quoted percentage.

Every number reported in this manuscript is injected from
`skyfall.manuscript_variables.generate_variables()` — never hand-authored —
and that rule is enforced in both directions by the suite: no token may go
unresolved, and no bare numeral may appear in the results narrative. Section 6
describes the gates.

Where a scenario could pass while the underlying algorithm was wrong, the
package prefers a test that enumerates a family over a test that checks the
canonical case; Section 4 records the two defects that discipline caught.
