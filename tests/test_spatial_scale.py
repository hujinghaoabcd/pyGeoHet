import pandas as pd
import pytest

from pygeohet import (
    FactorDetectorResult,
    QStatisticResult,
    SpatialScaleOPGD,
    compare_spatial_scales,
)
from pygeohet.exceptions import InvalidDataError


def _q(q: float, p_value: float) -> QStatisticResult:
    return QStatisticResult(
        q=q,
        p_value=p_value,
        f_statistic=1.0,
        noncentrality=0.0,
        df1=1,
        df2=8,
        n_observations=10,
        n_strata=2,
        stratum_counts={1: 5, 2: 5},
        within_ss=1.0 - q,
        between_ss=q,
        total_ss=1.0,
        dropped_count=0,
    )


def _factor_result(values: dict[str, tuple[float, float]]) -> FactorDetectorResult:
    return FactorDetectorResult(
        {name: _q(q_value, p_value) for name, (q_value, p_value) in values.items()}
    )


def test_primary_paper_quantile_selects_highest_scale_score() -> None:
    result = compare_spatial_scales(
        {
            10: _factor_result({"a": (0.1, 0.01), "b": (0.2, 0.01), "c": (0.8, 0.01)}),
            20: _factor_result({"a": (0.2, 0.01), "b": (0.7, 0.01), "c": (0.9, 0.01)}),
        }
    )

    assert result.selection_valid
    assert result.best is not None
    assert result.best.scale == 20
    assert result.candidates[0].score == pytest.approx(0.68)
    assert result.candidates[1].score == pytest.approx(0.86)


def test_significance_filter_matches_legacy_gd_eligibility_rule() -> None:
    result = compare_spatial_scales(
        {
            10: pd.DataFrame(
                {
                    "factor": ["a", "b", "c"],
                    "q": [0.2, 0.95, 0.8],
                    "p_value": [0.01, 0.2, float("nan")],
                }
            ),
            20: pd.DataFrame(
                {
                    "factor": ["a", "b", "c"],
                    "q": [0.3, 0.4, 0.5],
                    "p_value": [0.01, 0.01, 0.01],
                }
            ),
        },
        significant_only=True,
    )

    first = result.candidates[0]
    assert first.eligible_factors == ("a", "c")
    assert first.excluded_factors == ("b",)
    assert first.score == pytest.approx(0.74)


def test_scale_ties_are_explicit_and_deterministic() -> None:
    inputs = {
        20: _factor_result({"a": (0.5, 0.01), "b": (0.5, 0.01)}),
        10: _factor_result({"a": (0.5, 0.01), "b": (0.5, 0.01)}),
    }

    first = compare_spatial_scales(inputs, tie_break="first")
    smallest = compare_spatial_scales(inputs, tie_break="smallest")

    assert first.best is not None
    assert smallest.best is not None
    assert first.best.scale == 20
    assert smallest.best.scale == 10


def test_scale_comparison_requires_same_factor_set() -> None:
    with pytest.raises(InvalidDataError, match="same factors"):
        compare_spatial_scales(
            {
                10: _factor_result({"a": (0.2, 0.01), "b": (0.3, 0.01)}),
                20: _factor_result({"a": (0.4, 0.01), "c": (0.5, 0.01)}),
            }
        )


def test_spatial_scale_opgd_runs_prepared_scale_datasets() -> None:
    y = [1.0] * 4 + [5.0] * 4 + [10.0] * 4
    aligned = pd.DataFrame(
        {
            "x1": [0.0, 0.1, 0.2, 0.3, 5.0, 5.1, 5.2, 5.3, 10.0, 10.1, 10.2, 10.3],
            "x2": [1.0, 1.1, 1.2, 1.3, 6.0, 6.1, 6.2, 6.3, 11.0, 11.1, 11.2, 11.3],
        }
    )
    crossed = pd.DataFrame(
        {
            "x1": [0.0, 1.0, 2.0, 3.0] * 3,
            "x2": [3.0, 2.0, 1.0, 0.0] * 3,
        }
    )

    result = SpatialScaleOPGD(
        methods=["equal_interval", "quantile", "natural_breaks"],
        n_strata=[2, 3],
    ).fit({10: (y, aligned), 20: (y, crossed)})

    assert result.scale_effects.selection_valid
    assert result.scale_effects.best is not None
    assert result.scale_effects.best.scale == 10
    assert set(result.opgd_results) == {10.0, 20.0}
    assert result.best_opgd is result.opgd_results[10.0]


def test_spatial_scale_opgd_retains_failed_scale() -> None:
    y = [1.0, 1.0, 5.0, 5.0, 10.0, 10.0]
    valid = pd.DataFrame({"x": [0.0, 0.1, 5.0, 5.1, 10.0, 10.1]})
    invalid = pd.DataFrame({"x": [1.0] * 6})

    result = SpatialScaleOPGD(
        methods=["equal_interval"],
        n_strata=[2],
    ).fit({10: (y, valid), 20: (y, invalid)})

    assert not result.scale_effects.selection_valid
    assert 20.0 in result.failures
    rejected = result.scale_effects.candidates[1]
    assert not rejected.accepted
    assert rejected.rejection_reason is not None
