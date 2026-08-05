"""skyfall — Skyfall (2012) · mission codename SILVA.

A PROJECT BOND film package. The pure domain core models the SILVA mission's
threat surfaces:

* :mod:`skyfall.cyber_ops` — the cyberattack on MI6's headquarters network:
  intrusion-path enumeration, shortest/cheapest reachability, and a
  deterministic step-by-step intrusion simulation.
* :mod:`skyfall.traffic_analysis` — periodic-baseline CUSUM change-point
  detection of the agent-list exfiltration burst.
* :mod:`skyfall.exfiltration` — Edmonds–Karp max-flow and min-cut severance of
  the outward data transfer.
* :mod:`skyfall.legacy_audit` — the aging-infrastructure exposure audit:
  closed-form per-system risk scores, fleet aggregation, and prioritized
  remediation.
* :mod:`skyfall.patch_strategy` — greedy scheduling of the legacy patch
  backlog under a daily budget.
* :mod:`skyfall.estate_defense` — Silva's island hideout topology and the
  Skyfall estate choke-point defense plan (articulation-point analysis).

:mod:`skyfall.mission` adapts these pure modules to the frozen BOND-API
:class:`~bond_api.protocol.MissionProvider` contract and registers the film's
gadgets with the BOND gadget registry.

The domain modules import nothing from the BOND protocol — they are fully
standalone (stdlib + math only) — so the film's core stays usable even if the
bond-api path dependency is ever unavailable. For that same reason the facade
does NOT eagerly import the mission adapter: use ``from skyfall.mission import
MissionProvider`` when the provider is needed (the discovery contract imports
``skyfall.mission`` directly and never goes through this facade).
"""

from __future__ import annotations

from . import (
    cyber_ops,
    estate_defense,
    exfiltration,
    legacy_audit,
    patch_strategy,
    traffic_analysis,
)

__all__ = [
    "cyber_ops",
    "legacy_audit",
    "estate_defense",
    "exfiltration",
    "patch_strategy",
    "traffic_analysis",
]
