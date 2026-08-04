"""Integrated model workflows."""

from pygeohet.models.geodetector import GeoDetector, geodetector
from pygeohet.models.opgd import OPGD, OPGDResult, opgd
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
    "SpatialScaleCandidateResult",
    "SpatialScaleOPGD",
    "SpatialScaleOPGDResult",
    "SpatialScaleResult",
    "compare_spatial_scales",
    "geodetector",
    "opgd",
]
