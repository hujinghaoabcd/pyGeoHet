# HANDOFF - pyGeoHet Stage 5A baseline

Date: 2026-08-05

## 1. Authoritative continuation source

After PR #7 is merged, the latest `main` branch of `hujinghaoabcd/pyGeoHet` is the only authoritative baseline. A new conversation must fetch the latest `main` commit SHA before editing. Do not reconstruct Stage 5A from chat text, temporary extracts or old ZIP copies.

Read in this order:

1. `HANDOFF_NEXT_CONVERSATION.md`;
2. `PROJECT_STATUS.md`;
3. `DECISIONS.md`;
4. `docs/models/spade.md`;
5. `docs/references/spade-idsa-code-audit.md`;
6. `VALIDATION_MATRIX.md`;
7. `ROADMAP.md`;
8. `MODEL_INVENTORY.md`;
9. `THIRD_PARTY_NOTICES.md`;
10. the IDSA paper and pinned reference source used for Stage 5B.

## 2. Completed baseline

Stages 1-4 remain implemented: classical GeoDetector, OPGD, prepared-support scale comparison, MSD, robust discretization, RGD and RID.

Stage 5A adds version `0.0.7` and:

- `SpatialVarianceResult` and `spatial_variance()`;
- `SpatialStratumVariance`;
- `PowerSpatialDeterminantResult` and `power_spatial_determinant()`;
- `CompensatedSpatialDeterminantResult` and `compensated_spatial_determinant()`;
- `MultilevelSpatialCandidate`;
- `MultilevelSpatialDeterminantResult` and `multilevel_spatial_determinant()`;
- `SPADE`, `spade` and `SPADEResult`;
- explicit dense spatial-weight validation;
- diagonal removal, matrix symmetry and island audit evidence;
- one common missing-data mask applied to vectors and both weight-matrix axes;
- optional seeded permutation inference for PSD and PSMD;
- complete accepted/rejected PSMD level tables;
- a public example, model manual and SPADE/IDSA source audit;
- a provenance-only NTD SPADE fixture and offline validator.

## 3. Non-negotiable Stage 5A decisions

- Spatial weights are prepared statistical inputs, not silently derived from geometry.
- The core does not choose a CRS, centroid, distance metric, unit, neighbourhood, bandwidth, normalization or symmetrization rule.
- Weights must be square, finite and nonnegative.
- Diagonal weights are excluded and reported.
- Directed matrices are accepted and audited; they are not silently symmetrized.
- Missing observations remove the matching row and column from `W`.
- Islands are rejected by default. Explicit retention does not make an all-zero global or stratum submatrix valid.
- Spatial variance is weighted average semivariance.
- PSD is `1 - sum_h(N_h * Gamma_h) / (N * Gamma)`.
- PSD is not described as identical to classical q under arbitrary weights.
- CPSD is response PSD divided by information-retention PSD under the same sample, strata and weights.
- A zero information PSD makes CPSD undefined.
- PSMD is the arithmetic mean of accepted CPSD levels and requires at least two accepted levels.
- Failed PSMD levels remain in the result.
- Permutation inference is conditional on supplied weights and fixed strata/accepted levels.
- gdverse, sdsfun, sf and spdep are references, not runtime dependencies.

## 4. Reference audit and external validation

Stage 5A reviewed:

- Cang and Luo (2018), *Spatial association detector (SPADE)*;
- Song and Wu (2021), *An interactive detector for spatial associations*;
- uploaded gdverse `R/psd_spade.R`, `R/spade.R`, `R/idsa.R`, `R/pid_idsa.R`, tests and vignettes;
- maintained `stscl/sdsfun` `R/spvar.R`, `R/fuzzyoverlay.R` and `R/spwt.R`.

External NTD SPADE validation uses the separately obtained gdverse `NTDs.gpkg`:

```text
SHA-256: 1dd0508fc03a61db973cce48524cf6ef32a93ac8102b7ca03a1865f4fb8cb406
complete observations: 185
weight: inverse Euclidean distance squared
response: incidence
stratum: soiltype
pyGeoHet PSD: 0.2566528294856155
gdverse expected: 0.256653
```

The raw GPKG is not redistributed. `tests/fixtures/reference/ntd_spade_reference.json` stores provenance and expected output; `tools/validate_ntd_spade_reference.py` performs the optional reconstruction.

## 5. Known Stage 5A validation gaps

Stage 5A is implemented. The pinned categorical NTD PSD route is externally checked, while CPSD, PSMD and the full continuous SPADE workflow remain provisional.

Remaining tasks:

1. generate static CPSD and PSMD reference tables from a pinned environment;
2. reproduce a published continuous-factor SPADE case;
3. add larger null, clustered and boundary-sensitive spatial simulations;
4. study sensitivity to alternative upstream weight constructions;
5. quantify discretization-level and PSMD selection uncertainty;
6. benchmark dense execution and design sparse-weight support without changing the estimand;
7. test strongly asymmetric directed weights with external fixtures.

Do not block Stage 5B merely to manufacture superficial parity where the reference workflow delegates weight construction to other packages.

## 6. Next active stage - Stage 5B IDSA

IDSA must be implemented as a distinct spatial-interaction estimand. It is not classical Cartesian intersection and is not the robust RID workflow.

### Source-derived fuzzy overlay behaviour

The reviewed `sdsfun::fuzzyoverlay()` route:

1. computes the response mean for every stratum of every explanatory factor;
2. normalizes all factor-stratum response means together;
3. maps every observation to one membership value for each factor's current stratum;
4. fuzzy AND selects the factor-stratum identity with the minimum membership;
5. fuzzy OR selects the factor-stratum identity with the maximum membership;
6. returns a categorical interaction-zone label.

pyGeoHet must preserve `(factor_name, original_stratum_label)` as a collision-safe identity rather than concatenating strings.

### Freeze before public coding

- normalization formula and constant-risk behaviour;
- whether normalization is global across all factor-strata or per factor;
- missing response/factor sample scope;
- deterministic tie rule when memberships are equal;
- fuzzy AND and OR names and whether both enter public IDSA;
- categorical versus continuous input handling;
- continuous-factor discretization and candidate selection;
- exact spatial power component `theta`;
- exact information-retention component `phi`;
- denominator-zero and degenerate-zone behaviour;
- `PID = theta / phi` orientation;
- pairwise versus multivariate factor combinations;
- zone counts and minimum internal spatial-weight requirements;
- permutation null and whether overlay is recomputed under response shuffles;
- immutable membership, zone, component and PID result objects;
- reference fixtures for fuzzy labels, `theta`, `phi` and PID.

### Recommended implementation sequence

1. implement an internal risk-membership table with complete provenance;
2. implement collision-safe `fuzzy_overlay(..., operation="and"|"or")` and manual tests;
3. implement `theta` using the Stage 5A PSD core;
4. derive and independently implement `phi` from the paper and pinned source;
5. implement fixed-strata PID;
6. add continuous-factor preprocessing only after fixed-strata PID is verified;
7. build pairwise/multivariate `IDSA` workflow and candidate tables;
8. create a static gdverse/sdsfun fixture and a published-case reproduction;
9. update all status, validation, README and handoff files before merge.

## 7. Required checks

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
ruff check src tests examples tools
black --check src tests examples tools
mypy src/pygeohet
python examples/01_factor_detector.py
python examples/02_classic_workflow.py
python examples/03_stratification_opgd.py
python examples/04_spatial_scale_opgd.py
python examples/05_multiscale_discretization.py
python examples/06_robust_detectors.py
python examples/07_spade.py
python -m build
```

Optional external checks:

```bash
python tools/validate_ntd_reference.py "path/to/classic.csv"
python tools/validate_ntd_spade_reference.py "path/to/NTDs.gpkg"
```

## 8. Merge discipline

Use a dedicated branch and pull request. Before merge:

- all Ubuntu, Windows and macOS jobs pass on Python 3.11-3.13;
- Ruff, Black, mypy, all examples and package builds pass;
- every new public method has analytical/property tests;
- source and licence audits are recorded;
- status, validation, changelog, inventory, roadmap, structure and handoff match code;
- external software remains reference-only;
- paper/source disagreements stay explicit;
- no full-validation claim is made without pinned output fixtures and a documented case.
