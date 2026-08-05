# Skyfall — SILVA

## Abstract

Skyfall is a PROJECT BOND mission-software package (film: Skyfall, 2012;
codename **SILVA**) that models six linked threat surfaces through a purely
deterministic computational core, grouped into three mission layers.

The **cyber layer** models the intrusion paths an adversary can take into MI6's
headquarters network, enumerating all simple routes and the minimum-hop /
minimum-difficulty routes into the deepest system; it detects the agent-list
exfiltration burst in HQ traffic with a periodic-baseline CUSUM change-point
detector; and it computes the minimum severance cut (max-flow / min-cut) that
stops the exfiltration.

The **legacy layer** audits the aging infrastructure that still underpins
operations, computing a closed-form exposure score per system from four
normalized risk factors, an aggregate fleet risk, and a greedy patch schedule
that minimizes cumulative exposure under a daily patching budget.

The **physical-defense layer** computes Silva's island hideout topology by
flood fill and the Skyfall estate's articulation (choke) points by Tarjan's
algorithm, then plans a defender assignment that covers them.

All results are reproducible: fixed inputs, no random draws, and no wall-clock
in any persisted metric. The package implements the frozen BOND-API
``MissionProvider`` contract and registers its gadgets with the BOND gadget
registry, making the SILVA mission discoverable by the suite's orchestrator.

## Concurrency of the six threats

The mission treats the cyber intrusion ({{SILVA_ENTRY}} → {{SILVA_TARGET}},
{{SILVA_NUM_INTRUSION_PATHS}} simple paths), the exfiltration burst (detected
at hour {{SILVA_ALARM_INDEX}}, window {{SILVA_EXFIL_WINDOW}}), the severance
cut (max flow {{SILVA_MAX_FLOW}}), the legacy-system exposure (fleet size
{{SILVA_FLEET_SIZE}}, mean exposure {{SILVA_MEAN_EXPOSURE}}), the patch
back-log ({{SILVA_NUM_VULNERABILITIES}} vulnerabilities, cut by
{{SILVA_PATCH_REDUCTION}}), and the estate's choke-point defense
({{SILVA_NUM_CHOKE_POINTS}} choke points, coverage {{SILVA_COVERAGE}}) as one
coordinated assault — the way the film depicts a single adversary reaching
MI6's most sensitive systems through a chain of aging, poorly-segmented
connections.
