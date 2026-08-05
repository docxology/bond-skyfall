#!/usr/bin/env python3
"""Thin orchestrator: run one phase of the SILVA mission against the skyfall film.

Usage:
    uv run python scripts/run_mission.py {brief|recon|plan|execute|debrief|all} [--json]

Binds the skyfall mission provider from ``src/`` and always runs the complete
five-stage lifecycle (each stage consumes the previous stage's output, so the
later stages cannot be produced in isolation); ``phase`` selects which stage's
result is *reported*, in human-readable form or as ``--json``.

Exit code is 0 on success and 2 on an argparse error. A provider failure
propagates as an uncaught exception rather than an exit-1 summary: this is a
thin orchestrator, and swallowing a domain traceback would hide the defect.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bond_api.protocol import ReconRequest  # noqa: E402
from bond_api.serialization import to_json  # noqa: E402

from skyfall.mission import MissionProvider  # noqa: E402

_PHASES = ("brief", "recon", "plan", "execute", "debrief", "all")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=_PHASES, help="mission phase to run")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    provider = MissionProvider()
    request = ReconRequest(goal="assess SILVA's combined cyber, legacy, and estate threat")

    brief = provider.brief()
    report = provider.recon(request)
    plan = provider.plan(brief)
    outcome = provider.execute(plan)
    debrief = provider.debrief(outcome)

    if args.json:
        payload = {
            "film": brief.film,
            "phase": args.phase,
        }
        if args.phase in ("brief", "all"):
            payload["brief"] = {"codename": brief.codename, "objectives": list(brief.objectives)}
        if args.phase in ("recon", "all"):
            payload["recon"] = {"findings": [{"label": f.label} for f in report.findings]}
        if args.phase in ("plan", "all"):
            payload["plan"] = {"steps": [s.name for s in plan.steps]}
        if args.phase in ("execute", "all"):
            payload["outcome"] = to_json(outcome)
        if args.phase in ("debrief", "all"):
            payload["debrief"] = {"lessons": list(debrief.lessons)}
        print(to_json({"result": payload}))
        return 0

    print(f"Film: {brief.film} ({brief.codename})")
    if args.phase in ("brief", "all"):
        print(f"Objectives: {len(brief.objectives)}")
    if args.phase in ("recon", "all"):
        print(f"Recon findings: {len(report.findings)}")
    if args.phase in ("plan", "all"):
        print(f"Plan steps: {len(plan.steps)}")
    if args.phase in ("execute", "all"):
        estate = outcome.results["estate"]
        print(f"Outcome success: {outcome.success} | coverage {estate['coverage']}")
    if args.phase in ("debrief", "all"):
        print(f"Lessons: {len(debrief.lessons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
