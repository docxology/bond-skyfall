# Results

## Intrusion reachability

The adversary enters at `{{SILVA_ENTRY}}` and works toward `{{SILVA_TARGET}}`
across a {{SILVA_NUM_NETWORK_NODES}}-node network, reaching it by
{{SILVA_NUM_INTRUSION_PATHS}} distinct simple paths. The minimum-hop route is
{{SILVA_SHORTEST_HOPS}} hops (`{{SILVA_SHORTEST_PATH}}`); the
minimum-difficulty route is {{SILVA_CHEAPEST_HOPS}} hops
(`{{SILVA_CHEAPEST_PATH}}`). Traversing the minimum-hop route uncontained has
probability {{SILVA_SUCCESS_PROBABILITY}} under the per-hop survival model.

The legacy directory (`legacy_ldap`, the intrusion network's most exposed host) sits
on some simple intrusion paths but on neither the minimum-hop nor the
minimum-difficulty route: `legacy_ldap` appears on the cheapest path —
**{{SILVA_LEGACY_ON_CHEAPEST}}**. The high traversal difficulty assigned to
that hop is what keeps it off the optimum, so the pivot an adversary would
*prefer* for its exposure is not the pivot the cost model *selects*. Both
directions of that claim are pinned by tests rather than asserted in prose.

## Traffic detection and severance

The HQ traffic detector residualizes the daily rhythm over the
{{SILVA_TRAFFIC_SAMPLES}}-hour series and runs a CUSUM chart; the agent-list
exfiltration burst (window {{SILVA_EXFIL_WINDOW}}) is
**{{SILVA_BURST_DETECTED}}** — the alarm fires at hour {{SILVA_ALARM_INDEX}},
the first hour of the burst window, with a peak accumulation of
{{SILVA_MAX_CUSUM}} standardized units against a decision interval of
{{SILVA_CUSUM_H}}. The independently-computed maximum-likelihood change point
agrees at hour {{SILVA_BEST_CHANGE_POINT}}.

Containment is a min-cut problem: the maximum exfiltration rate from the
registry to the internet is {{SILVA_MAX_FLOW}}, and the minimum severance cut
of equal value ({{SILVA_MIN_CUT_VALUE}}) is `{{SILVA_SEVERANCE}}`. Severing
exactly those links stops the exfiltration. The equality is not a property of
this scenario alone: an enumerated sweep over a family of five-node networks —
including ones whose maximum flow requires reverse residual arcs — confirms
`value(cut) == value(flow)` on every member.

![MI6 HQ traffic detection — residual series with CUSUM alarm](../output/figures/traffic_detection.png){#fig:traffic_detection}

## Fleet exposure and patch schedule

The audited legacy fleet of {{SILVA_FLEET_SIZE}} systems has mean exposure
{{SILVA_MEAN_EXPOSURE}} and maximum exposure {{SILVA_MAX_EXPOSURE}}, with
{{SILVA_CRITICAL_COUNT}} critical systems, yielding an overall fleet risk of
**{{SILVA_FLEET_RISK}}**.

Scheduling the {{SILVA_NUM_VULNERABILITIES}} known vulnerabilities under a
daily budget of {{SILVA_DAILY_BUDGET}} patch over {{SILVA_HORIZON_DAYS}} days
patches all {{SILVA_PATCHED_COUNT}}, cutting cumulative exposure from a
no-patching baseline of {{SILVA_PATCH_BASELINE}} severity-days to
{{SILVA_PATCH_SCHEDULED}} — a {{SILVA_PATCH_REDUCTION}} reduction.

## Estate defense

Of the estate's {{SILVA_NUM_ESTATE_POSITIONS}} positions,
{{SILVA_NUM_CHOKE_POINTS}} are choke points ({{SILVA_CHOKE_POINTS}}). Deploying
the {{SILVA_NUM_DEFENDERS}}-agent team across them posts
{{SILVA_DEFENDERS_USED}} defenders and yields a defensive coverage of
{{SILVA_COVERAGE}} — the team has slack, so no choke point goes unheld. Silva's
island hideout admits {{SILVA_ISLAND_REACHABLE}} reachable cells behind a
perimeter of {{SILVA_ISLAND_PERIMETER}}; its contested approach corridor is
{{SILVA_ISLAND_CORRIDOR}} cells long, terminating at the hideout cell
({{SILVA_ISLAND_HIDEOUT}}).

The flagship figure ([@fig:estate_defense]) maps the estate approach graph,
highlights the choke points, and annotates the assigned defender at each
covered position.

![Skyfall estate choke-point defense plan](../output/figures/estate_defense.png){#fig:estate_defense}

Both figures are rendered deterministically to `output/figures/` by
`skyfall.figures`.
