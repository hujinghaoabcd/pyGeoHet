"""Regression tests for the documented top-level package API."""

import pygeohet


def _assert_public(expected: set[str]) -> None:
    assert not expected.difference(vars(pygeohet))
    assert not expected.difference(pygeohet.__all__)


def test_stage5b_symbols_are_available_from_top_level_package() -> None:
    _assert_public(
        {
            "IDSA",
            "IDSAResult",
            "FuzzyOverlayResult",
            "InteractiveSpatialDeterminantResult",
            "fuzzy_overlay",
            "idsa",
            "optimize_spatial_discretization",
            "power_interactive_determinant",
        }
    )


def test_stage6a_symbols_are_available_from_top_level_package() -> None:
    _assert_public(
        {
            "SRSGeoDetector",
            "SRSGeoDetectorResult",
            "SRSFactorDetectorResult",
            "SRSEcologicalDetectorResult",
            "SRSInteractionDetectorResult",
            "SpatialRoughSetResult",
            "spatial_rough_set_measure",
            "srs_factor_detector",
            "srs_ecological_detector",
            "srs_interaction_detector",
            "srsgd",
        }
    )
