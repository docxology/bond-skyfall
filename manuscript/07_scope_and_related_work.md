# Scope and Related Work

## Scope

The SILVA mission deliberately covers six computational problems, across three
layers, that can be solved exactly and deterministically with classical graph,
statistical, and scheduling algorithms.

It explicitly does **not** attempt a full stochastic intrusion simulation, a
live penetration test, an adaptive (non-periodic) change-point detector beyond
the two-segment likelihood, or a physical simulation of the estate — those
would introduce nondeterminism that the package's reproducibility guarantee
forbids. The exposure and severity models are likewise transparent linear
scores, not calibrated empirical risk estimates: they are stated as a model,
scoped as a model, and never presented as measurements of real infrastructure.
The value is in clean problem formulation, exact algorithms, and honest
measurement.

The betweenness-ranked defense and the coupling-aware scheduler are deliberate
*modeling extensions*, provided and tested alongside their defaults rather
than replacing them: the canonical recorded figures stay fixed unless the
variant is invoked, so the manuscript's headline numbers are not disturbed by
the richer alternatives. Likewise the coupling discount
({{SILVA_COUPLING_DISCOUNT}}×) and the exposure/severity weights are model
parameters, not measurements of real infrastructure.

## Related work

The algorithms used here are textbook, and the security framings they serve are
established practice:

- **Simple-path enumeration for intrusion reachability** is the core of the
  attack-graph literature: enumerating the routes an adversary can take through
  a networked system, then reasoning over that set (Phillips & Swiler 1998;
  Sheyner et al. 2002).
- **BFS / Dijkstra reachability** (Dijkstra 1959; Cormen et al. 2009) supply
  the minimum-hop and minimum-difficulty routes, and **Edmonds–Karp max-flow
  with the max-flow min-cut theorem** (Edmonds & Karp 1972; Ford & Fulkerson
  1962) supplies the exfiltration severance.
- **Tarjan's articulation-point algorithm** (Tarjan 1972; Hopcroft & Tarjan
  1973; Even 2011) finds cut vertices — the choke points — and is standard in
  network-resilience and defensive-planning work. **Betweenness centrality**
  (Brandes 2001) ranks those choke points by the share of shortest-path
  traffic each carries, complementing degree when scarce defenders must be
  placed.
- **CUSUM change-point detection** (Page 1954; Montgomery 2012; Hawkins &
  Olwell 1998) underpins the traffic detector; the two-segment likelihood split
  is the single-change-point special case of the segmentation objective treated
  at scale by Killick et al. (2012).
- **Weighted multi-factor vulnerability scoring** follows the structure of
  CVSS-style composite metrics (Mell, Scarfone & Romanosky 2007), kept
  deliberately simpler and fully transparent here.
- **Patch scheduling under a finite budget** is a real operational tradeoff
  studied directly by Beattie et al. (2002); the greedy severity-first policy
  is standard priority scheduling (Pinedo 2016).

Where the film's narrative maps onto these tools, this package documents the
mapping so a reader can trace every metric to its algorithm.
