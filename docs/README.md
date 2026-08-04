# docs/ — CLI Quick Navigation

Agent-facing documentation for the skyfall (SILVA) mission package.

- `agent_instructions.md` — read-first behavioral rules for AI agents.
- `architecture.md` — module boundaries and the thin-orchestrator pattern.
- `testing_philosophy.md` — zero-mock, ≥90% coverage, deterministic tests.

## Quick commands

```bash
cd projects/working/bond/skyfall
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/run_mission.py all --json
```
