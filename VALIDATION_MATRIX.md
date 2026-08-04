# Validation matrix

Every public statistical method must satisfy four evidence layers.

## Layer A — Analytical and property validation

Exact or hand-calculated examples; range and boundary behaviour; row-order and label invariance; equivalent formula checks; explicit errors for undefined estimands; deterministic behaviour for fixed random seeds.

## Layer B — Static cross-language reference fixtures

Fixtures are generated outside the pyGeoHet test runtime and committed as CSV/JSON with provenance: reference package and version/commit, source function and arguments, input data hash, generation command, expected output, tolerance, and known convention differences. Tests never invoke R, MATLAB, QGIS or a competing Python package.

## Layer C — Simulation validation

Null association, perfect or near-perfect stratification, nonlinear association, unbalanced strata, missingness, small strata, outliers, perturbations, and spatial/temporal dependence when relevant.

## Layer D — Published-case reproduction

Each model family must reproduce at least one documented paper or official-software case with data provenance and a comparison narrative.

## Current matrix

| Method | Analytical | Cross-language | Simulation | Published case | Status |
|---|---:|---:|---:|---:|---|
| q-statistic | yes | pending fixture | basic tests | pending | provisional |
| Factor detector | yes | pending fixture | basic tests | pending | provisional |
| Interaction detector | pending | pending | pending | pending | Stage 2 |
| Risk detector | pending | pending | pending | pending | Stage 2 |
| Ecological detector | pending | pending | pending | pending | Stage 2 |

“Provisional” means implemented and tested but not yet promoted to stable because the independent fixture and published-case layers are incomplete.
