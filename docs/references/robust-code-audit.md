# Robust detector source and formula audit

## Reviewed evidence

Stage 4 reviewed three evidence tracks together:

1. Zhang, Song and Wu (2022), *Robust geographical detector*, including the B-value equation, rank-equivalence transformation, least-squares segment cost and dynamic-programming pseudocode.
2. The uploaded author archive `Robust_Geographical_Detector-main(1).zip`, especially `CPD_1.ipynb`, `README.md` and the bundled article PDF.
3. The uploaded `gdverse` archive, especially:
   - `R/robustdisc.R`;
   - `R/rgd.R`;
   - `R/rid.R`;
   - `inst/python/cpd_disc.py`;
   - `vignettes/rgdrid.Rmd`;
   - generated help pages and figures.

The RGD paper and author repository identify the core statistical operation as a dependent-variable signal ordered by the rank of the explanatory variable, segmented by variance-based offline change-point detection. The `gdverse` Python helper uses `ruptures.Dynp(model="l2", jump=1)` and the R wrappers search requested class counts before running factor or interaction detection.

## Independently implemented numerical core

pyGeoHet does not call `ruptures`, R, reticulate, GD or gdverse at runtime. The implementation uses its own:

- numeric pair validation and missing-value mask;
- stable explanatory-variable ordering;
- admissible distinct-value boundary construction;
- prefix-sum interval SSE calculation;
- exact dynamic-programming recursion and backtracking;
- deterministic objective tie handling;
- aligned label reconstruction;
- class-count candidate and selection audit objects;
- composition with the existing classical detector implementation.

This is a clean-room implementation of the published estimand and algorithmic idea rather than a translation of external source lines.

## Behaviour retained from the references

The following behaviours are scientifically central and retained:

- the response is treated as a one-dimensional signal ordered by the explanatory variable;
- a requested `K` zones corresponds to `K - 1` change points;
- segment cost is least-squares deviation from the segment mean;
- the optimum minimizes total within-zone sum of squares;
- the resulting B-value has the same variance-decomposition form as q;
- multiple class counts may be evaluated;
- RGD feeds the selected robust zones into factor detection;
- RID feeds the same selected robust zones into interaction detection.

## Deliberate improvements and clarified contracts

### Equal explanatory values

The notebook and current `gdverse` helper obtain change positions from the row-level sorted signal and subsequently classify the rank values. With duplicate explanatory values, the row-level optimum and rank-based classification can become ambiguous.

pyGeoHet permits breaks only between distinct explanatory values. Consequently, equal values always receive the same robust label. This removes dependence on incidental row ordering and preserves the interpretation of a discretized explanatory variable.

### Minimum stratum size

External examples allow a minimum segment size of one. pyGeoHet defaults to two because the broader package requires auditable within-stratum inference and avoids silently introducing singleton factor strata. A value of one remains explicitly configurable where mathematically admissible.

### Number-of-strata selection

The paper describes selecting the interval count when B-value change rates fall below 0.05. Current `gdverse` exposes a highest-q strategy and a LOESS-based strategy delegated to `sdsfun`.

pyGeoHet separates the exact change-point estimator from class-count selection and currently exposes:

- `marginal_gain`, a direct documented threshold rule;
- `max_b`, a transparent maximum-B rule with a smaller-model tie break.

No LOESS compatibility claim is made until its exact pinned implementation and expected outputs are represented by a static fixture.

### B-value terminology

The paper's B-value and the classical q-statistic share the same variance-decomposition formula. pyGeoHet stores the complete `QStatisticResult` for inference and exposes `b_value` as an explicit property when the strata were constructed by robust change-point optimization.

### RID composition

The `gdverse` RID wrapper runs RGD and then the interaction detector. pyGeoHet follows the same model boundary while reusing its collision-safe tuple overlay, joint complete-case policy and explicit five-class interaction classifier.

## Licensing boundary

The uploaded `gdverse` package declares GPL-3. The author robust-detector archive did not include a visible licence file in the reviewed snapshot. Their code was therefore used only for behavioural understanding and comparison. No source was copied or translated line by line into the MIT-licensed package.

## Remaining validation work

Before the robust family is labelled externally validated:

1. pin an executable author or gdverse environment by version and checksum;
2. create static fixtures for fixed class counts, selected cuts, labels and B-values;
3. investigate duplicate-value behaviour as an explicit compatibility comparison;
4. reproduce the published RGD case or a redistributable official example;
5. add a pinned RID interaction fixture;
6. benchmark exact dynamic programming and any future pruning implementation;
7. evaluate selection stability and optimism under resampling and response outliers.
