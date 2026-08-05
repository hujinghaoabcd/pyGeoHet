# Ten-stage development roadmap

The algorithms are mostly compact; the work is divided into ten stages so that statistical definitions, validation evidence, documentation, and handoff state remain reviewable. A stage is complete only when its code, tests, examples, model manual, validation record, status documents, and handoff are all updated.

## Stage 1 - Foundation and q-statistic (`0.0.1`)

Package, docs, tests and CI skeleton; numerical contracts and typed immutable results; q-statistic, noncentral-F significance and factor detector; q bounds, invariance, q-R2 equivalence and missing-data tests.

**Status:** complete and merged.

## Stage 2 - Classical four-detector workflow (`0.0.2`)

Collision-safe overlays; five interaction classes and common-sample interaction detector; Welch risk detector; ecological detector with primary two-sided and explicit upper-tail compatibility conventions; integrated `GeoDetector`; NTD static reference fixture and case reproduction.

**Status:** complete and merged.

## Stage 3 - Stratification, optimal discretization and scale (`0.0.5`)

### Stage 3A - Univariate stratification and OPGD (`0.0.3`)

Equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard-deviation and head/tail breaks; immutable stratification results; joint-sample candidate evaluation; complete audit tables; deterministic q ties; optimal univariate discretization and integrated OPGD.

**Status:** complete and merged.

### Stage 3B - Spatial-scale OPGD (`0.0.4`)

Primary-paper 90% q-quantile scoring across explicitly prepared supports; optional legacy-GD significance eligibility; precomputed-result and integrated OPGD interfaces; common-factor checks; explicit ties and failed-scale evidence. Automatic geographic aggregation remains upstream.

**Status:** complete and merged; external scale fixture and published-case reproduction remain validation debt.

### Stage 3C - Multiscale discretization (`0.0.5`)

Supervised bivariate cut search by q maximization; explicit explanatory-variable value grid; exact global-search mode; paper-style coarse-to-fine upscaling/downscaling; one refined cut per mapped epsilon neighbourhood; cached interval objectives; immutable scale-path evidence; missing/sample/stratum contracts and deterministic ties.

**Status:** complete and merged; author Figshare parity and a published-case reproduction remain validation debt.

## Stage 4 - Robust detector family (`0.0.6`)

Stable explanatory-variable ordering; duplicate-value-safe admissible boundaries; exact least-squares variance change-point segmentation; prefix-sum dynamic programming; B-value; explicit marginal-gain and maximum-B class-count selection; RGD and RID composition with the classical detector core; independent brute-force, rank-invariance, missingness and integration tests.

**Status:** complete and merged. External author/gdverse fixtures, published RGD/RID cases, outlier perturbation experiments and selection-uncertainty analysis remain validation debt.

## Stage 5 - Spatial-dependence detector family

### Stage 5A - Spatial variance and SPADE (`0.0.7`)

Prepared dense spatial-weight contracts; weighted spatial variance; PSD for categorical strata; CPSD information compensation; PSMD over explicit discretization levels; integrated SPADE; conditional permutation inference; immutable audit results; NTD soiltype reference validation.

The implementation keeps geometry processing and weight construction upstream. It does not silently choose a CRS, centroid, distance metric, neighbourhood, normalization or symmetrization rule.

**Status:** complete and merged in PR #7. The categorical PSD path matches the pinned gdverse NTD reference at six decimal places. Continuous published-case reproduction, static CPSD/PSMD tables, sparse weights and uncertainty analysis remain validation debt.

### Stage 5B - Fuzzy overlay and IDSA (`0.0.8`)

Collision-safe fuzzy factor-stratum labels; response-risk membership normalization; explicit fuzzy AND/OR and deterministic ties; spatial interactive power `theta`; information-retention component `phi`; `PID = theta / phi`; continuous-factor discretization strategy; pairwise and multivariate IDSA audit tables; independent manual fixtures and reference-case reproduction.

**Status:** complete and merged in PR #8. Analytical tests and source audits are complete. Pinned external PID fixtures, LOESS-selector comparison and a published IDSA case remain validation debt.

## Stage 6 - Categorical and information-consistency SSH (`0.4.0`)

### Stage 6A - Spatial rough-set geographical detectors (`0.0.9`)

Nominal-target spatial information systems; focal-object local regions; exact multifeature indiscernibility; local positive regions; average local explanatory power `D`; spatial entropy `SE`; factor, ecological and interaction detectors; paired inference and immutable local evidence.

**Status:** implementation and final CI complete in PR #9. The paper Figure 1 local values, `D`, `SE` and refinement monotonicity are reproduced. Published Baltimore/Cincinnati cases and a pinned gdverse compatibility table remain validation debt.

### Stage 6B - Information-consistency SSH (`0.0.10`)

Nominal `IN-SSH` by normalized mutual information and continuous `IC-SSH` by stratum-weighted arctangent-normalized relative entropy; corrected seeded permutation inference; common histogram support and explicit density contracts.

**Status:** complete and merged in PR #10. Hand-calculated nominal and continuous fixtures, shared-edge contracts, corrected seeded permutations, common-sample workflows, public exports and the model manual are complete. Static `sshicm` candidate tables and a published-case reproduction remain validation debt.

### Stage 6C - Spatially weighted mutual information

Spatial probability adjustment, weighted entropy and mutual information only after the complete 2026 paper equations, implementation evidence and a numerical fixture are pinned.

**Status:** evidence audit complete and implementation blocked. The accessible official source confirms only the high-level sequence of discretization, spatial-autocorrelation probability adjustment and entropy/mutual-information calculation. The exact adjustment, spatial support, discretization, normalization, interaction and inference equations are not pinned; no authoritative code or numerical fixture was found. No provisional API or version bump is permitted. See `docs/references/swmi-evidence-audit.md`.

## Stage 7 - Multivariate stratification and contribution (`0.5.0`)

### Stage 7A - GOZH evidence and numerical contract

Audit progressive geographical-zone optimization, merge and stopping rules, individual and interactive determinants, scale and search complexity, source licences, and published numerical cases before implementation.

**Status:** next active batch after the Stage 6C evidence-gate PR is merged.

### Stage 7B - LESH and Shapley contribution

Separate multivariate-zone construction from contribution allocation; freeze coalition values, baseline, exact/approximate Shapley routes, direct and interaction interpretation, and uncertainty evidence.

### Stage 7C - OMGD multivariate stratification and scale

Univariate and clustering-based multivariate stratification; factor-combination search; spatial-scale detector; deterministic search budgets and external author-code fixtures.

## Stage 8 - Local and structural SSH (`0.6.0`)

LISP, GPI where evidence is sufficient, local geometry structure, UEP, local maps and uncertainty-aware exports.

## Stage 9 - Regression, observation bias and unified framework (`0.8.0`)

q-R2 regression interface, spatial-econometric correction adapters, direct/indirect Shapley decomposition, SSH goodness-of-fit, confounding diagnostics, EQ-statistic and SOH where formulas and code can be verified.

## Stage 10 - Temporal-lag research, integration and 1.0 (`1.0.0`)

Experimental cross-lag SSH estimand, lag search and selection-aware inference, static/dynamic stratification, temporal and spatial dependence controls, full API audit, benchmarks, bilingual manuals and stable release.

## Scope rule

A method whose paper, formula, code licence, or validation data cannot be verified remains planned or experimental; gaps are not silently filled from neighbouring methods. Reference source archives are inspected for numerical behaviour and software contracts, but code is not copied line by line into the MIT-licensed package. Correct estimands and reproducible outputs take priority over mechanical source parity.
