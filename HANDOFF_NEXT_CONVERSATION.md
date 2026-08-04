# HANDOFF — pyGeoHet Stage 1 baseline

Date: 2026-08-05

## 1. Authoritative baseline

After the Stage 1 pull request is merged, GitHub `main` in `hujinghaoabcd/pyGeoHet` is the only authoritative continuation baseline. A new conversation must fetch the current `main` commit SHA and record it here before starting Stage 2. Do not reconstruct from chat text, old ZIP archives, or the superseded `pyGeoDetectorX` blueprint.

## 2. Current completed work

- package and documentation skeleton;
- ten-stage roadmap and method inventory;
- explicit numerical conventions and durable decisions;
- immutable q and factor-detector result classes;
- q-statistic with direct SSW/SST and classical noncentral-F p-value;
- factor detector over pandas DataFrames, mappings, or one-dimensional input;
- tests for exact boundaries, invariance, missing values, singleton rejection, q–R² equality, and multi-factor output;
- compact CI quality gate and runnable example.

## 3. Non-negotiable decisions

Read `DECISIONS.md` and `docs/theory/numerical-conventions.md` before editing statistics. In particular: no silent singleton removal; no hidden imputation; direct sums of squares; interaction components use a common complete-case sample; classic and extended estimands remain distinct; results retain audit information; q alone does not justify causal wording; handoff documents are updated before every merge.

## 4. Next task — Stage 2

Implement the complete classical workflow in this order:

1. collision-safe categorical overlay utility using tuple coding;
2. interaction classification with explicit floating tolerance;
3. interaction detector using joint complete cases;
4. Welch risk detector and pairwise p-value table;
5. ecological detector after documenting the exact F convention;
6. integrated `GeoDetector` orchestrator and result object;
7. static reference fixtures from GD/gdverse and an independent Python implementation, with convention differences recorded;
8. NTD or another published-case reproduction;
9. model docs, examples, status, validation matrix and handoff update.

## 5. Known open questions

- Historical ecological-detector implementations use inconsistent F-tail and degree-of-freedom conventions. Resolve from the primary paper and document any compatibility mode rather than copying one implementation blindly.
- Some R implementations silently remove singleton strata and may retain pre-removal degrees of freedom. pyGeoHet intentionally rejects this behaviour.
- The noncentral-F formula needs a dedicated independent reference fixture before q/factor promotion from provisional to stable.

## 6. Required checks

```bash
python -m pip install -e ".[test]"
pytest --cov=pygeohet --cov-report=term-missing
python examples/01_factor_detector.py
python -m build
```

Before merging Stage 2, also run Ruff and mypy using `pyproject.toml`.
