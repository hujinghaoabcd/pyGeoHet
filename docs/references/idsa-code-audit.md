# IDSA paper and source-code audit

## Sources reviewed

Stage 5B used three evidence layers:

1. Song and Wu (2021), *An interactive detector for spatial associations*;
2. uploaded gdverse source:
   - `R/idsa.R`;
   - `R/pid_idsa.R`;
   - package tests, help pages and vignettes;
3. maintained `stscl/sdsfun` source:
   - `R/fuzzyoverlay.R`;
   - `R/vector_toolkits.R` (`normalize_vector`);
   - `R/spvar.R`.

The source was studied to verify the estimand and workflow. pyGeoHet does not translate the GPL-family source line by line and does not use it at runtime.

## Confirmed fuzzy-overlay contract

The reference code:

- converts each factor stratum to a factor-prefixed identity;
- calculates the response mean for every factor-stratum;
- flattens all means across all factors;
- applies global min-max normalization;
- maps every observation to one membership value per factor;
- uses `which.min` for fuzzy AND and `which.max` for fuzzy OR;
- returns the identity of the selected source factor-stratum.

The normalization formula is:

```text
(x - min(x)) / (max(x) - min(x))
```

R's `which.min` and `which.max` resolve exact ties by the first column. pyGeoHet makes that rule explicit and also permits an explicit last-factor rule. Near-ties are controlled by `membership_tolerance` and counted.

Reference implementations concatenate factor and stratum text. pyGeoHet instead stores `(factor_name, original_label)` tuples, preventing collisions without changing the scientific meaning.

## Confirmed PID formulas

The paper defines the spatial explanatory component:

```text
theta = 1 - sum_k N_k * Gamma_y,k / (N * Gamma_y)
```

This is PSD of the response under the fuzzy interaction zones.

For every discretized explanatory factor `X_i`, the information component compares global spatial variance with spatial variance remaining inside the same fuzzy zones:

```text
phi = 1 - sum_i sum_k N_k * Gamma_xi,k / sum_i (N * Gamma_xi)
```

The final power of interactive determinant is:

```text
PID = theta / phi
```

The gdverse helper computes the same ratio indirectly by calling its PSD routine for every discretized factor, recovering the within-zone component from `(1 - PSD_i) * Gamma_i`, and combining factors.

## Discretization audit

The reviewed gdverse IDSA workflow discretizes continuous factors before fuzzy overlay. Its current route uses CPSD candidates and may apply a LOESS-based class-count strategy through supporting helpers.

pyGeoHet uses the same scientific criterion—CPSD—but adopts an explicit maximum-CPSD selector with deterministic simplicity ties. This avoids embedding a partially pinned LOESS heuristic. Candidate values and failures remain public, so a future compatibility selector can be added without changing the fixed-strata PID estimand.

## Integrated search audit

The paper's iterative procedure starts from the individual factor with the strongest spatial explanatory power and adds factors while PID improves. pyGeoHet implements that as the default greedy search and additionally provides bounded exhaustive subset search for verification and small factor sets.

The reference wrapper computes one final interaction result after discretizing all supplied variables. pyGeoHet retains every attempted subset and failure, making the search auditable rather than returning only the terminal subset.

## Independent implementation choices

pyGeoHet adds several explicit contracts not safely guaranteed by the reviewed source:

- one joint complete-case sample across response and all factors;
- matching removal of both rows and columns from the spatial-weight matrix;
- collision-safe tuple zone identities;
- explicit constant-risk failure instead of divide-by-zero normalization;
- canonical sorted ordinal codes `1,...,K` for fixed discretizations;
- explicit minimum fuzzy-zone size and internal spatial-weight requirements;
- explicit zero-`phi` rejection;
- deterministic CPSD and PID tie rules;
- recomputation of response-derived fuzzy zones for every response permutation;
- valid and failed permutation counts;
- bounded exhaustive search;
- immutable result and candidate objects.

Canonical ordinal coding is important because the information component uses spatial variance of discretized factor codes. It prevents harmless external shifts or positive rescaling of class codes from changing the result. Unordered nominal labels are not assigned an undocumented order.

## Validation boundary

Current analytical tests verify fuzzy labels, memberships, ties, PID decomposition, canonical-code invariance, permutation determinism, CPSD selection and integrated subset searches.

Remaining external tasks:

1. pin a gdverse/sdsfun environment and source hashes;
2. generate a static fuzzy-zone table for a redistributable input;
3. generate external `theta`, `phi` and PID values;
4. record any difference caused by canonical ordinal encoding;
5. reproduce a published IDSA case;
6. compare maximum-CPSD and reference LOESS selectors;
7. evaluate interaction-search optimism and stability under resampling.
