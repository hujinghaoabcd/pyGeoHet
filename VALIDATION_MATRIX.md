# Validation matrix

Every public statistical method must satisfy four evidence layers.

## Layer A - Analytical and property validation

Exact or hand-calculated examples; range and boundary behaviour; row-order and label invariance; equivalent formula checks; explicit errors for undefined estimands; deterministic behaviour for fixed random seeds.

## Layer B - Static cross-language reference fixtures

Fixtures are generated outside the pyGeoHet test runtime and committed as CSV/JSON with provenance: reference package and version/commit, source function and arguments, input data hash, generation command, expected output, tolerance, and known convention differences. Tests never invoke R, MATLAB, QGIS or a competing Python package.

## Layer C - Simulation validation

Null association, perfect or near-perfect stratification, nonlinear association, unbalanced strata, missingness, small strata, outliers, perturbations, and spatial/temporal dependence when relevant.

## Layer D - Published-case reproduction

Each model family must reproduce at least one documented paper or official-software case with data provenance and a comparison narrative.

## Current matrix

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| q-statistic | yes | NTD q/p fixture | yes | NTD | validated |
| Factor detector | yes | GD/gdverse NTD fixture | yes | NTD | validated |
| Interaction detector | five classes, tolerance, collision test | gdverse labels | joint-missing and singleton-overlay tests | NTD | validated |
| Risk detector | manual Welch equality | gdverse significance counts | zero-variance and matrix tests | NTD | validated |
| Ecological detector | primary F formula, reciprocal invariance | gdverse `greater` compatibility | tail and zero-dispersion tests | NTD | validated with convention split |
| Integrated GeoDetector | workflow composition | NTD whole-workflow fixture | one/two-factor tests | NTD | validated |
| Equal interval | exact cuts and lower-boundary test | source convention reviewed; fixture pending | missing alignment and collapsed-layer audit | pending | implemented, provisional |
| Quantile | lower-quantile and no-tie-split tests | source convention reviewed; fixture pending | duplicate-cut collapse | pending | implemented, provisional |
| Natural breaks | clear-cluster Fisher-Jenks test | independent/reference fixture pending | weighted duplicate values and deterministic ties | pending | implemented, provisional |
| Geometric interval | ratio and upper-boundary contract | source convention reviewed; fixture pending | nonpositive-domain rejection | pending | implemented, provisional |
| Standard deviation | sample-SD cut contract | source convention reviewed; fixture pending | collapsed/empty layer audit | pending | implemented, provisional |
| Head/tail breaks | recursive-mean and threshold contract | source convention reviewed; fixture pending | automatic class count and stopping tests | pending | implemented, provisional |
| Optimal stratification | direct q evaluation and deterministic tie rule | gdverse/GD candidate fixture pending | rejected candidates and joint-complete-case tests | pending | implemented, provisional |
| Integrated OPGD | workflow composition | external optimum fixture pending | multi-factor, one-factor and all-invalid tests | OPGD case pending | implemented, provisional |
| Primary-paper scale score | hand-calculated linear 90% quantiles and maximum selection | paper/GD convention audit; fixture pending | equal-score ties, scale validation and common-factor checks | vegetation/H1N1 reproduction pending | implemented, provisional |
| Legacy GD scale eligibility | p-filter plus 90% q quantile | `GD::sesu` pinned-source fixture pending | missing p-value and no-eligible-factor tests | pending | implemented, provisional |
| SpatialScaleOPGD | scale-specific OPGD composition | external multi-scale fixture pending | failed scales, one-valid-scale and aligned/misaligned synthetic supports | OPGD scale case pending | implemented, provisional |
| gdverse LOESS scale heuristic | source formula audited | pinned gdverse/sdsfun fixture pending | threshold crossings and fallback pending | pending | documented only |
| MSD exact search | equality with independent exhaustive enumeration | author Figshare fixture pending | cut membership, ties, minimum size and missing sample | MSD case pending | implemented, provisional |
| MSD coarse-to-fine search | paper-derived 6 -> 3 -> 1 mapping contract | author scale-path fixture pending | known-threshold recovery, invalid scales and audit tables | MSD case pending | implemented, provisional |
| Robust fixed-K discretization | equality with independent brute-force partitions; B=q identity | author/gdverse cut and B fixture pending | duplicate-x indivisibility, rank invariance, missingness and invalid sizes | RGD case pending | implemented, provisional |
| Robust class-count optimization | explicit marginal-gain and maximum-B rules | gdverse/author class-count table pending | rejected counts, threshold crossing and deterministic ties | RGD case pending | implemented, provisional |
| Integrated RGD | robust labels reproduce factor q/B and compose with classical workflow | pinned author/gdverse output pending | one/multi-factor integration and aligned labels | published RGD case pending | implemented, provisional |
| Integrated RID | robust labels plus collision-safe pairwise interaction | pinned gdverse RID fixture pending | at-least-two-factor, joint sample and interaction integration | published RID case pending | implemented, provisional |
| Spatial variance | hand-computed weighted semivariance | sdsfun formula/source audit | global weight scaling, directed weights, missing-axis alignment and islands | SPADE NTD support calculation | implemented and externally checked |
| PSD | direct stratum decomposition | gdverse NTD soiltype fixture: 0.2566528295 | simultaneous row/weight permutation, minimum strata and island failures | NTD SPADE case | validated for pinned case |
| CPSD | ratio identity when response equals information variable | gdverse/sdsfun formula audit | zero denominator and common-sample tests | pending | implemented, provisional |
| PSMD | exact mean of accepted CPSD levels | reference workflow audited; static table pending | invalid-level retention, minimum accepted levels and seeded permutations | pending | implemented, provisional |
| Integrated SPADE | categorical PSD plus continuous PSMD composition | NTD categorical path checked | mixed factor typing and deterministic seeds | partial NTD | implemented, provisional |
| IDSA fuzzy overlay and PID | manual labels and direct theta/phi equality | fixture pending | ties, normalization, permutations, subset search and missing rows | pending | implemented, provisional |
| SRS-GD | Figure 1 local quality, D and SE | paper/source audit; external compatibility table pending | tuple monotonicity, adjacency permutation, islands, missing axes and nominal guards | Baltimore/Cincinnati pending | implemented, provisional |
| Nominal IN-SSH | perfect/null extremes and hand contingency calculation | pinned `sshicm` source audited; static table pending | relabeling, constant target, missing scope and corrected seeded permutations | pending | implemented, provisional |
| Continuous IC-SSH | fixed-bin `KL=log(2)` example and zero-divergence case | pinned `sshicm` source audited; static table pending | affine invariance, five bin methods, fixed-edge permutations, support and small-stratum failures | pending | implemented, provisional |
| InformationConsistency workflow | scalar estimators composed on one joint sample | external multi-factor table pending | factor ordering, common missing mask and public API tests | pending | implemented, provisional |

## NTD fixtures

`tests/fixtures/reference/ntd_classic_reference.json` contains expected classical outputs and the SHA-256 hash of the non-redistributed input. `tools/validate_ntd_reference.py` verifies the hash and reruns all classical detectors.

`tests/fixtures/reference/ntd_spade_reference.json` records the gdverse `NTDs.gpkg` SHA-256, preparation contract and expected soiltype PSD without redistributing the GPKG. `tools/validate_ntd_spade_reference.py` reconstructs disease centroids, supporting-layer joins and inverse-distance-squared weights when the separately obtained GPKG is available.

## Stage 3 validation gaps

Stage 3A has analytical, boundary, failure-mode and integrated workflow tests but still needs stable external method fixtures and a published OPGD reproduction.

Stage 3B has analytical scale-score tests, significance-policy tests, deterministic ties, common-factor validation, failed-scale retention and integrated prepared-support OPGD tests. It is not labelled fully externally validated until a static GD/gdverse scale fixture and at least one published multi-scale OPGD case are reproduced. Automatic spatial-support construction and the newer gdverse LOESS heuristic are not silently inferred.

Stage 3C has an independent exhaustive-enumeration oracle for exact searches, paper-style scale mapping, a synthetic 6 -> 3 -> 1 threshold recovery, deterministic ties, joint missing-data tests and full scale-path evidence. MSD still needs the reported Figshare archive audit, static author-output fixtures and a published-case reproduction.

## Stage 4 validation gaps

Stage 4 has an independent brute-force oracle for fixed-zone ordered partitions, B=q equality, monotone-rank invariance, duplicate-value safety, missing-row reconstruction, explicit minimum-size failures, multi-factor RGD composition and RID interaction integration.

It still needs pinned author/gdverse fixtures, published RGD/RID examples, perturbation/outlier simulations and class-count selection-stability analysis.

## Stage 5A validation state and gaps

Stage 5A has analytical and property tests for every public statistic. The categorical PSD route is also checked against the gdverse NTD reference case:

```text
pyGeoHet full precision: 0.2566528294856155
gdverse test expectation: 0.256653
```

The preparation uses 185 complete disease-centroid observations and an inverse Euclidean distance-squared matrix. The raw GPKG is not redistributed.

Remaining work:

1. pin static CPSD and PSMD tables from a maintained reference environment;
2. reproduce a published continuous-factor SPADE example;
3. test sparse and strongly asymmetric weights once those input forms are public;
4. study sensitivity to neighbourhood and weight construction outside the core statistic;
5. quantify PSMD level-selection and discretization uncertainty;
6. add larger spatial simulations for null, clustered and boundary-sensitive processes.

“Validated with convention split” means the primary scientific convention and the compatibility convention are both explicit, independently tested, and not numerically conflated.

## Stage 5B validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Fuzzy overlay | manual AND/OR labels and min-max memberships | sdsfun source contract audited | ties, constant risk, missing rows and collision-safe labels | pending | implemented, provisional |
| Fixed PID | direct theta/phi equality | gdverse `pid_idsa` formula audited | canonical-code invariance, zero denominator and invalid zones | pending | implemented, provisional |
| IDSA permutation | deterministic recomputation of response-derived overlay | external null table pending | valid/failed permutation accounting | pending | implemented, provisional |
| CPSD discretization | maximum-CPSD and simplicity tie rule | reference candidate table pending | rejected candidates and degenerate levels | pending | implemented, provisional |
| Integrated IDSA | greedy and exhaustive subset search | gdverse final-output fixture pending | joint missing sample, bounded search and failure retention | pending | implemented, provisional |

Stage 5B still requires a pinned gdverse/sdsfun environment, a static fuzzy-zone table, external theta/phi/PID outputs, comparison of maximum-CPSD and LOESS selectors, a published IDSA reproduction, and selection-stability experiments. No full external-validation claim is made before those records exist.

## Stage 6A validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Local rough-set measure | Figure 1 local regions, positive regions and quality | primary paper fixture; gdverse discrepancy audit | diagonal invariance, row/adjacency permutation, islands and missing axes | pending | implemented, provisional |
| Average local power `D` | hand mean `0.7325757575757575` for `a1` | independent paper transcription | exact refinement monotonicity and nominal-input guards | pending | implemented, provisional |
| Spatial entropy `SE` | hand entropy `3.245554302578003` for `a1` | independent paper transcription | normalized entropy and undefined all-zero contract | pending | implemented, provisional |
| SRS factor detector | one-sample local-quality inference | gdverse factor output pending | common sample, seeded subset and public API tests | Baltimore/Cincinnati pending | implemented, provisional |
| SRS ecological detector | paired local-quality difference | Welch compatibility table pending | equal/unequal factors and common-location sampling | Baltimore/Cincinnati pending | implemented, provisional |
| SRS interaction detector | `{a1,a2}` D/SE and nonnegative gain | gdverse interaction output pending | exact tuple refinement, entropy direction and zero gain | Baltimore/Cincinnati pending | implemented, provisional |
| Integrated SRSGeoDetector | factor/ecological/interaction composition | external workflow fixture pending | three-factor Figure 1 workflow | pending | implemented, provisional |

Stage 6A follows the published spatial rough-set estimand. Known differences in the reviewed reference C++ implementation are documented rather than hidden. Remaining work includes pinned gdverse input/output fixtures, published Baltimore and Cincinnati reproductions, larger nominal simulations, neighbourhood sensitivity analysis and inference that accounts for dependence among overlapping local regions.

## Stage 6B validation state and gaps

| Method | Analytical | Cross-language/static | Simulation/edge cases | Published case | Status |
|---|---:|---:|---:|---:|---|
| Nominal IN-SSH | `IN=1`, `IN=0`, and a hand-calculated partial table | `stscl/sshicm` commit pinned; static outputs pending | category relabeling, zero entropy, missing policy and corrected seeded permutations | pending | implemented, provisional |
| Continuous IC-SSH | separated fixed-bin strata with `KL=log(2)` and identical distributions with `IC=0` | histogram/relative-entropy source audited; static outputs pending | shared support, explicit edges, five automatic rules, affine invariance, small strata and fixed-edge permutations | pending | implemented, provisional |
| Multi-factor workflow | direct scalar/workflow equality on one joint sample | external candidate ranking pending | common complete cases, factor ordering and functional/class APIs | pending | implemented, provisional |

Stage 6B deliberately differs from the reviewed source where that source mixes logarithm bases, uses uncorrected `exceedances/B` p values or creates incompatible global and stratum histogram supports. Remaining work is to pin static candidate and final-output tables from the audited revision, reproduce a published application, add larger null/power simulations, and quantify sensitivity to histogram selection. No fully external-validation claim is made before those records exist.

