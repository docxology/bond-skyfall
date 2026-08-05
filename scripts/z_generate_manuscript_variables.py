#!/usr/bin/env python3
"""Thin orchestrator: hydrate manuscript {{TOKEN}}s and render the flagship figure.

Usage:
    uv run python scripts/z_generate_manuscript_variables.py [--allow-draft]

Strict by default: unresolved {{TOKEN}}s in a manuscript section fail the run.
``--allow-draft`` writes the resolved tree anyway (intentional early drafts
only). Writes ``output/data/manuscript_variables.json`` and the resolved tree
under ``output/manuscript/``, and renders the estate-defense figure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from skyfall.figures import render_estate_defense_figure, render_traffic_figure  # noqa: E402
from skyfall.manuscript_variables import generate_variables, resolve_manuscript_tree  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-draft", action="store_true", help="write even if tokens remain unresolved")
    parser.add_argument("--config", default=None, help="path to manuscript/config.yaml")
    parser.add_argument("--manuscript-dir", default=None, help="manuscript source directory")
    parser.add_argument("--output-dir", default=None, help="output directory (default: <root>/output)")
    args = parser.parse_args()

    variables = generate_variables(config_path=args.config)
    output_root = Path(args.output_dir) if args.output_dir else ROOT / "output"

    variables_path = output_root / "data" / "manuscript_variables.json"
    variables_path.parent.mkdir(parents=True, exist_ok=True)
    variables_path.write_text(json.dumps(variables, sort_keys=True, indent=2), encoding="utf-8")

    resolve_manuscript_tree(
        variables,
        manuscript_dir=args.manuscript_dir,
        output_dir=output_root / "manuscript",
        strict=not args.allow_draft,
    )
    figure_path = render_estate_defense_figure(output_path=output_root / "figures" / "estate_defense.png")
    traffic_path = render_traffic_figure(output_path=output_root / "figures" / "traffic_detection.png")
    print(f"Resolved {len(variables)} manuscript variables -> {variables_path}")
    print(f"Rendered estate-defense figure -> {figure_path}")
    print(f"Rendered traffic-detection figure -> {traffic_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
