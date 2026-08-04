# Third-party and scientific-source notices

pyGeoHet is an independent Python implementation. It does not copy source code from the reviewed R, Python, C++, QGIS, MATLAB, notebook, or spreadsheet implementations and does not call those projects at runtime.

Reference implementations and papers may be used to define formulas, construct static numerical fixtures, and investigate disagreements. Every reference fixture records its source project or publication, input hash, expected output, tolerance, and known convention differences.

## Classical and OPGD reviewed sources

The classical-workflow and Stage 3 audits reviewed the primary geographical-detector papers and user-uploaded source archives from `GD`, `gdverse`, `geodetector`, `GeodetectorPy`, QGIS implementations, OMGD and robust-detector research code. Several reviewed packages use GPL-family licences. No source code was copied or translated line by line into the MIT-licensed package.

The uploaded `gdverse` archive was used concretely rather than treated only as a citation. Files reviewed for software and numerical contracts include:

- `R/gd_optunidisc.R` and `R/opgd.R` for candidate-grid organisation and separation of optimal parameters from detector output;
- `R/sesu_opgd.R` for keeping geographic-support comparison separate from discretization;
- package tests and vignettes for public wrappers, deterministic examples and output tables.

The uploaded GD and lightweight Python/R/QGIS implementations were also reviewed for API expectations, q conventions, labels and failure handling. Their behaviour is not silently adopted when it conflicts with a primary-paper estimand.

## MSD scientific and code evidence

Stage 3C is anchored by Meng et al. (2021), *Development of a multiscale discretization method for the geographical detector model*, DOI `10.1080/13658816.2021.1884686`. The paper reports associated code at Figshare DOI `10.6084/m9.figshare.13643318`.

The Figshare archive bytes could not be retrieved in the current development environment. Accordingly:

- pyGeoHet does not claim line-by-line or output parity with the author archive;
- no Figshare source was copied into the repository;
- the current MSD contract is independently implemented from the paper's formula, pseudocode and examples;
- uploaded GD/gdverse code informs software organisation and boundaries but is not presented as an MSD numerical oracle;
- author parity remains a named validation task requiring archive version, file names, checksums, licence and static fixtures.

The full audit is recorded in `docs/references/msd-code-audit.md`.

## Robust detector scientific and code evidence

Stage 4 reviewed:

- Zhang, Song and Wu (2022), *Robust geographical detector*;
- the uploaded author archive `Robust_Geographical_Detector-main(1).zip`, including `CPD_1.ipynb`, its README and bundled article PDF;
- the uploaded gdverse files `R/robustdisc.R`, `R/rgd.R`, `R/rid.R`, `inst/python/cpd_disc.py`, the robust-detector vignette and generated help pages.

The paper and reference software support the central workflow: order the response by the explanatory variable, solve a least-squares offline change-point problem, calculate B from the resulting zones, and use those zones in factor or interaction detection.

The reviewed gdverse snapshot declares GPL-3. The uploaded author archive did not contain a visible licence file in the reviewed snapshot. Therefore both sources are used for formula, behaviour and validation understanding only. pyGeoHet does not copy or translate their implementation and does not distribute their notebook or code.

The Stage 4 implementation independently provides:

- pair validation and missing-row reconstruction;
- stable ordering and distinct-value-safe candidate boundaries;
- prefix-sum interval objectives;
- exact dynamic programming and deterministic backtracking;
- immutable candidate and selected-model results;
- RGD/RID composition with pyGeoHet's own q and interaction implementations.

No runtime dependency on `ruptures`, reticulate, R, GD or gdverse is introduced. Differences from the reviewed software, especially the rule that tied explanatory values cannot be split, are documented rather than hidden. See `docs/references/robust-code-audit.md`.

## Validation data

The NTD validation uses a GPL-associated CSV available in a reviewed archive. pyGeoHet does not redistribute that raw file. It stores only numerical outputs, provenance, the input SHA-256 hash, and a validator that the developer can run against a separately obtained copy.

The ecological detector has incompatible historical software conventions. pyGeoHet implements the primary-paper residual-dispersion F ratio, uses a two-sided test by default, and exposes a separately named upper-tail compatibility option. This is a documented statistical choice, not copied package behaviour.

## Scientific anchors

Initial anchors include Wang et al. (2010), Cao, Ge, and Wang (2013), Wang, Zhang, and Fu (2016), Wang and Xu (2017), Song et al. (2020), Meng et al. (2021), Zhang, Song, and Wu (2022), and later method papers listed in `MODEL_INVENTORY.md`.

Licences of future source archives must be audited before code-level adaptation. Lack of a clear licence means the source may be read for behavioural understanding but must not be copied or translated line by line.
