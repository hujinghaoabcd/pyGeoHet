"""Continuous-variable stratification and q-guided optimization."""

from pygeohet.stratification.methods import canonical_method, stratify
from pygeohet.stratification.msd import (
    MSD,
    MSD_TIE_RULE,
    MSDResult,
    MSDScaleResult,
    multiscale_discretize,
)
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
    "MSD",
    "MSDResult",
    "MSDScaleResult",
    "MSD_TIE_RULE",
    "TIE_RULE",
    "OptimalStratificationResult",
    "StratificationEvaluationResult",
    "StratificationResult",
    "canonical_method",
    "evaluate_stratification",
    "multiscale_discretize",
    "optimize_stratification",
    "stratify",
]
