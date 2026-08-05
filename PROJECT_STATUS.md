# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed stage:** Stage 6B of 10 - information-consistency SSH  
**Next evidence gate:** Stage 6C - spatially weighted mutual information  
**Next implementable family if 6C evidence remains insufficient:** Stage 7 - multivariate stratification and contribution  
**Development version:** 0.0.10

## Completed

- package, immutable result, documentation, testing and cross-platform CI foundation;
- classical q and four-detector workflows;
- auditable univariate stratification, OPGD, spatial-scale comparison and MSD;
- robust change-point discretization, RGD and RID;
- prepared spatial variance, PSD, CPSD, PSMD and SPADE;
- fuzzy overlay, PID and IDSA;
- paper-aligned SRS-GD for nominal targets;
- nominal IN-SSH by normalized mutual information;
- continuous IC-SSH by stratum-weighted transformed KL divergence;
- one shared continuous histogram support and edge sequence;
- corrected seeded permutation inference;
- common complete-case multi-factor information workflow;
- immutable entropy, contingency, histogram, KL, sample and null evidence;
- ten public examples and top-level API regression protection.

## Stage 6B public surface

```python
from pygeohet import (
    InformationConsistency,
    ContinuousInformationConsistencyResult,
    InformationConsistencyFactorResult,
    NominalInformationConsistencyResult,
    continuous_information_consistency,
    information_consistency,
    nominal_information_consistency,
)
```

## Numerical contract

### Nominal

```text
IN = I(Y; S) / H(Y)
   = 1 - H(Y | S) / H(Y)
```

- natural logarithms are used consistently;
- category names do not affect the result;
- a constant target has zero entropy and is rejected;
- contingency probabilities and entropy components remain public evidence.

### Continuous

```text
IC = sum_h p_h * atan(KL(P_h || P)) / (pi / 2)
```

- the global target and every stratum use one shared support and edges;
- automatic methods are Sturges, square root, Rice, Scott and Freedman-Diaconis;
- explicit integer counts and edge sequences are supported;
- zero stratum-probability KL terms are omitted without smoothing;
- a positive stratum bin cannot have zero global mass under the shared sample.

### Inference and workflow

- the target is shuffled relative to fixed supplied strata;
- continuous permutations reuse the observed edge sequence;
- pseudo-p values use `(1 + exceedances) / (B + 1)`;
- all factors in one workflow use one joint complete-case sample;
- minimum strata and missing-data policies are explicit;
- no R, C++ reference package or competing implementation is called at runtime.

## Validation state

The Stage 6B suite includes perfect, null and hand-calculated partial nominal cases; category relabeling invariance; constant-target failure; a continuous fixed-bin `KL=log(2)` case; identical-distribution `IC=0`; affine invariance; five automatic histogram methods; explicit support failures; small-stratum failures; corrected seeded permutations; common-sample multi-factor ranking; and public API tests.

The first full Stage 6B implementation CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black and mypy passed after the explicit histogram-label type fix. The clean final CI must also pass with ten examples, wheel build and source-distribution build before PR #10 merge.

Stage 6B is **implemented, provisional**. Static outputs from the pinned `stscl/sshicm` revision, a published application reproduction, larger simulations and histogram-sensitivity analysis remain validation debt.

## Deliberately deferred

- automatic discretization of inputs for information consistency;
- selection-adjusted inference for searched factors or bins;
- spatial-dependence-adjusted permutation schemes;
- kernel density estimation or adaptive bins inside the core estimator;
- Stage 6C SWMI until full probability weighting, null procedure and numerical fixtures are verified;
- Stage 7 GOZH, LESH/Shapley and OMGD until Stage 6B is merged and their separate contracts are audited.

## Immediate next task

1. finish the clean PR #10 CI and merge Stage 6B;
2. audit the complete SWMI equations and search for an authoritative numerical reference;
3. if SWMI remains evidence-gated, begin Stage 7A with GOZH evidence and numerical-contract review rather than inventing a provisional SWMI API.
