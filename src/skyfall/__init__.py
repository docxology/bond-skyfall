"""skyfall — Skyfall (2012) · mission codename SILVA.

A PROJECT BOND film package. The pure domain core models the SILVA mission's
three threat surfaces:

* :mod:`skyfall.cyber_ops` — the cyberattack on MI6's headquarters network:
  intrusion-path enumeration, shortest/cheapest reachability, and a
  deterministic step-by-step intrusion simulation.
* :mod:`skyfall.legacy_audit` — the aging-infrastructure exposure audit:
  closed-form per-system risk scores, fleet aggregation, and prioritized
  remediation.
* :mod:`skyfall.estate_defense` — Silva's island hideout topology and the
  Skyfall estate choke-point defense plan (articulation-point analysis).

:mod:`skyfall.mission` adapts these pure modules to the frozen BOND-API
:class:`~bond_api.protocol.MissionProvider` contract and registers the film's
gadgets with the BOND gadget registry.

The domain modules import nothing from the BOND protocol — they are fully
standalone (stdlib + math only) — so the film's core stays usable even if the
bond-api path dependency is ever unavailable.
"""

from __future__ import annotations

from . import cyber_ops, estate_defense, legacy_audit
from .mission import MissionProvider

__all__ = ["cyber_ops", "legacy_audit", "estate_defense", "MissionProvider"]
