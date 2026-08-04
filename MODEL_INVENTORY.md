# SSH method inventory

This development-facing inventory distinguishes source evidence, planned implementation, and actual package support. “Planned” never means an API placeholder exists.

| Family | Method | Main purpose | Reference implementation evidence | pyGeoHet state | Stage |
|---|---|---|---|---|---:|
| Classical | GD / q-statistic | global stratified explanatory power | GD, gdverse, Python/QGIS implementations | q and factor implemented | 1–2 |
| Discretization | Optimal discretization | reduce subjective continuous-factor breaks | GD/gdverse follow-up implementations | planned | 3 |
| Discretization | OPGD | optimize method, class count and scale | GD and gdverse | planned | 3 |
| Discretization | MSD | supervised multiscale break search | paper-associated code reported | planned | 3 |
| Spatial | SPADE | spatial variance and multilevel discretization | gdverse follow-up implementation | planned | 5 |
| Spatial | IDSA | spatially informed interaction zones | IDSA/gdverse | planned | 5 |
| Categorical | SRS-GD | nominal target and local rough-set power | paper C++ / gdverse follow-up | planned | 6 |
| Multivariate | GOZH | optimized multi-factor geographical zones | gdverse | planned | 7 |
| Robust | RGD | change-point robust discretization and B-value | gdverse follow-up | planned | 4 |
| Information | SSHIC/SSHIN | distribution differences beyond variance | sshicm | planned | 6 |
| Explanation | LESH | Shapley allocation in multivariate zones | gdverse | planned | 7 |
| Robust | RID | robust two-factor interaction | gdverse | planned | 4 |
| Heavy-tail | Head/Tail SSH | recursive heavy-tailed stratification | paper code reported | planned | 3/8 |
| Multivariate | OMGD | optimal 3+ factor clustering and scale | author Python repository | planned | 7 |
| Local | LISP | local stratified power and significance | localsp | planned | 8 |
| Pattern | GPI | variable effects in pattern interaction | partial related software evidence | evidence review | 8 |
| Structure | Local geometry SSH | compare local geometrical configurations | author repository reported | evidence review | 8 |
| Complexity | UEP | power per stratification complexity | author repository reported | evidence review | 8 |
| Spatial information | SWMI | spatially weighted mutual information | no full public package found | source audit | 6 |
| Observation bias | EQ-statistic | biased and missing spatial observations | no public implementation found | source audit | 9 |
| Outliers | SOH | outlier-pattern-assisted stratification | associated data/code reported | source audit | 9 |
| Original research | Lagged SSH | cross-lag explanatory power with valid inference | methodological gap | experimental only | 10 |

## Evidence hierarchy

1. primary peer-reviewed paper;
2. official supplementary material or author implementation;
3. maintained reference software;
4. independent implementation used only for behavioural comparison;
5. simulation and analytical properties.

When sources disagree, pyGeoHet records the disagreement and exposes an explicit convention instead of averaging incompatible definitions.
