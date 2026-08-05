# Stage 7A GOZH evidence and numerical-contract audit

Date: 2026-08-05

## Purpose

This audit freezes the estimand and software boundary for the Geographically Optimal Zones-based Heterogeneity (GOZH) model before a public pyGeoHet implementation is introduced.

GOZH is treated as a response-supervised recursive partition of one or more explanatory variables. Its terminal nodes form geographical strata and its optimized explanatory power is the classical q value on those strata. It is not ordinary unsupervised discretization, a Cartesian overlay of independently discretized factors, or a spatial-contiguity regionalization algorithm.

## Primary publication

Luo, P., Song, Y., Huang, X., Ma, H., Liu, J., Yao, Y., and Meng, L. (2022). *Identifying determinants of spatio-temporal disparities in soil moisture of the Northern Hemisphere using a geographically optimal zones-based heterogeneity model*. ISPRS Journal of Photogrammetry and Remote Sensing, 185, 111–128. DOI `10.1016/j.isprsjprs.2022.01.009`.

## Reviewed software evidence

### gdverse 1.7

Uploaded archive: `gdverse-main.zip`.

Relevant files:

- `R/gozh.R`;
- `R/rpartdisc.R`;
- `R/sesu_gozh.R`;
- package manual pages.

The package declares GPL-3. pyGeoHet may use it to understand behaviour and create independent fixtures, but cannot copy or translate its source line by line into the MIT package.

`rpart_disc()` delegates directly to `rpart::rpart()` and returns terminal-node identifiers. Unless users forward arguments, tree complexity, minimum bucket size, cost-complexity pruning, surrogate splits, missing-value behaviour and categorical split handling are inherited from the installed `rpart` defaults.

`gozh_detector()`:

- builds one response tree per individual factor for factor/risk/ecological detectors;
- builds one joint response tree for each factor pair in the interaction detector;
- calculates q and classical detector results from terminal-node labels;
- does not expose the paper's all-subset optimal-combination and removal-contribution procedure as one integrated result.

### Python geodetector 0.2.0

Uploaded archive: `geodetector-master (2).zip`.

Relevant file: `src/geodetector/extensions/_gozh.py`.

The project declares MIT and uses `sklearn.tree.DecisionTreeRegressor`. Its defaults are `max_depth=5`, `min_samples_leaf=5`, and `random_state=42`. Pair interactions use a separate joint tree. Object/string factors are factorized into integer codes before fitting, which imposes an arbitrary ordinal relation and is not equivalent to native categorical regression-tree splitting.

This source is useful as a secondary behavioural comparison, not a primary estimator definition.

## Paper estimand

For response `Y`, explanatory-variable set `X`, and terminal zones `D`, the paper defines

\[
\gamma(X,D)=1-\frac{SSW_{X,D}}{SST},
\]

and

\[
\Omega=\max_D\gamma(X,D)
      =1-\frac{\min_D SSW_{X,D}}{SST}.
\]

For a candidate binary split at node `t`, explanatory variable `X_k`, and cutoff `s`, define

\[
R_1(k,s)=\{x:x^{(k)}\le s\},\qquad
R_2(k,s)=\{x:x^{(k)}>s\}.
\]

The selected split minimizes

\[
\sum_{i\in R_1(k,s)}(y_i-\bar y_1)^2+
\sum_{i\in R_2(k,s)}(y_i-\bar y_2)^2.
\]

The procedure is repeated recursively inside each child. A node with fewer observations than `minsplit` is terminal. The paper's application used `minsplit=30` for 653 monitoring stations to avoid finely divided zones.

The algorithm is therefore a greedy binary least-squares regression tree. It solves a local split optimum at each node, not the globally optimal unrestricted partition implied by the NP-complete objective.

## Primary-text contradiction

The equations, surrounding text and application section consistently require minimum within-zone SSW and maximum between-zone variation. A sentence on page 116 states that the two-zone solution with the “highest SSW” is optimal and later refers to the “highest overall SSW.” That wording contradicts Equations (3)–(5), the squared-error minimization criterion, the statement that optimal zones have minimum intra-area variance, and the later application description.

pyGeoHet treats “highest SSW” as an editorial sign error and implements minimum SSW. The contradiction remains documented rather than silently ignored.

## Spatial meaning

The paper calls terminal groups geographical zones because observations are georeferenced and the explanatory variables describe geography. The split equations do not include adjacency, distance, contiguity or a spatial-weight matrix. Terminal groups can be spatially disconnected when distant observations share the same path conditions.

The numerical core therefore accepts tabular response and factor values. Geometry-to-factor extraction, map construction and optional contiguity diagnostics remain upstream. GOZH must not claim connected regionalization unless a future extension adds an explicit spatial constraint.

## Frozen numerical contract

### Sample scope

- use one joint complete-case sample for the response and every factor in the fitted tree;
- retain original row indices and dropped-row count;
- `missing="raise"` rejects incomplete input;
- no surrogate split or factor-specific missing sample is used in the primary estimator;
- response must be finite, numeric and nonconstant.

### Continuous splits

- candidate thresholds lie only between adjacent distinct sorted values observed in the current node;
- equal explanatory values are never separated;
- a candidate is valid only when both children satisfy `min_leaf_size`;
- the threshold stored in evidence is the midpoint between adjacent distinct values, while membership uses the observed-order boundary;
- strictly monotone transformations preserve the ordered split structure, apart from transformed threshold values.

### Categorical splits

The paper and `rpart` support categorical predictors, while the secondary Python source's integer factorization is not acceptable.

For a numeric-response binary tree, pyGeoHet orders categories within the current node by response mean and evaluates the `K-1` contiguous bipartitions in that order. This is the standard exact reduction for squared-error binary categorical splitting. Category-mean ties use stable first-observed category order. The result retains the ordered categories and selected left/right category sets.

This route is response-supervised and node-specific. It must not be confused with ordinal encoding supplied by the user.

### Split objective and ties

For a node with parent SSW `SSW_t`, each candidate has child SSW `SSW_L + SSW_R` and gain

\[
\Delta_t=SSW_t-(SSW_L+SSW_R).
\]

The selected candidate minimizes child SSW. Objective values within `objective_tolerance` are tied, then prefer:

1. earlier user-supplied factor order;
2. continuous split before a later equal factor candidate naturally through factor order;
3. the lower continuous threshold, or lexicographically smaller categorical left-set representation.

The tie rule is deterministic and stored in the result.

### Explicit stopping and complexity

A node becomes terminal when any condition holds:

- `n_node < min_split_size`;
- no valid split leaves at least `min_leaf_size` observations in both children;
- `max_depth` is reached;
- absolute gain is not greater than `min_gain` within tolerance;
- relative gain `gain / parent_ssw` is not greater than `min_relative_gain` when that option is active;
- the node response is constant.

The primary implementation exposes these controls explicitly and does not inherit hidden `rpart` or scikit-learn defaults. Post-hoc cost-complexity pruning is a separate possible estimator and is not silently applied.

### Terminal-zone identity

Terminal zones use deterministic root-to-leaf path identities and canonical left-to-right labels `0,1,...,L-1`. Raw library node numbers are not public because they vary across implementations.

Each result retains the complete node table, split candidates selected at each internal node, path conditions, terminal counts, means, SSW values, depth and stop reasons.

### Omega and classical q

For terminal labels,

\[
\Omega=1-SSW/SST.
\]

It is numerically equal to the classical q statistic on the optimized zones. pyGeoHet reuses its existing q implementation rather than maintaining a duplicate variance decomposition.

Because zones are selected using the same response, the classical noncentral-F p value is selection-naive. It may be reported only as conditional descriptive evidence and must be labelled accordingly.

## Individual, interaction and subset estimands

### Individual factor

Fit one tree using one factor. The terminal labels define that factor's optimized zones and individual `Omega`.

### Joint factor set

Fit one tree using all factors in a supplied set. Factors may be selected repeatedly at different nodes. Joint GOZH is not an overlay of separately optimized labels.

### Pair interaction

For factors `X1` and `X2`, compare individual trees with a joint two-factor tree on one common sample. Classical five-class interaction labels may be calculated from `Omega_1`, `Omega_2`, and `Omega_12` using the package's existing tolerance-aware classifier.

The comparison is between separately optimized individual and joint trees; it is not the classical fixed-stratification overlay estimand.

### Optimal factor subset

For `n` supplied factors, the paper considers every subset of size at least two, totaling

\[
2^n-n-1.
\]

A practical implementation must expose `max_subset_size` and `max_combinations`. Every attempted subset, selected score, failure and runtime-relevant candidate count remains public.

Subset selection maximizes `Omega`; ties within tolerance prefer fewer factors and then lexicographic input-order tuples.

### Removal contribution

For selected factor set `C*`, define

\[
\Delta_j=\Omega(C^*)-\Omega(C^*\setminus\{j\}).
\]

If all reductions are nonnegative and their sum is positive,

\[
r_j=\Delta_j/\sum_k\Delta_k,
\qquad
c_j=\Omega(C^*)r_j.
\]

The paper does not specify negative reductions, zero total reduction or refitting/tie instability. pyGeoHet freezes the following:

- every reduced model is refit on the same complete sample and with the same tree controls;
- reductions below zero only within tolerance are set to zero and retain the raw value;
- a materially negative reduction is retained and makes normalized contributions undefined unless an explicit signed mode is introduced later;
- zero total nonnegative reduction makes relative importance and allocated contribution undefined rather than equal shares;
- raw full/reduced `Omega`, reductions and tree evidence remain public.

## Inference contract

### Conditional analytical evidence

The q noncentral-F result on selected terminal zones is conditional on the selected tree and does not account for response-guided split search. It is labelled `selection_adjusted=False`.

### Refit permutation

The primary optional null shuffles the response relative to fixed factor rows, refits the complete tree for each permutation, and recomputes `Omega`. For subset search, a fully selection-aware permutation must repeat the entire subset search; holding the observed winning subset fixed is a separate conditional mode.

Pseudo-p values use

\[
(1+\#\{T_b\ge T_{obs}\})/(B+1).
\]

Invalid fits are counted and retained. A fixed-tree response permutation is not the primary GOZH null because the observed tree was derived from the response.

## Reference-source divergences

### Paper versus gdverse

- the paper mentions `minsplit`; gdverse exposes all `rpart` controls only through `...`;
- gdverse inherits cost-complexity pruning, `minbucket`, surrogate and missing rules from the installed `rpart` version;
- the paper's all-subset optimal interaction and removal contribution are not represented by the pairwise `gozh_detector()` result;
- raw `rpart$where` node identifiers are implementation-specific.

### Paper versus Python geodetector

- fixed `max_depth=5` and `min_samples_leaf=5` are not paper defaults;
- no explicit `min_split_size=30` paper-case route is provided;
- categorical factorization creates arbitrary ordinal splits;
- fewer than three valid rows return a zero label vector rather than an explicit error;
- scikit-learn defaults determine additional split behaviour;
- joint pair trees are useful but do not implement all-subset optimization and contribution allocation.

## Validation plan

### Manual and independent analytical fixtures

1. one continuous factor with a unique best root split;
2. a two-level tree with a known root factor and known child splits;
3. duplicate explanatory values that cannot be separated;
4. equal-objective factor and threshold ties;
5. a categorical factor whose optimal category partition is not its input code order;
6. constant-node and no-valid-leaf stop reasons;
7. canonical path and terminal-label invariance under row permutation;
8. direct equality between terminal-zone `Omega` and q;
9. pair joint-tree interaction classification;
10. factor-removal contribution including zero-total and negative-reduction boundaries.

A brute-force split oracle must independently enumerate every valid candidate at a node. Small-tree fixtures should independently enumerate all greedy candidate decisions, not merely compare to the implementation's own helper.

### External/static validation

- record outputs from pinned `gdverse`/`rpart` versions for explicit controls, not ambient defaults;
- record outputs from the uploaded Python implementation for continuous-only comparable settings;
- identify at least one published GOZH table or zone tree suitable for reproduction;
- store inputs, package versions, hashes, controls and tolerances;
- document expected differences caused by pruning, categorical handling and label identity.

R is not available in the current execution environment, so no gdverse fixture is claimed in this audit. The source remains a contract reference until a pinned external run is generated.

### Simulation and robustness

- known threshold and hierarchical mechanism recovery;
- null false-positive behaviour under refit permutations;
- sensitivity to `min_split_size`, `min_leaf_size`, depth and gain controls;
- stability under noise, outliers and duplicate values;
- subset-search overfitting and selection-aware inference;
- runtime and memory scaling by observations, factors, categories and combinations.

## Implementation boundary

Stage 7A may proceed because the primary split objective and recursion are sufficiently specified, provided pyGeoHet exposes every complexity choice explicitly and documents where it departs from implicit `rpart` defaults.

Initial implementation should include:

- an independent deterministic tree core;
- continuous and categorical split evidence;
- immutable node, split, tree, subset and contribution results;
- individual and joint factor-set workflows;
- optional refit permutation inference;
- manual and brute-force tests;
- no runtime dependency on R, gdverse, rpart or scikit-learn.

Public names are added only with working code, tests, documentation and final cross-platform CI.
