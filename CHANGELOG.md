# Changelog

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
