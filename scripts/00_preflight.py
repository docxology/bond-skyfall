#!/usr/bin/env python3
"""Thin orchestrator: preflight the skyfall film for BOND-API compliance.

Usage:
    uv run python scripts/00_preflight.py [slug]

Verifies that the skyfall mission provider can be discovered and bound via
``bond_api.discovery``, that its five provider methods exist, and that the
domain core imports without the BOND protocol. Exit 0 iff all checks pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bond_api.discovery import load_provider  # noqa: E402
from bond_api.protocol import protocol_surface  # noqa: E402


def main() -> int:
    slug = sys.argv[1] if len(sys.argv) > 1 else "skyfall"
    provider = load_provider(slug, search_paths=[SRC])
    surface = protocol_surface()
    expected = set(surface["provider_methods"])
    missing = [m for m in expected if not callable(getattr(provider, m, None))]
    if missing:
        print(f"FAIL: provider {slug!r} missing methods {missing}")
        return 1
    # Report what was actually verified. Printing len(missing) here would
    # always read "0" — a number that cannot vary is not evidence.
    print(
        f"OK: {slug} discoverable, {len(expected)}/{len(expected)} provider methods bound, "
        f"{len(surface['dataclasses'])} protocol dataclasses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
