# SPADE and IDSA paper/source audit

## Evidence reviewed

Stage 5 reviewed the following together:

1. Cang and Luo (2018), *Spatial association detector (SPADE)*;
2. Song and Wu (2021), *An interactive detector for spatial associations*;
3. the uploaded gdverse source archive, especially:
   - `R/psd_spade.R`;
   - `R/spade.R`;
   - `R/idsa.R`;
   - `R/pid_idsa.R`;
   - tests and vignettes;
4. the maintained `stscl/sdsfun` source, especially:
   - `R/spvar.R`;
   - `R/fuzzyoverlay.R`;
   - `R/spwt.R`.

## SPADE formulas

The primary and reference sources agree on the weighted average semivariance:

\[
\Gamma =
\frac{\sum_i\sum_{j\ne i}w_{ij}(y_i-y_j)^2/2}
     {\sum_i\sum_{j\ne i}w_{ij}}.
\]

The power of spatial determinant is:

\[
PSD=1-\frac{\sum_hN_h\Gamma_h}{N\Gamma}.
\]

For a continuous explanatory variable and one discretization, the compensated statistic is:

\[
CPSD=PSD(y,h,W)/PSD(x,h,W).
\]

PSMD is the mean CPSD over an explicit collection of accepted class counts.

## Independent implementation choices

pyGeoHet implements the estimands directly rather than translating the R/C++ structure:

- accepts an already prepared dense weight matrix;
- validates shape, finiteness and nonnegative weights;
- removes the diagonal explicitly;
- does not row-standardize or symmetrize silently;
- subsets values, strata and both axes of the weight matrix on one missing-data mask;
- rejects islands by default and makes retention explicit;
- rejects strata without positive internal spatial weight;
- retains all PSMD class-count candidates and failures;
- provides optional seeded permutation inference;
- uses the package's existing deterministic discretization methods.

Automatic geometry processing, CRS interpretation, centroid selection, neighbourhood construction and distance units remain upstream. This prevents an apparently convenient wrapper from silently changing the estimand.

## External NTD parity

The gdverse test case uses `inst/extdata/NTDs.gpkg`, joins disease polygons to supporting layers by centroid, removes incomplete rows, constructs second-power inverse-distance weights, and evaluates incidence against `soiltype`.

Using the same prepared data contract, pyGeoHet obtains:

```text
PSD = 0.2566528294856155
```

The gdverse test expectation is `0.256653`; the values agree at six decimal places. The GPKG SHA-256 is:

```text
1dd0508fc03a61db973cce48524cf6ef32a93ac8102b7ca03a1865f4fb8cb406
```

The raw GPKG is not redistributed. A validator and provenance-only JSON fixture are included.

## IDSA findings reserved for Stage 5B

IDSA is not a simple deterministic intersection detector. The reviewed `sdsfun::fuzzyoverlay()` workflow:

1. computes the response mean for every stratum of every explanatory variable;
2. normalizes all resulting stratum-risk means;
3. maps each observation to its membership value in each factor's stratum;
4. for fuzzy AND, chooses the source factor-stratum label with the minimum membership;
5. for fuzzy OR, chooses the source factor-stratum label with the maximum membership.

The resulting fuzzy zone is categorical. It is then used in the IDSA power-of-interactive-determinant calculation. This differs from classical tuple intersection and must remain a separate public operation.

The IDSA paper defines a spatial power component and an information-retention component. Stage 5B will freeze the exact `phi`, `theta` and `PID=theta/phi` contracts, label collision policy, normalization edge cases, missing-risk strata and deterministic tie handling before adding public APIs.

## Licence boundary

The reviewed gdverse and sdsfun projects use GPL-family licensing. They are used as scientific and behavioural references. pyGeoHet does not copy their source or call them at runtime. The implementation is an independent Python formulation with its own validation, results and API design.
