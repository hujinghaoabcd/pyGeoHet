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
from pygeohet.models.spatial_scale import (
    SpatialScaleCandidateResult,
    SpatialScaleOPGD,
    SpatialScaleOPGDResult,
    SpatialScaleResult,
    compare_spatial_scales,
)

__all__ = [
    "GeoDetector",
    "OPGD",
    "OPGDResult",
    "RGD",
    "RGDResult",
    "RID",
    "RIDResult",
    "RobustCandidateResult",
    "RobustDiscretizationResult",
    "RobustOptimizationResult",
    "SpatialScaleCandidateResult",
    "SpatialScaleOPGD",
    "SpatialScaleOPGDResult",
    "SpatialScaleResult",
    "compare_spatial_scales",
    "geodetector",
    "opgd",
    "optimize_robust_discretization",
    "rgd",
    "rid",
    "robust_discretize",
]
