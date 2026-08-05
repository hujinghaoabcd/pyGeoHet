# SSH method inventory

This development-facing inventory distinguishes source evidence, planned implementation, and actual package support. “Planned” never means an API placeholder exists.

| Family | Method | Main purpose | Reference implementation evidence | pyGeoHet state | Stage |
|---|---|---|---|---|---:|
| Classical | GD / q-statistic | global stratified explanatory power | GD, gdverse, Python/QGIS implementations | implemented and NTD-validated | 1 |
| Classical | Interaction detector | pairwise overlay enhancement/weakening | GD, gdverse, geodetector, Python implementations | implemented and NTD-validated | 2 |
| Classical | Risk detector | compare response means between strata | GD, gdverse, geodetector, Python implementations | implemented with Welch tests | 2 |
| Classical | Ecological detector | compare residual dispersion between factors | primary papers; inconsistent package conventions | implemented with two-sided primary and upper-tail compatibility modes | 2 |
| Stratification | Equal interval | equal-width continuous breaks | optimal-discretization paper; sdsfun/gdverse | implemented with explicit lower-boundary convention | 3A |
| Stratification | Quantile | approximately equal-frequency strata | optimal-discretization paper; sdsfun/gdverse | implemented without splitting equal values; collapse audited | 3A |
| Stratification | Natural breaks | minimize within-class dispersion | optimal-discretization paper; sdsfun/gdverse | implemented by weighted Fisher-Jenks dynamic programming | 3A |
| Stratification | Geometric interval | multiplicative interval progression | optimal-discretization paper; sdsfun/gdverse | implemented for strictly positive values | 3A |
| Stratification | Standard deviation | mean-centred SD bands | optimal-discretization paper; sdsfun/gdverse | implemented with sample SD | 3A |
| Stratification | Head/tail breaks | recursive heavy-tail stratification | paper/code evidence; sdsfun | implemented with configurable head threshold | 3A |
| Discretization | Optimal univariate discretization | select method and class count by q | GD/gdverse follow-up implementations | implemented with full accepted/rejected candidate table | 3A |
| Discretization | OPGD | optimize continuous factors before classic detectors | 2020 OPGD paper; GD and gdverse | univariate method/class search implemented | 3A |
| Scale | Primary-paper spatial-scale OPGD | select prepared support by 90% q quantile | 2020 OPGD paper; legacy GD `sesu` | implemented with explicit eligibility and tie policies; external fixture pending | 3B |
| Scale | Legacy GD significant-factor scale score | filter by factor p before 90% q quantile | `ausgis/GD::sesu` | implemented as `significant_only=True` compatibility mode | 3B |
| Scale | gdverse LOESS scale heuristic | mean significant q with marginal-increase stopping | gdverse `sesu_opgd`; sdsfun `loess_optnum` | documented divergence; not yet reproduced | 3B |
| Discretization | MSD | supervised coarse-to-fine cut search on an explanatory-variable value grid | 2021 primary paper and reported Figshare code; uploaded GD/gdverse used as structural references | implemented with exact and multiscale modes; author-code fixture pending | 3C |
| Robust | Fixed-K robust discretization | exact variance change-point partition and B-value | RGD paper; uploaded author notebook; gdverse `robustdisc` | implemented by independent exact DP with duplicate-x safety; external fixture pending | 4 |
| Robust | RGD | optimize robust zones for continuous factors before detectors | uploaded author Python notebook; gdverse `rgd`; primary paper | implemented with marginal-gain and maximum-B selection; published case pending | 4 |
| Robust | RID | robust factor zones followed by pairwise interaction detection | gdverse `rid`; robust-interaction paper/workflow evidence | implemented by composition with collision-safe interaction detector; fixture pending | 4 |
| Spatial | Spatial variance | weighted average pairwise semivariance | SPADE paper; sdsfun `spvar`; gdverse wrappers | implemented for explicit dense weights with diagonal/island audit | 5A |
| Spatial | PSD | spatial determinant for categorical strata | SPADE paper; gdverse `psd_spade`; sdsfun | implemented and checked against NTD soiltype fixture | 5A |
| Spatial | CPSD | compensate response PSD by information-retention PSD | SPADE paper; gdverse/sdsfun workflows | implemented; external continuous-case fixture pending | 5A |
| Spatial | PSMD | average CPSD over explicit discretization levels | SPADE paper; gdverse `spade`; sdsfun | implemented with complete accepted/rejected level table | 5A |
| Spatial | SPADE | categorical PSD and continuous PSMD workflow | primary paper; gdverse and sdsfun | implemented with explicit factor typing and seeded permutations | 5A |
| Spatial interaction | Fuzzy overlay | response-risk membership AND/OR zones | IDSA paper; sdsfun `fuzzyoverlay` | implemented with tuple identities, explicit ties and audit tables | 5B |
| Spatial interaction | IDSA / PID | spatially informed interactive determinant | IDSA paper; gdverse `idsa`/`pid_idsa`; sdsfun | implemented with fixed PID, CPSD discretization and subset search; external case pending | 5B |
| Categorical | SRS-GD | nominal target and local rough-set power | Bai et al. (2022); uploaded gdverse source | paper-aligned implementation with Figure 1 fixture; external cases pending | 6A |
| Information | IC-SSH / IN-SSH | continuous and nominal distribution consistency across strata | 2023 paper; pinned stscl/sshicm source | implemented with shared-support histograms, normalized MI and corrected permutations; external fixture pending | 6B |
| Spatial information | SWMI | spatially weighted mutual information | 2026 paper; no authoritative implementation pinned | evidence-gated; no API until full formulas and fixture are verified | 6C |
| Multivariate | GOZH | optimized multi-factor geographical zones | gdverse | planned | 7 |
| Explanation | LESH | Shapley allocation in multivariate zones | gdverse | planned | 7 |
| Multivariate | OMGD | optimal 3+ factor clustering and scale | author Python repository | planned | 7 |
| Local | LISP | local stratified power and significance | localsp | planned | 8 |
| Pattern | GPI | variable effects in pattern interaction | partial related software evidence | evidence review | 8 |
| Structure | Local geometry SSH | compare local geometrical configurations | author repository reported | evidence review | 8 |
| Complexity | UEP | power per stratification complexity | author repository reported | evidence review | 8 |
| Observation bias | EQ-statistic | biased and missing spatial observations | no public implementation found | source audit | 9 |
| Outliers | SOH | outlier-pattern-assisted stratification | associated data/code reported | source audit | 9 |
| Original research | Lagged SSH | cross-lag explanatory power with valid inference | methodological gap | experimental only | 10 |

## Evidence hierarchy

1. primary peer-reviewed paper;
2. official supplementary material or author implementation;
3. maintained reference software;
4. independent implementation used only for behavioural comparison;
5. simulation and analytical properties.

When sources disagree, pyGeoHet records the disagreement and exposes an explicit convention instead of averaging incompatible definitions. This policy governs the ecological detector, Stage 3 scale and MSD distinctions, Stage 4 robust source differences, Stage 5 separation between prepared spatial weights, SPADE variance decomposition and IDSA fuzzy interaction zones, and Stage 6 separation between the published SRS-GD estimand, information-consistency distributions and ambiguous reference-source operations.
