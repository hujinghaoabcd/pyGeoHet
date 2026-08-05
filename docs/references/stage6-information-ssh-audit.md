# Stage 6 evidence audit: SRS-GD, information consistency and SWMI

## Purpose

Stage 6 extends pyGeoHet beyond variance-based continuous-response statistics. It is split into three compact batches:

- **Stage 6A:** spatial rough set-based geographical detectors (SRS-GD) for nominal targets;
- **Stage 6B:** information-consistency SSH for continuous and nominal targets (`IC-SSH` and `IN-SSH`);
- **Stage 6C:** spatially weighted mutual information (SWMI), only after its 2026 paper, formulas and validation data are sufficiently pinned.

These methods must remain separate from classical q, PSD, PID and ordinary Cartesian interaction overlays.

## Primary sources

### SRS-GD

- Bai, H., Li, D., Ge, Y., Wang, J., & Cao, F. (2022). *Spatial rough set-based geographical detectors for nominal target variables*. Information Sciences, 586, 525-539. DOI: 10.1016/j.ins.2021.12.019.
- Uploaded gdverse source:
  - `R/srs_geodetecor.R`;
  - `R/srsgd.R`;
  - `src/roughset.cpp`;
  - `tests/testthat/test-srs_geodetecor.R`;
  - `data/srs_table.rda` and `data/srs_wt.rda`.

### Information consistency

- Bai, H., Wang, H., Li, D., & Ge, Y. (2023). *Information Consistency-Based Measures for Spatial Stratified Heterogeneity*. Annals of the American Association of Geographers, 113(10), 2512-2524. DOI: 10.1080/24694452.2023.2223700.
- Maintained `stscl/sshicm` source, pinned during this audit to commit `76b6c2879353716f2632c4f5cbb13bef3f6c8305`:
  - `R/sshic.R`;
  - `R/sshin.R`;
  - `src/IC_SSH.cpp`;
  - `src/IN_SSH.cpp`;
  - histogram density and relative-entropy helpers;
  - package vignette and examples.

### SWMI

- Zhang, K., Yu, S., Sheng, Y., & Hu, X. (2026). *Geographic variables association detection model based on spatially weighted mutual information*. International Journal of Applied Earth Observation and Geoinformation, 148, 105213. DOI: 10.1016/j.jag.2026.105213.

The SWMI paper is recent and no authoritative implementation or redistributable benchmark has yet been pinned in the project. Stage 6C therefore remains evidence-gated.

## Stage 6A paper contract

### Spatial information system

The paper defines a spatial information system as

\[
SIS=(U,A,d,M),
\]

where `U` is the object universe, `A` is the set of named conditional features, `d` is a nominal decision or target feature, and `M` is a binary adjacency relation.

For a focal object `x`, the local region is

\[
C(x)=\{y\in U:M_{xy}=1\}\cup\{x\}.
\]

The focal object is therefore included even when the supplied adjacency matrix has a zero diagonal.

### Local indiscernibility

For feature set `A'`, the `x`-local indiscernible set of object `y` is

\[
LInd(y,x,A')=[y]_{A'}\cap C(x),
\]

where `[y]_{A'}` contains objects whose values equal `y` on **every** feature in `A'`. A multifeature interaction therefore uses exact tuples, not an any-coordinate match.

### Local positive region and approximation quality

Within `C(x)`, an indiscernible class belongs to the positive region when all objects in that class have the same decision value. The local positive region is the union of these decision-consistent classes.

The local approximation quality is

\[
\gamma(x;A',d)=\frac{|POS^x_{A'}(d)|}{|C(x)|}.
\]

It lies in `[0,1]`. Adding features refines the indiscernibility relation, so local quality and its average cannot decrease.

### Average local explanatory power

\[
D(A',d)=\frac{1}{|U|}\sum_{x\in U}\gamma(x;A',d).
\]

Larger `D` means stronger average local explanatory power for a nominal target.

### Spatial entropy

Let

\[
p_x=\frac{\gamma(x;A',d)}{\sum_{z\in U}\gamma(z;A',d)}.
\]

Then

\[
SE(A',d)=-\sum_{x\in U}p_x\log_2 p_x.
\]

A larger `SE` means the local explanatory power is more evenly distributed and therefore less spatially heterogeneous. The maximum is `log2(|U|)`. If every local quality is zero, `D=0` but `SE` is mathematically undefined because the normalization denominator is zero; pyGeoHet must report this explicitly rather than inventing a value.

### Three detectors

- **SRSF:** returns `D(A',d)` and `SE(A',d)` for one or more feature sets.
- **SRSE:** compares local qualities for two feature sets. Because both values are evaluated at the same focal objects, pyGeoHet uses a paired Student test as the primary comparison. A Welch compatibility route may be added separately if an external table requires it.
- **SRSI:** measures the gain

  \[
  D(A_1\cup A_2,d)-D(A_1,d),
  \]

  and the corresponding entropy change. The gain must be nonnegative apart from floating-point tolerance.

The paper describes Student tests on a random subset of focal objects. pyGeoHet will default to all complete focal objects for deterministic estimation and allow a seeded subset for paper-style sampling.

## SRS-GD reference-source discrepancies

The reviewed gdverse implementation is valuable as a software and fixture reference, but several operations do not match the paper literally:

1. The R wrapper zeroes the adjacency diagonal and the C++ loop does not explicitly add the focal object, whereas the paper defines `C(x)` as neighbors union `{x}`.
2. The C++ decision comparison uses `yobs[i] == yobs[n]`, where `n` is the position within the neighbor vector rather than the original neighbor index `wti[n]`.
3. The multifeature C++ path treats rows as matching when **any coordinate** agrees. The paper's indiscernibility relation requires equality on every feature, and exact tuple refinement is required for the monotonicity proof.
4. When no positive evidence is found, the C++ route returns `1 / degree`; the paper definition gives a zero numerator and therefore local quality zero, except that a self-only local region is trivially decision-consistent.
5. An empty neighbor list produces a zero denominator in the reference implementation.

For these reasons, the gdverse value `PD=0.459524, SE_PD=3.282169` is retained as a compatibility datum but is not the primary correctness oracle. pyGeoHet implements the published estimand independently and documents any compatibility mode separately.

## Stage 6A frozen implementation choices

- accept a prepared square finite binary adjacency matrix;
- ignore diagonal values and always add the focal object exactly once;
- require symmetry by default; a future directed-neighbourhood extension must be explicit;
- reject islands by default because self-only regions create trivially perfect local quality;
- permit islands only through an explicit option and report their indices;
- apply one complete-case mask to the nominal target, all features and both matrix axes;
- require nominal/discrete targets and factors; noninteger floating values are rejected until deliberately discretized;
- use collision-safe tuples for multifeature indiscernibility;
- retain local region sizes, positive-region sizes and approximation qualities;
- return `SE=None` when all local qualities are zero;
- use paired tests on common focal objects;
- retain test sample indices and random seeds;
- never infer geometry, CRS, distance thresholds or contiguity rules inside the numerical core.

## Hand-calculated paper-figure fixture

The information table and 11 by 11 adjacency matrix in Figure 1 of Bai et al. (2022) are transcribed as a redistributable numerical fixture. Under the literal paper definition and feature `a1`, pyGeoHet expects:

```text
local quality = (0.5, 0.0, 1.0, 0.6, 0.625, 1.0, 1.0,
                 1/3, 1.0, 1.0, 1.0)
D             = 0.7325757575757575
SE            = 3.245554302578003
```

For the feature union `{a1,a2}`:

```text
D  = 0.8143939393939393
SE = 3.3720204818904733
```

The increase in `D` is a direct monotonicity fixture.

## Stage 6B formula audit

### Nominal target: IN-SSH

The nominal information-consistency statistic is normalized mutual information:

\[
I_N(d,s)=\frac{I(d;s)}{H(d)}
        =1-\frac{H(d\mid s)}{H(d)}.
\]

The maintained source factorizes both target and strata, computes empirical marginal and joint probabilities, and estimates significance by permuting the target relative to fixed strata.

Frozen pyGeoHet contracts:

- `H(d)=0` for a constant nominal target;
- one stratum or one observation;
- zero-count categories;
- missing labels;
- natural-log versus base-2 consistency, which cancels in the ratio but should not be mixed within intermediate reporting;
- pseudo-p-value correction `(1 + exceedances) / (B + 1)` rather than the reference source's uncorrected `exceedances / B`.

### Continuous target: IC-SSH

For stratum `s_i`, let `f_i` be the target density in that stratum and `f` the global target density. The continuous statistic is

\[
I_C(d,s)=\sum_i p(s_i)
\frac{\arctan\{D_{KL}(f_i\Vert f)\}}{\pi/2}.
\]

The arctangent maps the nonnegative relative entropy to `[0,1)`. The maintained source estimates densities by histograms and defaults to Sturges bins. Before implementation pyGeoHet must freeze:

- a common histogram support and common bin edges for global and stratum densities;
- zero-density smoothing or masking rules;
- bin methods and deterministic edge construction;
- minimum stratum size;
- constant target handling;
- permutation p-value correction;
- sensitivity tables over bin choices.

The implementation is supported by direct hand calculations. Static `sshicm` candidate and final-output tables remain external-validation debt and are not required at runtime.

## Stage 6C SWMI boundary

The 2026 SWMI paper reports that it discretizes geographical variables, adjusts probabilities using spatial autocorrelation strength, and calculates spatially weighted entropy and mutual information for continuous or categorical targets. The abstract alone is insufficient to freeze the exact probability adjustment, interaction search and null distribution. Stage 6C remains planned until the full equations, code or author outputs are available.

## Validation plan

### Stage 6A

1. Figure 1 local qualities, `D` and `SE`;
2. exact tuple refinement and monotonicity;
3. focal-object inclusion;
4. adjacency row/column permutation invariance;
5. explicit island rejection and opt-in retention;
6. missing-row alignment across both axes;
7. multiclass nominal targets;
8. paired ecological and interaction tests;
9. comparison against the gdverse fixture with the discrepancy documented, not hidden.

### Stage 6B

1. hand-computed nominal entropy and mutual information;
2. independence and perfect-determination extremes;
3. category relabeling invariance;
4. seeded permutation determinism;
5. corrected p-value bounds;
6. continuous relative-entropy examples with fixed bins;
7. bin-method sensitivity;
8. static outputs from pinned `sshicm` source and published examples.

### Stage 6C

Implementation begins only after a complete primary-source contract and at least one independent numerical reference are obtained.

## Stage 6B implemented contract

pyGeoHet independently implements:

- nominal `IN = I(target; strata) / H(target)` with natural logarithms used consistently;
- explicit zero-target-entropy failure;
- continuous `IC = sum_h p_h * atan(KL(P_h || P)) / (pi/2)`;
- one complete-target support and one shared bin edge sequence;
- Sturges, square-root, Rice, Scott and Freedman-Diaconis automatic counts;
- explicit equal-width integer counts and complete custom edge sequences;
- omission of zero stratum-probability KL terms without pseudocount smoothing;
- a common complete-case sample for multi-factor comparisons;
- target permutations relative to fixed strata and fixed continuous edges;
- corrected pseudo-p values `(1 + exceedances) / (B + 1)`;
- immutable contingency, histogram, contribution, sample and null evidence.

The reviewed source is not copied or called at runtime. pyGeoHet does not reproduce mixed entropy bases, uncorrected p values, or density comparisons built on incompatible supports.

## Stage 6B analytical fixtures

Nominal tests include perfect determination (`IN=1`), independence (`IN=0`) and a four-observation partial table with

```text
H(Y)     = log(2)
H(Y | S) = 0.75 * H_binary(2/3)
IN       = 1 - H(Y | S) / H(Y)
```

The continuous separated-strata fixture uses global probabilities `(0.5, 0.5)`. Each stratum has `KL=log(2)`, giving

```text
IC = atan(log(2)) / (pi/2)
```

Identical stratum distributions produce zero KL divergence and `IC=0`.

## Stage 6B remaining evidence debt

- generate static input, candidate and final-output tables from the pinned `stscl/sshicm` revision;
- record exact source/package build metadata and tolerances;
- reproduce at least one published application;
- add larger nominal and continuous null/power simulations;
- quantify histogram-method and bin-count sensitivity;
- examine permutation validity under spatial dependence and selected stratifications.

