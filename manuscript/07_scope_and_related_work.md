# Scope and Related Work

## Scope

The SILVA mission deliberately covers three computational problems that can be
solved exactly and deterministically with classical graph and scoring
algorithms. It explicitly does **not** attempt a full stochastic intrusion
simulation, a live penetration test, or a physical-simulation of the estate —
those would introduce nondeterminism that the package's reproducibility
guarantee forbids. The value is in clean problem formulation, exact
algorithms, and honest measurement.

## Related work

The algorithms used here are textbook:

- **BFS / Dijkstra reachability** and **simple-path enumeration** are standard
  graph algorithms widely used in network-intrusion and reachability analysis.
- **Tarjan's articulation-point algorithm** is the canonical method for
  finding cut vertices / choke points in a graph, used in network resilience
  and defensive-planning domains.
- **Weighted risk scoring** (age, patch, protocol, surface factors) mirrors
  common vulnerability-management and CVSS-style aggregation practice, here
  kept fully transparent and deterministic.

Where the film's narrative maps onto these tools, this package documents the
mapping so a reader can trace every metric to its algorithm.
