# MSD paper and source-code audit

## Primary paper

- Xiaoyu Meng, Xin Gao, Jiaqiang Lei and Shengyu Li (2021).
- *Development of a multiscale discretization method for the geographical detector model*.
- International Journal of Geographical Information Science 35(8): 1650-1675.
- DOI: `10.1080/13658816.2021.1884686`.
- Code DOI reported by the paper: `10.6084/m9.figshare.13643318`.

The paper defines MSD as a supervised bivariate discretization. It first reduces the value-grid resolution of sorted unique `x`, performs a coarse q-maximizing cut search, and then maps neighbourhoods around selected cuts to successively finer buffer scales. The final scale is the original scale. The paper also describes caching interval variances to avoid repeatedly recomputing the same within-stratum objective terms.

## Uploaded source archives inspected

The user-provided archives were treated as implementation references, not merely as bibliography. The Stage 3C audit inspected the following surrounding implementations:

### `gdverse-main(2).zip`

Relevant files:

- `R/gd_optunidisc.R`: builds a complete variable × class-count × method grid, evaluates factor-detector q and selects the largest q per variable;
- `R/opgd.R`: separates optimal discretization from the final detector workflow and returns both optimal parameters and detector results;
- `R/sesu_opgd.R`: keeps spatial-support scale effects separate from within-variable discretization;
- `R/robustdisc.R` and `inst/python/cpd_disc.py`: sort observations by the explanatory variable, expose group-count/minimum-size parameters and retain a clear Python numerical kernel behind the R wrapper;
- package tests and vignettes: used as references for small deterministic examples, public wrappers and explicit parameter tables.

No MSD implementation was found in the uploaded gdverse source. Therefore gdverse informed package organization, audit-table design, sample ordering and separation of estimands, but it was not treated as the MSD numerical oracle.

### `GD-main(2).zip`

The GD source was reviewed as a reference for OPGD parameter-grid organization, q-based candidate comparison and spatial-unit-scale separation. It does not replace the MSD paper's coarse-to-fine cut-search definition.

### Other uploaded GeoDetector Python/R/QGIS archives

The lightweight implementations were used to check public API expectations, category-label conventions and the need to avoid silent data mutation. They do not contain an independently verified MSD implementation.

## Author-code availability status

The paper's Figshare DOI has been identified and recorded. During this development batch the runtime environment could retrieve the paper and Figshare API documentation but could not fetch the archive bytes from the DOI endpoint. Consequently:

- pyGeoHet does **not** claim line-by-line parity with the author archive yet;
- no author source code was copied into pyGeoHet;
- the implemented numerical contract is derived from the paper's equations, pseudocode and examples;
- the exact-search special case and exhaustive-enumeration tests provide an independent oracle;
- final external validation remains blocked until the Figshare archive can be pinned by file name, version, checksum and licence.

This limitation is intentionally visible in `VALIDATION_MATRIX.md`, `PROJECT_STATUS.md` and `HANDOFF_NEXT_CONVERSATION.md`.

## Paper-to-code mapping

| Paper concept | pyGeoHet implementation |
|---|---|
| `X1 = sort(unique(X))` | stable sort of one joint complete-case sample, with unique-value boundaries |
| q maximization | equivalent minimization of within-stratum sum of squares |
| upscaling number `k` | `upscale` value-grid scale |
| buffer scale `kn` | ordered `buffer_scales` ending at 1 |
| epsilon neighbourhood | `epsilon`, mapped using the paper's scale-ratio formula |
| one refined cut near each prior cut | exactly one candidate is selected from each mapped neighbourhood |
| repeated variance calculations | prefix-sum interval costs reused throughout search |
| final cuts at original scale | final buffer scale must equal 1 |
| cut belongs to latter class | `searchsorted(..., side="right") + 1` |
| number of classes supplied by user | fixed `n_strata`, limited to 10 |

## Independent implementation choices

The paper and accessible text do not freeze every software detail. pyGeoHet therefore makes the following explicit decisions:

- one joint complete-case sample is used for all scales;
- `base_resolution` and `origin` make the value grid reproducible for non-integer data;
- absent `base_resolution` is inferred as the minimum positive unique-value spacing and stored;
- intermediate and final strata obey `min_stratum_size`;
- ties use the lexicographically smallest cut tuple;
- failed scale searches raise a clear exception rather than silently falling back;
- every scale retains candidate and selected cut evidence;
- `upscale=1` is exposed as an exact global-search validation mode.

These are pyGeoHet contracts, not claims about undocumented author-code behaviour.

## Remaining audit tasks

1. Retrieve the Figshare archive.
2. Record article version, file names, byte sizes, checksums and licence.
3. Run the original example unchanged in its documented environment.
4. Compare coarse candidates, neighbourhood ranges, cut membership, ties, q values and final cuts.
5. Store a static non-runtime fixture.
6. Reproduce at least one published MSD case or a redistributable subset.
7. Resolve any discrepancy through an explicit paper mode, author-code compatibility mode or documented erratum; never silently alter the primary estimator.
