"""Subprocess smoke tests for the thin skyfall scripts.

Runs the CLIs through the venv interpreter with cwd = package root, exactly as
a user would, and asserts exit codes + written artifacts.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(*args: str, expect: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / args[0]), *args[1:]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expect, f"cmd failed: {args} -> {result.stderr}"
    return result


class TestRunMission:
    def test_brief(self) -> None:
        result = _run("run_mission.py", "brief")
        assert "skyfall" in result.stdout

    def test_execute(self) -> None:
        result = _run("run_mission.py", "execute")
        assert "success: True" in result.stdout

    def test_all_json(self) -> None:
        result = _run("run_mission.py", "all", "--json")
        payload = json.loads(result.stdout)
        assert payload["result"]["film"] == "skyfall"

    def test_invalid_phase_exits_2(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_mission.py"), "bogus"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2


class TestPreflight:
    def test_preflight_ok(self) -> None:
        result = _run("00_preflight.py", "skyfall")
        assert "OK" in result.stdout


class TestGenerateManuscript:
    def test_generate_outputs(self, tmp_path: Path) -> None:
        result = _run(
            "z_generate_manuscript_variables.py",
            "--output-dir",
            str(tmp_path),
        )
        assert "manuscript variables" in result.stdout
        assert (tmp_path / "data" / "manuscript_variables.json").is_file()
        assert (tmp_path / "figures" / "estate_defense.png").is_file()
        resolved = list((tmp_path / "manuscript").glob("*.md"))
        assert resolved  # at least one resolved section

    def test_strict_fails_on_unresolved(self, tmp_path: Path) -> None:
        # Provide a manuscript dir whose section contains an unresolved token.
        manu = tmp_path / "manuscript_src"
        manu.mkdir()
        (manu / "00_abstract.md").write_text("token {{NOPE}} left", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "z_generate_manuscript_variables.py"),
                "--manuscript-dir",
                str(manu),
                "--output-dir",
                str(tmp_path / "out"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "unresolved" in result.stderr
