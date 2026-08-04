# NTD classical-workflow reference

Stage 2 was checked against the 185-row neural-tube-defect disease dataset used by existing GeoDetector implementations.

## Provenance

- local reference filename: `GeoDetector_2018_Example(Disease Dataset).csv`;
- SHA-256: `b28764136d57c3e7929465b12c4d5bcbb8521d09361633716f89dc59dc962e61`;
- mapping: `type -> soiltype`, `region -> watershed`, `level -> elevation`;
- raw data are not redistributed by pyGeoHet;
- static expected values are stored in `tests/fixtures/reference/ntd_classic_reference.json`.

## Results reproduced

The factor-detector q and noncentral-F p-values agree with the `gdverse` and `GD` vignette within `1e-7`:

| factor | q | p-value |
|---|---:|---:|
| watershed | 0.6377736701 | 0.0001288023 |
| elevation | 0.6067087097 | 0.0433822430 |
| soiltype | 0.3857168428 | 0.3721454859 |

All three pairwise interactions are classified as `enhance_bivariate`, matching the reference vignette. The counts of significant Welch risk comparisons are 29 for watershed, 20 for elevation, and 8 for soil type, also matching the published output.

## Ecological-detector convention

The primary pyGeoHet convention is a two-sided F test of equal residual within-stratum dispersion. This detects differences regardless of factor ordering. With the NTD data it marks watershed-versus-soiltype and elevation-versus-soiltype as significant.

`alternative="greater"` is an explicit compatibility mode for the upper-tail convention used by `gdverse::ecological_detector()`. Under the vignette's factor order it reproduces the three published `No` decisions. This difference is intentional and recorded rather than hidden.
