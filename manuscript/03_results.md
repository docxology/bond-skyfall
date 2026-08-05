# Results

## Intrusion reachability

The adversary enters at `{{SILVA_ENTRY}}` and works toward `{{SILVA_TARGET}}`
across a {{SILVA_NUM_NETWORK_NODES}}-node network, reaching it by
{{SILVA_NUM_INTRUSION_PATHS}} distinct simple paths. The minimum-hop route is
{{SILVA_SHORTEST_HOPS}} hops; the minimum-difficulty route is
{{SILVA_CHEAPEST_HOPS}} hops. The legacy directory (a highly-exposed
aging node) is the pivot an adversary prefers when it is reachable, but the
expensive route through it is never the cheapest aggregate path.

## Traffic detection and severance

The HQ traffic detector residualizes the daily rhythm and runs a CUSUM chart;
the agent-list exfiltration burst (window {{SILVA_EXFIL_WINDOW}}) is
**{{SILVA_BURST_DETECTED}}** — the alarm fires at hour {{SILVA_ALARM_INDEX}},
and the most likely change point is hour {{SILVA_BEST_CHANGE_POINT}}.

Containment is a min-cut problem: the maximum exfiltration rate from the
registry to the internet is {{SILVA_MAX_FLOW}}, and the minimum severance cut
of equal value ({{SILVA_MIN_CUT_VALUE}}) is `{{SILVA_SEVERANCE}}`. Severing
exactly those links stops the exfiltration.

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

The Skyfall estate has {{SILVA_NUM_CHOKE_POINTS}} choke points
({{SILVA_CHOKE_POINTS}}). Deploying the {{SILVA_NUM_DEFENDERS}}-agent team
across them yields a defensive coverage of {{SILVA_COVERAGE}}. The island
hideout's contested approach corridor is {{SILVA_ISLAND_CORRIDOR}} cells long,
terminating at the hideout cell ({{SILVA_ISLAND_HIDEOUT}}).

The flagship figure ([@fig:estate_defense]) maps the estate approach graph,
highlights the choke points, and annotates the assigned defender at each
covered position.

![Skyfall estate choke-point defense plan](../output/figures/estate_defense.png){#fig:estate_defense}

Both figures are rendered deterministically to `output/figures/` by
`skyfall.figures`.
