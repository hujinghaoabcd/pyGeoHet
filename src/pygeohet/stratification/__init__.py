"""Continuous-variable stratification and q-guided optimization."""

from pygeohet.stratification.methods import canonical_method, stratify
from pygeohet.stratification.optimal import (
    TIE_RULE,
    evaluate_stratification,
    optimize_stratification,
)
from pygeohet.stratification.results import (
    OptimalStratificationResult,
    StratificationEvaluationResult,
    StratificationResult,
)

__all__ = [
    "TIE_RULE",
    "OptimalStratificationResult",
    "StratificationEvaluationResult",
    "StratificationResult",
    "canonical_method",
    "evaluate_stratification",
    "optimize_stratification",
    "stratify",
]
