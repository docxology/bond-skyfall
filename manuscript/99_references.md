# References

Every entry below is a real, checkable publication that a model in this package
actually rests on. An entry whose subject matter no model uses has been removed
rather than kept for weight.

## Graph algorithms

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009).
*Introduction to Algorithms* (3rd ed.). MIT Press. — breadth-first search,
Dijkstra's algorithm, depth-first search / articulation-point analysis, and
Edmonds–Karp max-flow / min-cut.

Dijkstra, E. W. (1959). A Note on Two Problems in Connexion with Graphs.
*Numerische Mathematik*, 1, 269–271. — the minimum-difficulty intrusion path.

Tarjan, R. (1972). Depth-First Search and Linear Graph Algorithms. *SIAM
Journal on Computing*, 1(2), 146–160. — the articulation-point (choke-point)
algorithm, implemented here in iterative form.

Hopcroft, J., & Tarjan, R. (1973). Algorithm 447: Efficient Algorithms for
Graph Manipulation. *Communications of the ACM*, 16(6), 372–378. — the
biconnectivity formulation of the same search.

Even, S. (2011). *Graph Algorithms* (2nd ed.). Cambridge University Press. —
biconnectivity and cut-vertex theory underlying the choke-point analysis.

## Network flow

Edmonds, J., & Karp, R. M. (1972). Theoretical Improvements in Algorithmic
Efficiency for Network Flow Problems. *Journal of the ACM*, 19(2), 248–264. —
the BFS-augmenting max-flow algorithm used in the severance analysis.

Ford, L. R., & Fulkerson, D. R. (1962). *Flows in Networks*. Princeton
University Press. — the max-flow min-cut theorem underlying the severance
plan, and the residual-graph construction the cut computation depends on.

## Intrusion reachability and vulnerability scoring

Phillips, C., & Swiler, L. P. (1998). A Graph-Based System for
Network-Vulnerability Analysis. *Proceedings of the 1998 Workshop on New
Security Paradigms (NSPW '98)*, 71–79. — the attack-graph framing of intrusion
reachability.

Sheyner, O., Haines, J., Jha, S., Lippmann, R., & Wing, J. M. (2002).
Automated Generation and Analysis of Attack Graphs. *Proceedings of the 2002
IEEE Symposium on Security and Privacy*, 273–284. — automated enumeration and
analysis of adversary paths through a networked system.

Mell, P., Scarfone, K., & Romanosky, S. (2007). *A Complete Guide to the
Common Vulnerability Scoring System Version 2.0*. FIRST. — the weighted
multi-factor composite structure the legacy exposure score follows, in
simplified and fully transparent form.

## Change-point detection

Page, E. S. (1954). Continuous Inspection Schemes. *Biometrika*, 41(1/2),
100–115. — the cumulative-sum (CUSUM) control chart used by the traffic
change-point detector.

Hawkins, D. M., & Olwell, D. H. (1998). *Cumulative Sum Charts and Charting
for Quality Improvement*. Springer. — residualized two-sided CUSUM practice.

Montgomery, D. C. (2012). *Introduction to Statistical Quality Control* (7th
ed.). Wiley. — the standardized CUSUM parameterization (allowance *k*,
decision interval *h*) this package uses.

Killick, R., Fearnhead, P., & Eckley, I. A. (2012). Optimal Detection of
Changepoints with a Linear Computational Cost. *Journal of the American
Statistical Association*, 107(500), 1590–1598. — the segmentation objective
whose single-change-point case this package's two-segment likelihood solves.

## Scheduling

Beattie, S., Arnold, S., Cowan, C., Wagle, P., Wright, C., & Shostack, A.
(2002). Timing the Application of Security Patches for Optimal Uptime.
*Proceedings of the 16th USENIX Conference on System Administration (LISA
'02)*, 233–242. — patching as a scheduled operational tradeoff rather than an
instantaneous act.

Pinedo, M. L. (2016). *Scheduling: Theory, Algorithms, and Systems* (5th ed.).
Springer. — greedy priority scheduling under a capacity constraint.
