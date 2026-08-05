# Stage 6C SWMI evidence-gate audit

Date: 2026-08-05

## Purpose

This audit determines whether the Spatially Weighted Mutual Information (SWMI) model has enough primary-source and numerical evidence to support a public pyGeoHet implementation.

The conclusion is **blocked**. Stage 6C does not introduce code, result types, package exports or a version change.

## Primary publication

Zhang, K., Yu, S., Sheng, Y., and Hu, X. (2026). *Geographic variables association detection model based on spatially weighted mutual information*. International Journal of Applied Earth Observation and Geoinformation, 148, 105213.

- DOI: `10.1016/j.jag.2026.105213`
- PII: `S1569843226001299`
- publisher: Elsevier
- publication date: April 2026

The accessible official abstract supports only the following workflow-level statements:

1. geographical variables are discretized;
2. variable probabilities are adjusted using spatial-autocorrelation strength;
3. information entropy and mutual information are calculated from the adjusted probabilities;
4. the model is intended for both continuous and categorical dependent variables;
5. the paper evaluates simulated noise, Chinese NO2 concentration and vegetation-cover categories in the Xizang Autonomous Region;
6. data are available on request.

These statements are insufficient to reconstruct the estimand.

## Retrieval and code search

The audit searched by exact title, DOI, PII, model acronym and author combinations.

Checked channels include:

- the official ScienceDirect article page;
- direct publisher PDF routes;
- ResearchGate metadata and full-text status;
- GitHub code and repository search;
- GitLab and Gitee through web search;
- Figshare, Zenodo and OSF;
- author and Nanjing Normal University web results;
- secondary Chinese summaries and figure-caption reproductions.

Results:

- the official article metadata, highlights, abstract and data-availability statement are indexed;
- the full article and PDF return access denial in the current environment;
- ResearchGate reports no downloadable full text;
- no authoritative author repository, supplementary archive or executable implementation was found;
- no redistributable numerical fixture was found;
- secondary summaries expose abstract-level workflow and figure captions but not the required equations.

A search failure is not proof that no code or supplement exists. It is evidence that no authoritative implementation can currently be pinned by repository, version and checksum.

## Missing mathematical contract

The following items are unknown and must not be guessed from ordinary mutual information, Moran's I, entropograms, image-registration SWMI or neighbouring GeoDetector variants.

### Spatial-autocorrelation adjustment

- the exact statistic used as “spatial autocorrelation strength”;
- whether adjustment is global, class-specific, observation-specific or pair-specific;
- the probability-adjustment equation;
- normalization and admissible range;
- handling of zero, negative or undefined spatial autocorrelation;
- whether the response, explanatory variable or both are adjusted;
- whether marginal and joint probabilities receive the same transformation.

### Spatial support

- accepted spatial-weight or neighbourhood inputs;
- symmetry, row standardization and diagonal conventions;
- distance or contiguity construction;
- neighbourhood scale selection;
- island and disconnected-component behaviour;
- missing-row alignment across both spatial axes.

### Discretization

- which variables are discretized;
- accepted methods and candidate class counts;
- whether continuous responses are discretized jointly or independently of factors;
- tie, empty-cell and duplicate-value rules;
- the objective used to select a discretization;
- whether discretization is repeated during inference.

### Entropy and association score

- exact adjusted marginal and joint probabilities;
- logarithm base;
- zero-cell treatment or smoothing;
- mutual-information normalization;
- statistic name, range and boundary interpretation;
- factor ranking and multivariable group score;
- interaction construction and classification.

### Inference and validation

- analytical or permutation null distribution;
- what is shuffled and what remains fixed;
- pseudo-p-value correction;
- treatment of spatial dependence under the null;
- uncertainty from neighbourhood and discretization selection;
- published numerical values, tables or machine-readable cases.

## Why neighbouring methods cannot fill the gaps

Ordinary normalized mutual information from Stage 6B does not contain a spatial probability adjustment. The 2023 entropogram measures lag-dependent association within a categorical random field and is not evidence for the SWMI factor-association estimator. Earlier medical-image-registration methods named SWMI apply spatial importance weights to image registration and are a different scientific problem.

Likewise, classical q, SRS-GD, PSD, PID and IC/IN-SSH each have distinct sample spaces, decompositions and inference contracts. Reusing one of them under a new name would create an unsupported estimand.

## Implementation gate

SWMI implementation may begin only after all of the following are pinned:

1. a complete primary-source copy containing every model equation;
2. the exact spatial-autocorrelation and probability-adjustment definitions;
3. the spatial-weight and neighbourhood contract;
4. the discretization and multivariable-group selection algorithm;
5. the association-score normalization and boundary cases;
6. the significance or resampling procedure;
7. at least one hand-calculable example;
8. at least one author or publisher numerical output;
9. provenance for code/data, including version, licence and checksums;
10. an independent implementation plan that does not copy incompatible source code.

## Current decision

- no `swmi()` function;
- no `SWMI` class;
- no result placeholder;
- no empty module;
- no package export;
- no inferred formula;
- no version bump.

Stage 6C remains evidence-gated. The roadmap proceeds to Stage 7A GOZH evidence and numerical-contract audit while retaining SWMI as a blocked method that can be reopened when authoritative evidence is obtained.

## Reopening procedure

When a full paper, supplement, author code or author-generated output becomes available:

1. record the file/source checksum and licence;
2. transcribe equations independently into an estimand specification;
3. produce a symbol table and boundary-case table;
4. construct a small manual oracle;
5. generate static external fixtures outside the pyGeoHet runtime;
6. compare alternative interpretations before exposing a public API;
7. update this audit, the decisions log, validation matrix and handoff before implementation.
