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
| Stratification methods | pending | pending | pending | pending | Stage 3 |

## NTD fixture

`tests/fixtures/reference/ntd_classic_reference.json` contains expected outputs and the SHA-256 hash of the non-redistributed input. `tools/validate_ntd_reference.py` verifies the hash and reruns all classical detectors.

“Validated with convention split” means the primary scientific convention and the compatibility convention are both explicit, independently tested, and not numerically conflated.
