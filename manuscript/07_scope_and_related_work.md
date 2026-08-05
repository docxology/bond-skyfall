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

- **BFS / Dijkstra reachability**, **simple-path enumeration**, and
  **Edmonds–Karp max-flow / min-cut** are standard graph algorithms widely
  used in network-intrusion and reachability analysis (Cormen et al. 2009;
  Edmonds & Karp 1972; Ford & Fulkerson 1962).
- **Tarjan's articulation-point algorithm** finds cut vertices / choke points
  in a graph, used in network resilience and defensive-planning domains
  (Even 2011).
- **CUSUM change-point detection** (Page 1954; Hawkins & Olwell 1999)
  underpins the traffic detector.
- **Weighted risk scoring** and **greedy priority scheduling** mirror common
  vulnerability-management and scheduling practice (Pinedo 2016), kept
  transparent and deterministic.

Where the film's narrative maps onto these tools, this package documents the
mapping so a reader can trace every metric to its algorithm.
