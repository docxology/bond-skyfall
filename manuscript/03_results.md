# Results

## Intrusion reachability

The adversary enters at `{{SILVA_ENTRY}}` and works toward `{{SILVA_TARGET}}`
across a {{SILVA_NUM_NETWORK_NODES}}-node network, reaching it by
{{SILVA_NUM_INTRUSION_PATHS}} distinct simple paths. The minimum-hop route is
{{SILVA_SHORTEST_HOPS}} hops; the minimum-difficulty route is
{{SILVA_CHEAPEST_HOPS}} hops. The legacy directory (a highly-exposed
aging node) is the pivot an adversary prefers when it is reachable, but the
expensive route through it is never the cheapest aggregate path.

## Fleet exposure

The audited legacy fleet of {{SILVA_FLEET_SIZE}} systems has mean exposure
{{SILVA_MEAN_EXPOSURE}} and maximum exposure {{SILVA_MAX_EXPOSURE}}, with
{{SILVA_CRITICAL_COUNT}} critical systems, yielding an overall fleet risk of
**{{SILVA_FLEET_RISK}}**. A bounded remediation budget of three actions targets
{{SILVA_REMEDIATION_TARGETS}} in order of greatest risk reduction.

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

Figure rendered deterministically to ``output/figures/estate_defense.png`` by
`skyfall.figures.render_estate_defense_figure`.
