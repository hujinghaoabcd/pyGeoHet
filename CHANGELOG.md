# Changelog

## Unreleased - Stage 6C evidence audit

### Added

- a dedicated SWMI evidence-gate audit with known facts, unresolved equations, search record, implementation gate and reopening procedure;
- an explicit Stage 7A/7B/7C split for GOZH, LESH/Shapley and OMGD.

### Changed

- SWMI is recorded as implementation-blocked rather than merely planned;
- no SWMI code, placeholder API or version change is introduced;
- Stage 7A GOZH evidence and numerical-contract review becomes the next active batch.

## 0.0.10 - 2026-08-05

### Added

- nominal `nominal_information_consistency()` using normalized mutual information;
- continuous `continuous_information_consistency()` using stratum-weighted arctangent-normalized KL divergence;
- shared global/stratum histogram support with Sturges, square-root, Rice, Scott and Freedman-Diaconis rules;
- explicit integer and edge-sequence histogram contracts;
- immutable contingency, entropy, histogram, KL-contribution and multi-factor result objects;
- `InformationConsistency` / `information_consistency()` common-sample workflows;
- corrected seeded permutation inference with fixed continuous edges;
- analytical perfect, null, partial contingency, `KL=log(2)` and zero-divergence tests;
- label and affine invariance, missing-scope, small-stratum, support and public API tests;
- tenth runnable example, model manual and expanded Stage 6 source audit.

### Changed

- package development version advanced to `0.0.10`;
- public API exports nominal, continuous and integrated information-consistency interfaces;
- CI runs ten public examples;
- entropy components use one natural-log convention rather than mixed bases;
- continuous density comparison uses one shared support rather than per-stratum supports;
- permutation p values use `(1 + exceedances) / (B + 1)`;
- Stage 6C SWMI remains evidence-gated and Stage 7 becomes the next implementable family after the evidence review.

## 0.0.9 - 2026-08-05

### Added

- paper-aligned spatial rough-set numerical core for nominal targets;
- prepared binary adjacency validation with explicit symmetry and island evidence;
- local regions containing the focal object and its supplied neighbours;
- exact tuple-based local indiscernibility and decision-consistent positive regions;
- immutable `SpatialRoughSetResult` with local quality, region sizes, `D` and `SE`;
- public `spatial_rough_set_measure()` and SRS factor, ecological and interaction detectors;
- integrated `SRSGeoDetector` / `srsgd` workflow;
- paired common-location inference and reproducible paper-style subsampling;
- Figure 1 hand-calculated local-quality, `D`, `SE` and monotonicity fixtures;
- row-and-adjacency permutation, island, missing-axis and discrete-input tests;
- Stage 6 evidence audit, SRS-GD model manual, public example and API regression protection.

### Changed

- package development version advanced to `0.0.9`;
- CI runs nine public examples;
- Stage 6 is split into 6A SRS-GD, 6B information consistency and evidence-gated 6C SWMI;
- the published SRS-GD estimand is primary when reviewed reference C++ behaviour is ambiguous;
- multifeature indiscernibility requires equality on every feature rather than any-coordinate matching;
- adjacency diagonal values are ignored and the focal object is added exactly once;
- geometry-to-adjacency construction remains an explicit upstream responsibility;
- final CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13;
- Ruff, Black, mypy, nine examples, wheel build and source-distribution build passed;
- Stage 6B information-consistency SSH becomes the next active batch.

## 0.0.8 - 2026-08-05

### Added

- collision-safe fuzzy AND/OR zones through `fuzzy_overlay()`;
- global min-max normalization of factor-stratum response risks;
- explicit first/last membership tie policies and tied-row evidence;
- fixed-discretization `power_interactive_determinant()` with `PID = theta / phi`;
- canonical ordinal encoding for externally supplied discrete class codes;
- CPSD-guided `optimize_spatial_discretization()` with complete candidate tables;
- integrated `IDSA` / `idsa` with greedy and bounded exhaustive subset search;
- response-permutation inference that recomputes fuzzy memberships and zones;
- immutable fuzzy-risk, overlay, PID, discretization and combination results;
- analytical fuzzy-label, component, invariance, search and missing-data tests;
- IDSA example, model manual and detailed paper/source audit.

### Changed

- package development version advanced to `0.0.8`;
- public API now exports fuzzy overlay, PID, spatial discretization and IDSA interfaces;
- CI runs eight public examples;
- continuous-factor selection uses explicit maximum CPSD with deterministic simplicity ties;
- reference LOESS selection remains a separate unimplemented compatibility estimator;
- Stage 6 categorical and information-consistency SSH becomes the next active stage.

## 0.0.7 - 2026-08-05

### Added

- auditable weighted spatial variance through `spatial_variance()`;
- explicit prepared dense spatial-weight validation with diagonal, symmetry and island evidence;
- power of spatial determinant through `power_spatial_determinant()`;
- compensated power of spatial determinant through `compensated_spatial_determinant()`;
- multilevel spatial determinant through `multilevel_spatial_determinant()`;
- integrated `SPADE` / `spade` workflow for explicit continuous and categorical factors;
- immutable spatial-variance, PSD, CPSD, PSMD candidate and integrated result objects;
- optional seeded permutation inference for PSD and PSMD;
- complete PSMD candidate tables retaining invalid discretization levels and reasons;
- hand-computed, invariance, missing-alignment, island, ratio and workflow tests;
- provenance-only NTD SPADE reference fixture and offline GPKG validator;
- SPADE model manual, source audit and public example.

### Changed

- package development version advanced to `0.0.7`;
- public API now exports spatial variance, PSD, CPSD, PSMD and SPADE interfaces;
- CI runs seven public examples;
- spatial weights remain explicit upstream inputs; the package does not infer CRS, centroids, neighbours, distance units or row standardization;
- reference gdverse/sdsfun code is used for formula and behavioural validation, not copied or called at runtime;
- Stage 5B IDSA becomes the next active development batch.

## 0.0.6 - 2026-08-05

### Added

- exact ordered variance-change-point discretization through `robust_discretize()`;
- prefix-sum segment costs and dynamic-programming backtracking for a fixed stratum count;
- distinct-value boundary constraints so equal explanatory values are never split;
- immutable robust discretization, class-count candidate and optimization result objects;
- RGD B-value reporting through the same variance decomposition as q;
- `marginal_gain` and `max_b` class-count selection policies;
- integrated `RGD` / `rgd` workflow for one or more continuous factors;
- integrated `RID` / `rid` workflow using robust zones and collision-safe interaction detection;
- aligned missing-row reconstruction, duplicate-value evidence and deterministic cut ties;
- independent brute-force, rank-invariance, duplicate-value, missing-data and integration tests;
- robust detector example, model manual and paper/source-code audit.

### Changed

- package development version advanced to `0.0.6`;
- public API now exports robust discretization, RGD and RID interfaces and results;
- CI runs six public examples;
- Stage 4 uses an independently written numerical core rather than a runtime dependency on `ruptures`, R, GD or gdverse;
- author/gdverse behaviour is treated as reference evidence, while explicit improvements such as duplicate-value safety are documented;
- Stage 5 spatial-dependence detector development becomes the next active stage.

## 0.0.5 - 2026-08-05

### Added

- supervised multiscale discretization through `MSD` and `multiscale_discretize()`;
- exact global-search mode over observed unique-value boundaries;
- paper-style coarse-to-fine explanatory-variable value-grid search;
- explicit upscale, buffer-scale, epsilon, grid-origin and base-resolution contracts;
- one refined cut selected from each mapped neighbourhood;
- cached interval within-stratum objectives and deterministic cut-tuple ties;
- immutable `MSDResult` and `MSDScaleResult` audit objects;
- per-scale candidate counts, selected cuts, q, within-stratum sum of squares and failure evidence;
- exhaustive-enumeration, known-threshold, missing-data, boundary, tie and invalid-contract tests;
- runnable MSD example, model manual and paper/source-code audit.

### Changed

- package development version advanced to `0.0.5`;
- public API now exports MSD interfaces and results;
- CI runs five public examples;
- Stage 3 is complete in implementation terms and Stage 4 robust detector development is next;
- author Figshare parity and a published MSD case are retained as explicit validation debt rather than assumed compatibility.

## 0.0.4 - 2026-08-05

### Added

- immutable spatial-scale candidate, selection and integrated OPGD result objects;
- primary-paper spatial-scale scoring based on the 90% quantile of factor q values;
- optional significance filtering matching the legacy `GD::sesu()` eligibility convention;
- explicit mean-q scale scoring for descriptive and compatibility analysis;
- deterministic scale-score tie policies;
- strict common-factor validation across prepared spatial supports;
- `compare_spatial_scales()` for precomputed factor, GeoDetector or OPGD results;
- `SpatialScaleOPGD` for running OPGD on explicit scale-specific datasets;
- scale-level failure retention, tests, documentation and runnable example.

### Changed

- package development version advanced to `0.0.4`;
- public API now exports spatial-scale comparison interfaces;
- CI runs all four public examples;
- spatial support aggregation remains an explicit upstream responsibility;
- the 2020 paper convention, legacy GD significance filter and newer gdverse mean-plus-LOESS heuristic are documented as distinct estimators.

## 0.0.3 - 2026-08-05

### Added

- audited continuous-variable stratification subsystem;
- equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard-deviation and head/tail breaks;
- immutable stratification, candidate-evaluation and optimal-search result objects;
- duplicate-cut, collapsed-stratum, boundary-convention and rejection evidence;
- joint-complete-case q-guided method-by-class-count optimization;
- complete candidate tables retaining accepted and rejected candidates;
- deterministic q-tie policy;
- integrated `OPGD` / `opgd` workflow for continuous explanatory variables;
- Stage 3A tests, model documentation and runnable example;
- GitHub Actions concurrency control that cancels superseded pull-request runs.

### Changed

- package development version advanced to `0.0.3`;
- public API now exports stratification and OPGD interfaces;
- Stage 3 is split into Stage 3A univariate stratification/OPGD and later spatial-scale/MSD batches.

## 0.0.2 - 2026-08-05

### Added

- collision-safe tuple overlay utility;
- explicit five-class interaction classifier with floating tolerances;
- pairwise interaction detector using one joint complete-case sample;
- risk detector with stratum means, sample variances, Welch tests and symmetric p-value matrices;
- ecological detector using the primary-paper F ratio;
- default two-sided ecological test and explicit `greater` compatibility mode;
- integrated `GeoDetector` / `geodetector` workflow;
- immutable interaction, risk, ecological and integrated result objects;
- `min_overlay_size` policy for retaining natural singleton intersection cells;
- NTD static fixture, SHA-256 validator and validation report;
- full classical-workflow example and model documentation.

### Changed

- factor-column names are normalized to strings and must remain unique after normalization;
- Stage 2 public APIs are exported from `pygeohet`;
- project status, roadmap, validation matrix, numerical conventions and handoff documents now target Stage 3.

## 0.0.1 - 2026-08-05

### Added

- project, packaging, documentation, testing, and CI foundations;
- immutable `QStatisticResult` and `FactorDetectorResult` objects;
- direct sums-of-squares q-statistic implementation;
- classical noncentral-F significance calculation;
- strict missing-value, constant-response, and small-stratum validation;
- factor detector for one or multiple categorical explanatory variables;
- analytical and invariance tests, including q-R2 equivalence;
- ten-stage roadmap, model inventory, validation matrix, decisions log, and next-conversation handoff system.
