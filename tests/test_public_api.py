"""Regression tests for the documented top-level package API."""

import pygeohet


def test_stage5b_symbols_are_available_from_top_level_package() -> None:
    expected = {
        "IDSA",
        "IDSAResult",
        "FuzzyOverlayResult",
        "InteractiveSpatialDeterminantResult",
        "fuzzy_overlay",
        "idsa",
        "optimize_spatial_discretization",
        "power_interactive_determinant",
    }

    assert not expected.difference(vars(pygeohet))
    assert not expected.difference(pygeohet.__all__)
