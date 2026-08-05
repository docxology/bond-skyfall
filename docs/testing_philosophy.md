# Testing Philosophy — skyfall (SILVA)

## Zero-mock policy

Every test in this package exercises real algorithms against real data. No
`unittest.mock`, no `MagicMock`, no `mocker.patch`, no `create_autospec` —
not as a stylistic preference but because this package's entire value claim is
that its numbers are computed. A mocked collaborator returns the number the
test author expected, which tests the author's expectation rather than the
code.

Where a test needs a boundary it uses a real one:

| Need | What we use instead of a mock |
| --- | --- |
| Isolate the pure core from `bond_api` | A real subprocess with a clean `sys.modules` |
| Exercise a CLI | `subprocess.run([sys.executable, script])` with a real `cwd` |
| Exercise file I/O | `tmp_path` and real files |
| Render a figure | Real matplotlib on the Agg backend |
| Exercise a degraded mission path | A real `Network` in which the target is genuinely unreachable |

That last row is the pattern to copy. When a branch could not be reached with
the frozen scenario, the fix is a real input that reaches it — not a patched
function, and not a `# pragma: no cover`.

## Coverage: a floor, not a trophy

The gate is `uv run pytest tests/ --cov=src --cov-fail-under=90`, measuring
line **and** branch coverage on `src/`. Run it for the current figure; this
document deliberately does not quote one, because a number written in prose
goes stale the moment a line moves and then quietly misinforms every reader
after that.

Coverage is necessary and nowhere near sufficient. Both real defects this
package has carried were in fully covered lines.

## The anti-vacuity doctrine

A green suite is evidence about the tests, not proof about the code. This
package has two documented cases, kept here because they are the reason the
rules below exist.

**Case 1 — the min-cut theorem that only held on the canonical graph.**
`min_cut_edges` computed residual reachability by walking only the original
forward edges, ignoring the reverse arcs that pushed flow creates. On
`DEFAULT_FLOW_NETWORK` — an acyclic network where the distinction never bites —
the max-flow min-cut assertion passed. On a five-node network with a shared
bottleneck it reported a cut of 6.0 against a max flow of 3.0, violating the
theorem the docstring cited. The test that caught it enumerates every 5-edge
subset of an 11-edge candidate set (462 networks) and asserts the theorem on
each; the fix was verified by confirming that sweep fails against the old
implementation before it passed against the new one.

**Case 2 — the tie-break that compared one character.**
`prioritize_remediation` documented "ties broken lexicographically by id" and
implemented `-ord(system_id[0])`, comparing only the first character. Systems
sharing a first letter tied completely, and the winner fell out of dict
insertion order. No test noticed, because the canonical fleet has five systems
with five distinct dominant factors and no ties at all. The test that catches
it constructs two systems identical apart from their ids and asserts the result
is insertion-order independent.

The rules that follow from those two:

1. **Test the property, not the scenario.** If a claim is universal ("the cut
   equals the flow", "the order is deterministic"), enumerate a family. A
   single canonical case measures the case.
2. **Confirm the guard fails.** Before accepting a regression test, run it
   against the broken code. A test that passes both before and after the fix
   guards nothing.
3. **Pin the population.** An enumerated sweep asserts its own size
   (`assert checked == 462`); otherwise a filter bug silently reduces it to
   zero cases and the sweep passes vacuously.
4. **A guard that cannot fire is worse than no guard**, because it reads as
   coverage. Three such guards were deleted from this package (an empty-path
   check behind a dataclass that rejects empty paths, an impassable-entry check
   behind a grid that rejects impassable entries, and an unreachable `inf`
   sentinel branch). Where the guard is genuinely wanted, give it a seam —
   `require_reachable()` and the injectable `MissionProvider(network=...)` are
   both branches made testable rather than deleted or ignored.
5. **Include negative controls.** The results section claims `legacy_ldap` is
   not on the cheapest path; a test asserts that, and a second asserts it *does*
   appear on some simple path — otherwise the first would pass trivially if the
   node became unreachable.

## Determinism

- Fixed scenario constants — network, traffic series, flow network, legacy
  fleet, vulnerability backlog, estate graph, island grid. Nothing varies.
- No RNG draws anywhere. `SILVA_SEED = 11` is recorded in provenance only, and
  the provenance asserts it.
- No wall-clock in any persisted metric. `GENERATION_TIMESTAMP` is a build
  label and enters no result; `Provenance.wall_time_s` is fixed at `0.0`.
- Both figure PNGs are asserted byte-identical across repeated renders.
- `analyze_*` functions are asserted to return equal results on repeated calls.
- Iteration order is explicitly sorted wherever a set or dict is traversed, so
  results do not depend on hash ordering.

## Manuscript integrity, enforced from both directions

- **Forward** — every injected token used in a numbered section must exist in
  the generated variable map, so a section can never render a raw brace.
- **Reverse** — the abstract, methodology, results, and conclusion are scanned
  for bare numerals outside tokens, inline code, and math. A hand-typed metric
  fails the suite. Four-digit calendar years are exempt: a film release year is
  a literal, not a measurement.

Together these mean a number in the manuscript is either injected from the code
that computed it, or the suite is red.

## Test inventory

| File | Covers |
| --- | --- |
| `test_cyber_ops.py` | Network validation, simple-path enumeration, BFS/Dijkstra (including stale-heap discard), survival probability, step simulation, named model constants, the cheapest-path claims the results section makes |
| `test_traffic_analysis.py` | Periodic baseline, detrending, baseline statistics, CUSUM series and detection, EWMA, change-point likelihood, the canonical burst |
| `test_exfiltration.py` | Network validation, Edmonds–Karp, min cut, severance rendering, the 462-network theorem sweep, the diamond regression case |
| `test_legacy_audit.py` | System validation, the shared factor model, exposure score, fleet audit and all four risk labels, tier membership, remediation ordering and tie-breaking |
| `test_patch_strategy.py` | Vulnerability validation, baseline exposure, greedy schedule, exposure with schedule, reduction metrics |
| `test_estate_defense.py` | Island grid and topology, Tarjan choke points, road-symmetry enforcement, defense planning, coverage, the no-choke-point plan |
| `test_mission.py` | Provider identity, structural protocol conformance, five-stage lifecycle, provenance, gadget registry, every conditional debrief lesson, the unreachable-target failure path, pure-core isolation |
| `test_manuscript_variables.py` | Config loading and validation, token generation, strict resolution, the reachability seam, and both manuscript-integrity gates |
| `test_figures.py` | Deterministic PNG rendering of both figures, coverage-fraction typing |
| `test_scripts_smoke.py` | All three CLIs via real subprocesses, including argparse exit codes |

`conftest.py` pins `MPLBACKEND=Agg` and puts `src/` on `sys.path` so the
documented pytest command works from a clean environment.

## Running

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90     # the gate
uv run pytest tests/test_exfiltration.py -v            # one module
uv run pytest tests/ -q -k "theorem"                   # one property
```
