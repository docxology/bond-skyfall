# scripts/ — Thin orchestrators

Skyfall scripts are thin CLIs: argv shaping + forwarding to `src/`. No
business logic lives here.

| Script | Purpose |
| --- | --- |
| `run_mission.py` | Run one/full SILVA mission phase (brief/recon/plan/execute/debrief) |
| `00_preflight.py` | Verify BOND-API discovery/protocol compliance |
| `z_generate_manuscript_variables.py` | Hydrate `{{TOKEN}}`s + render flagship figure |

Scripts add `src/` to `sys.path` and are run with the venv python from the
package root, e.g. `uv run python scripts/run_mission.py all --json`.
