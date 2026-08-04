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

## NTD fixture

`tests/fixtures/reference/ntd_classic_reference.json` contains expected outputs and the SHA-256 hash of the non-redistributed input. `tools/validate_ntd_reference.py` verifies the hash and reruns all classical detectors.

## Stage 3A validation gap

Stage 3A has analytical, boundary, failure-mode and integrated workflow tests. It is not labelled fully validated until static reference fixtures and at least one published OPGD case are added. Spatial-scale OPGD and MSD remain unimplemented rather than being inferred from the univariate search.

“Validated with convention split” means the primary scientific convention and the compatibility convention are both explicit, independently tested, and not numerically conflated.
