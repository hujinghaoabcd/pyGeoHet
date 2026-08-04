# Changelog

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
