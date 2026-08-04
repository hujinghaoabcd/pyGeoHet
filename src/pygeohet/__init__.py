"""pyGeoHet public API."""

from pygeohet._version import __version__
from pygeohet.core import (
    InteractionType,
    categorical_overlay,
    classify_interaction,
    q_statistic,
)
from pygeohet.detectors import (
    EcologicalDetector,
    FactorDetector,
    InteractionDetector,
    RiskDetector,
    ecological_detector,
    factor_detector,
    interaction_detector,
    risk_detector,
)
from pygeohet.models import GeoDetector, geodetector
from pygeohet.results import (
    EcologicalComparisonResult,
    EcologicalDetectorResult,
    FactorDetectorResult,
    GeoDetectorResult,
    InteractionComparisonResult,
    InteractionDetectorResult,
    QStatisticResult,
    RiskComparisonResult,
    RiskDetectorResult,
    RiskStratumSummary,
)

__all__ = [
    "__version__",
    "EcologicalComparisonResult",
    "EcologicalDetector",
    "EcologicalDetectorResult",
    "FactorDetector",
    "FactorDetectorResult",
    "GeoDetector",
    "GeoDetectorResult",
    "InteractionComparisonResult",
    "InteractionDetector",
    "InteractionDetectorResult",
    "InteractionType",
    "QStatisticResult",
    "RiskComparisonResult",
    "RiskDetector",
    "RiskDetectorResult",
    "RiskStratumSummary",
    "categorical_overlay",
    "classify_interaction",
    "ecological_detector",
    "factor_detector",
    "geodetector",
    "interaction_detector",
    "q_statistic",
    "risk_detector",
]
