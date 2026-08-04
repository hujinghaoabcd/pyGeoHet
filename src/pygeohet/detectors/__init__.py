"""Detector APIs."""

from pygeohet.detectors.ecological import EcologicalDetector, ecological_detector
from pygeohet.detectors.factor import FactorDetector, factor_detector
from pygeohet.detectors.interaction import InteractionDetector, interaction_detector
from pygeohet.detectors.risk import RiskDetector, risk_detector

__all__ = [
    "EcologicalDetector",
    "FactorDetector",
    "InteractionDetector",
    "RiskDetector",
    "ecological_detector",
    "factor_detector",
    "interaction_detector",
    "risk_detector",
]
