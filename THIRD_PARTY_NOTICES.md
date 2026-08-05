# Third-party and scientific-source notices

pyGeoHet is an independent Python implementation. It does not copy source code from the reviewed R, Python, C++, QGIS, MATLAB, notebook, or spreadsheet implementations and does not call those projects at runtime.

Reference implementations and papers may be used to define formulas, construct static numerical fixtures, and investigate disagreements. Every reference fixture records its source project or publication, input hash, expected output, tolerance, and known convention differences.

## Classical and OPGD reviewed sources

The classical-workflow and Stage 3 audits reviewed the primary geographical-detector papers and user-uploaded source archives from `GD`, `gdverse`, `geodetector`, `GeodetectorPy`, QGIS implementations, OMGD and robust-detector research code. Several reviewed packages use GPL-family licences. No source code was copied or translated line by line into the MIT-licensed package.

The uploaded `gdverse` archive was used concretely rather than treated only as a citation. Files reviewed for software and numerical contracts include `R/gd_optunidisc.R`, `R/opgd.R`, `R/sesu_opgd.R`, tests and vignettes. Their behaviour is not silently adopted when it conflicts with a primary-paper estimand.

## MSD scientific and code evidence

Stage 3C is anchored by Meng et al. (2021), *Development of a multiscale discretization method for the geographical detector model*, DOI `10.1080/13658816.2021.1884686`. The paper reports associated code at Figshare DOI `10.6084/m9.figshare.13643318`.

The Figshare archive bytes could not be retrieved in the current development environment. pyGeoHet therefore does not claim author-code parity; it implements the documented estimand independently and retains the missing archive fixture as validation debt. See `docs/references/msd-code-audit.md`.

## Robust detector scientific and code evidence

Stage 4 reviewed Zhang, Song and Wu (2022), the uploaded `Robust_Geographical_Detector` author archive, and gdverse `robustdisc`, `rgd`, `rid` and Python change-point helper sources.

The reviewed gdverse snapshot declares GPL-3. The uploaded author archive did not contain a visible licence file. Both are used only for formula, behaviour and validation understanding. pyGeoHet independently implements validation, distinct-value-safe candidates, prefix sums, dynamic programming, immutable results and workflow composition. No runtime dependency on `ruptures`, reticulate, R, GD or gdverse is introduced. See `docs/references/robust-code-audit.md`.

## SPADE and IDSA scientific and code evidence

Stage 5 reviewed:

- Cang and Luo (2018), *Spatial association detector (SPADE)*;
- Song and Wu (2021), *An interactive detector for spatial associations*;
- uploaded gdverse `R/psd_spade.R`, `R/spade.R`, `R/idsa.R`, `R/pid_idsa.R`, tests and vignettes;
- maintained `stscl/sdsfun` `R/spvar.R`, `R/fuzzyoverlay.R` and `R/spwt.R`.

The reviewed gdverse and sdsfun projects use GPL-family licensing. pyGeoHet uses them to verify formulas, public workflow boundaries and reference outputs, not as code to translate or a runtime backend.

Stage 5A independently implements:

- square finite nonnegative spatial-weight validation;
- explicit diagonal removal, symmetry and island evidence;
- weighted average semivariance;
- PSD, CPSD and PSMD variance decompositions;
- missing-sample alignment across both weight-matrix axes;
- immutable results and conditional seeded permutation inference;
- an integrated SPADE workflow using pyGeoHet's own stratification subsystem.

The package does not depend at runtime on R, gdverse, sdsfun, sf, spdep, geopandas or a geometry engine. Coordinate/geometry-to-weight construction remains an upstream responsibility.

The IDSA source audit identified fuzzy response-risk membership zones that differ from classical tuple intersection. Stage 5B implements those formulas independently with collision-safe labels, explicit tie rules and immutable evidence. See `docs/references/spade-idsa-code-audit.md`.

## Validation data

The classical NTD validation uses a GPL-associated CSV available in a reviewed archive. pyGeoHet does not redistribute that raw file. It stores only numerical outputs, provenance, the input SHA-256 hash and an offline validator.

The Stage 5A SPADE validation uses gdverse `inst/extdata/NTDs.gpkg`. pyGeoHet does not redistribute the GPKG. The provenance fixture records SHA-256

```text
1dd0508fc03a61db973cce48524cf6ef32a93ac8102b7ca03a1865f4fb8cb406
```

and the preparation contract: disease polygon centroids, supporting-layer spatial joins, 185 complete observations, inverse Euclidean distance-squared weights and the `soiltype` stratification. The independent result `0.2566528294856155` matches the gdverse expected value `0.256653` at six decimals.

The ecological detector has incompatible historical software conventions. pyGeoHet implements the primary-paper residual-dispersion F ratio, uses a two-sided test by default, and exposes a separately named upper-tail compatibility option. This is a documented statistical choice, not copied package behaviour.

## Scientific anchors

Initial anchors include Wang et al. (2010), Cao, Ge, and Wang (2013), Wang, Zhang, and Fu (2016), Wang and Xu (2017), Cang and Luo (2018), Song et al. (2020), Meng et al. (2021), Song and Wu (2021), Zhang, Song, and Wu (2022), and later method papers listed in `MODEL_INVENTORY.md`.

Licences of future source archives must be audited before code-level adaptation. Lack of a clear licence means the source may be read for behavioural understanding but must not be copied or translated line by line.


## IDSA Stage 5B source boundary

Stage 5B reviewed Song and Wu (2021), uploaded gdverse `R/idsa.R` and `R/pid_idsa.R`, and maintained sdsfun `R/fuzzyoverlay.R`, `R/vector_toolkits.R` and `R/spvar.R`. These GPL-family sources define formulas, workflow expectations and comparison targets. pyGeoHet independently implements sample alignment, tuple zone identities, canonical ordinal encoding, spatial components, candidate search, immutable results and permutation inference. It does not copy source line by line and does not call R, gdverse or sdsfun at runtime.


## SRS-GD and Stage 6 information-source boundary

Stage 6A reviewed Bai et al. (2022), *Spatial rough set-based geographical detectors for nominal target variables*, and uploaded gdverse wrappers, tests and `src/roughset.cpp`. The paper is the primary estimand. The reviewed source is used to understand software contracts and construct compatibility questions, but differs from the paper in focal-object inclusion, neighbour indexing, multifeature matching and zero-positive-region handling.

pyGeoHet independently implements prepared binary adjacency validation, complete-case alignment across both matrix axes, exact tuple equivalence classes, local positive regions, immutable evidence and paired inference. It does not copy or translate the reviewed C++ line by line and does not call gdverse or R at runtime.

Stage 6B evidence includes Bai et al. (2023), *Information Consistency-Based Measures for Spatial Stratified Heterogeneity*, and maintained `stscl/sshicm` source pinned during the audit to commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`. That source is used to verify formulas and future static outputs, not as a runtime backend. pyGeoHet independently implements consistent natural-log entropy, shared-support histograms and corrected permutation p values rather than reproducing known source conventions mechanically.

The 2026 SWMI evidence audit found accessible official metadata, highlights and an abstract, but not the complete probability-adjustment equations, executable reference, supplement or numerical fixture. The publisher states that data are available on request. No SWMI code or API is introduced. Reopening requires complete equations, licence/provenance records and at least one independent numerical output. See `docs/references/swmi-evidence-audit.md`.
