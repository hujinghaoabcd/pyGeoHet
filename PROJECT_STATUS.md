# Project status

**Project:** pyGeoHet  
**Date:** 2026-08-05  
**Completed implementation stage:** Stage 6B of 10 - information-consistency SSH  
**Completed evidence gate:** Stage 6C - SWMI blocked pending authoritative equations and fixtures  
**Next active batch:** Stage 7A - GOZH evidence and numerical contract  
**Development version:** 0.0.10

## Implemented model families

- classical q and the factor, interaction, risk and ecological detectors;
- auditable univariate stratification and OPGD;
- prepared-support spatial-scale comparison;
- exact and coarse-to-fine MSD;
- robust ordered segmentation, RGD and RID;
- prepared spatial variance, PSD, CPSD, PSMD and SPADE;
- fuzzy overlay, PID and IDSA;
- paper-aligned SRS-GD for nominal targets;
- nominal IN-SSH by normalized mutual information;
- continuous IC-SSH by stratum-weighted transformed KL divergence;
- common-sample multi-factor information consistency;
- immutable decomposition, sample and inference evidence;
- ten public examples and cross-platform API regression protection.

## Stage 6B baseline

Version `0.0.10` is merged in commit `6e9a96368f9b1421045fbb6a6fda7c5d37859980`.

The nominal statistic is

```text
IN = I(Y; S) / H(Y)
   = 1 - H(Y | S) / H(Y)
```

The continuous statistic is

```text
IC = sum_h p_h * atan(KL(P_h || P)) / (pi / 2)
```

Natural logarithms are used consistently. Global and stratum continuous histograms share one support and edge sequence. Permutation inference shuffles the target relative to fixed strata, keeps continuous edges fixed and uses `(1 + exceedances) / (B + 1)`.

The final Stage 6B CI passed on Ubuntu, Windows and macOS with Python 3.11, 3.12 and 3.13. Ruff, Black, mypy, ten examples, wheel and source-distribution builds passed.

Stage 6B remains **implemented, provisional** pending static `stscl/sshicm` outputs, a published-case reproduction, larger simulations and histogram-sensitivity analysis.

## Stage 6C SWMI evidence-gate result

The accessible official source confirms only this workflow:

1. discretize geographical variables;
2. use spatial-autocorrelation strength to adjust probabilities;
3. calculate entropy and mutual information from adjusted probabilities;
4. support continuous and categorical dependent variables;
5. search for individual or grouped explanatory variables.

The audit did not obtain the complete article equations, supplementary material, author code or a numerical fixture. The following contracts remain unknown:

- the exact spatial-autocorrelation statistic and probability adjustment;
- spatial weights, neighbourhood scale, normalization and island handling;
- discretization candidates, objective and tie rules;
- adjusted marginal and joint probability construction;
- mutual-information normalization and result range;
- multivariable grouping and interaction definition;
- significance, permutation and selection-adjustment procedures;
- missing-data, zero-cell and small-stratum behaviour.

Therefore Stage 6C introduces no code, empty module, placeholder result, public API or version change. Ordinary mutual information, the entropogram, medical-image SWMI, q, SRS-GD, PSD, PID and IC/IN-SSH cannot be substituted.

See `docs/references/swmi-evidence-audit.md`.

## Next active batch - Stage 7A GOZH audit

Stage 7A must freeze the Geographically Optimal Zones-based Heterogeneity model before implementation:

- the initial zones and candidate operations;
- progressive optimization, merge/split and stopping rules;
- objective functions and q/heterogeneity calculations;
- individual and interactive determinant outputs;
- zone-count and finely divided-zone controls;
- spatial support and scale behaviour;
- deterministic search/tie policies;
- complexity bounds and failure evidence;
- author/reference code licence and numerical fixtures;
- at least one published-case reproduction target.

GOZH, LESH/Shapley contribution and OMGD remain separate batches. Stage 7A must not silently turn the three models into one optimizer.

## Reopening SWMI

SWMI can be reconsidered when a complete primary-source copy, exact probability adjustment, spatial-support contract, inference procedure, hand-calculable example and author/publisher numerical output are pinned with provenance and licence information.
