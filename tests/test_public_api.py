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

    missing_attributes = sorted(
        name for name in expected if not hasattr(pygeohet, name)
    )
    missing_exports = sorted(
        name for name in expected if name not in pygeohet.__all__
    )

    assert missing_attributes == []
    assert missing_exports == []
