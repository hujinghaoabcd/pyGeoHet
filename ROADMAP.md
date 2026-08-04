# Ten-stage development roadmap

The algorithms are mostly compact; the work is divided into ten stages so that statistical definitions, validation evidence, documentation, and handoff state remain reviewable. A stage is complete only when its code, tests, examples, model manual, validation record, status documents, and handoff are all updated.

## Stage 1 - Foundation and q-statistic (`0.0.1`)

Package, docs, tests and CI skeleton; numerical contracts and typed immutable results; q-statistic, noncentral-F significance and factor detector; q bounds, invariance, q-R2 equivalence and missing-data tests.

**Status:** complete and merged.

## Stage 2 - Classical four-detector workflow (`0.0.2`)

Collision-safe overlays; five interaction classes and common-sample interaction detector; Welch risk detector; ecological detector with primary two-sided and explicit upper-tail compatibility conventions; integrated `GeoDetector`; NTD static reference fixture and case reproduction.

**Status:** complete and merged.

## Stage 3 - Stratification, optimal discretization and scale (`0.1.0` target)

### Stage 3A - Univariate stratification and OPGD (`0.0.3`)

Equal interval, quantile, weighted Fisher-Jenks natural breaks, geometric interval, standard-deviation and head/tail breaks; immutable stratification results; joint-sample candidate evaluation; complete audit tables; deterministic q ties; optimal univariate discretization and integrated OPGD.

**Status:** implemented in the Stage 3A pull request; final cross-platform merge gate required.

### Stage 3B - Spatial-scale optimization

Freeze the primary-source numerical contract for scale candidates, neighborhood construction, edge handling, sample scope and deterministic ties. Implement spatial-scale candidate tables and reference fixtures without conflating scale search with univariate discretization.

### Stage 3C - Multiscale discretization (MSD)

Implement MSD only after the paper and reference code establish its objective, candidate construction and relationship to OPGD. Retain failed candidates, complexity information and selection evidence.

## Stage 4 - Robust detector family (`0.2.0`)

Rank transformation, variance change-point segmentation, dynamic-programming robust discretization, RGD B-value and robust interaction detector (RID), with perturbation and outlier experiments.

## Stage 5 - Spatial-dependence detector family (`0.3.0`)

Spatial-weight and distance contracts; spatial variance and multilevel information loss; SPADE and IDSA, including fuzzy overlay.

## Stage 6 - Categorical and information-consistency SSH (`0.4.0`)

Spatial rough-set GD for nominal targets; continuous and nominal information-consistency measures; permutation inference; SWMI after primary-source verification.

## Stage 7 - Multivariate stratification and contribution (`0.5.0`)

GOZH, LESH/Shapley contribution allocation, OMGD univariate and clustering-based multivariate stratification, and search-complexity controls.

## Stage 8 - Local and structural SSH (`0.6.0`)

LISP, GPI where evidence is sufficient, local geometry structure, UEP, local maps and uncertainty-aware exports.

## Stage 9 - Regression, observation bias and unified framework (`0.8.0`)

q-R2 regression interface, spatial-econometric correction adapters, direct/indirect Shapley decomposition, SSH goodness-of-fit, confounding diagnostics, EQ-statistic and SOH where formulas and code can be verified.

## Stage 10 - Temporal-lag research, integration and 1.0 (`1.0.0`)

Experimental cross-lag SSH estimand, lag search and selection-aware inference, static/dynamic stratification, temporal and spatial dependence controls, full API audit, benchmarks, bilingual manuals and stable release.

## Scope rule

A method whose paper, formula, code licence, or validation data cannot be verified remains planned or experimental; gaps are not silently filled from neighbouring methods.
