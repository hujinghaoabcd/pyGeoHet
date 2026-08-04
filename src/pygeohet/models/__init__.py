"""Integrated model workflows."""

from pygeohet.models.geodetector import GeoDetector, geodetector
from pygeohet.models.opgd import OPGD, OPGDResult, opgd
from pygeohet.models.robust import (
    RGD,
    RID,
    RGDResult,
    RIDResult,
    RobustCandidateResult,
    RobustDiscretizationResult,
    RobustOptimizationResult,
    optimize_robust_discretization,
    rgd,
    rid,
    robust_discretize,
)
from pygeohet.models.spade import (
    SPADE,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    power_spatial_determinant,
    spade,
)
from pygeohet.models.spade_results import (
    CompensatedSpatialDeterminantResult,
    MultilevelSpatialCandidate,
    MultilevelSpatialDeterminantResult,
    PowerSpatialDeterminantResult,
    SPADEResult,
    SpatialStratumVariance,
)
from pygeohet.models.spatial_scale import (
    SpatialScaleCandidateResult,
    SpatialScaleOPGD,
    SpatialScaleOPGDResult,
    SpatialScaleResult,
    compare_spatial_scales,
)

__all__ = [
    "CompensatedSpatialDeterminantResult",
    "GeoDetector",
    "MultilevelSpatialCandidate",
    "MultilevelSpatialDeterminantResult",
    "OPGD",
    "OPGDResult",
    "PowerSpatialDeterminantResult",
    "RGD",
    "RGDResult",
    "RID",
    "RIDResult",
    "RobustCandidateResult",
    "RobustDiscretizationResult",
    "RobustOptimizationResult",
    "SPADE",
    "SPADEResult",
    "SpatialScaleCandidateResult",
    "SpatialScaleOPGD",
    "SpatialScaleOPGDResult",
    "SpatialScaleResult",
    "SpatialStratumVariance",
    "compare_spatial_scales",
    "compensated_spatial_determinant",
    "geodetector",
    "multilevel_spatial_determinant",
    "opgd",
    "optimize_robust_discretization",
    "power_spatial_determinant",
    "rgd",
    "rid",
    "robust_discretize",
    "spade",
]
