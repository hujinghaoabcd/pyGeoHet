import numpy as np
import pytest

from pygeohet import q_statistic
from pygeohet.exceptions import (
    ConstantResponseError,
    MissingDataError,
    SmallStratumError,
)


def test_q_is_zero_when_group_means_are_equal() -> None:
    result = q_statistic([0.0, 1.0, 0.0, 1.0], ["a", "a", "b", "b"])
    assert result.q == pytest.approx(0.0)
    assert result.between_ss == pytest.approx(0.0)
    assert result.within_ss == pytest.approx(result.total_ss)


def test_q_is_one_for_perfect_stratification() -> None:
    result = q_statistic([1.0, 1.0, 4.0, 4.0], ["a", "a", "b", "b"])
    assert result.q == pytest.approx(1.0)
    assert result.within_ss == pytest.approx(0.0)
    assert result.p_value == pytest.approx(0.0)


def test_q_is_invariant_to_row_order_and_label_names() -> None:
    y = np.array([1.0, 1.3, 2.8, 3.2, 5.0, 5.2])
    x = np.array(["a", "a", "b", "b", "c", "c"])
    expected = q_statistic(y, x)
    permutation = np.array([4, 0, 3, 1, 5, 2])
    renamed = np.array([30, 10, 20, 10, 30, 20])
    actual = q_statistic(y[permutation], renamed)
    assert actual.q == pytest.approx(expected.q)
    assert actual.within_ss == pytest.approx(expected.within_ss)
    assert actual.total_ss == pytest.approx(expected.total_ss)


def test_q_equals_dummy_regression_r_squared() -> None:
    y = np.array([1.0, 1.4, 2.2, 2.5, 4.7, 5.1])
    strata = np.array(["a", "a", "b", "b", "c", "c"])
    result = q_statistic(y, strata)

    categories = sorted(set(strata))
    design = np.column_stack(
        [np.ones(y.size)]
        + [(strata == category).astype(float) for category in categories[1:]]
    )
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    residuals = y - design @ coefficients
    r_squared = 1.0 - np.dot(residuals, residuals) / np.dot(y - y.mean(), y - y.mean())
    assert result.q == pytest.approx(r_squared)


def test_missing_drop_reports_sample_change() -> None:
    result = q_statistic(
        [1.0, 1.2, np.nan, 4.8, 5.0],
        ["a", "a", "b", "b", "b"],
    )
    assert result.n_observations == 4
    assert result.dropped_count == 1
    assert result.stratum_counts == {"a": 2, "b": 2}


def test_missing_raise_is_explicit() -> None:
    with pytest.raises(MissingDataError):
        q_statistic(
            [1.0, 1.2, np.nan, 4.8, 5.0],
            ["a", "a", "b", "b", "b"],
            missing="raise",
        )


def test_singleton_stratum_is_not_silently_removed() -> None:
    with pytest.raises(SmallStratumError):
        q_statistic([1.0, 1.2, 5.0], ["a", "a", "b"])


def test_constant_response_is_undefined() -> None:
    with pytest.raises(ConstantResponseError):
        q_statistic([2.0, 2.0, 2.0, 2.0], ["a", "a", "b", "b"])


def test_noncentral_f_fields_are_valid() -> None:
    result = q_statistic(
        [1.0, 1.2, 2.4, 2.8, 5.0, 5.5],
        ["a", "a", "b", "b", "c", "c"],
    )
    assert 0.0 <= result.p_value <= 1.0
    assert result.noncentrality >= 0.0
    assert result.df1 == 2
    assert result.df2 == 3
