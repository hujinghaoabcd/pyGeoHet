import numpy as np
import pandas as pd
import pytest

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.spade import (
    SPADE,
    compensated_spatial_determinant,
    multilevel_spatial_determinant,
    power_spatial_determinant,
)
from pygeohet.spatial import spatial_variance


def _complete_weights(n: int) -> np.ndarray:
    weights = np.ones((n, n), dtype=float)
    np.fill_diagonal(weights, 0.0)
    return weights


def test_spatial_variance_matches_manual_weighted_semivariance() -> None:
    values = np.asarray([0.0, 2.0, 5.0])
    weights = np.asarray(
        [
            [7.0, 1.0, 2.0],
            [1.0, 8.0, 3.0],
            [2.0, 3.0, 9.0],
        ]
    )
    off_diagonal = weights.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    differences = values[:, None] - values[None, :]
    expected_numerator = float(np.sum(off_diagonal * 0.5 * differences * differences))

    result = spatial_variance(values, weights)

    assert result.numerator == pytest.approx(expected_numerator)
    assert result.value == pytest.approx(expected_numerator / off_diagonal.sum())
    assert result.diagonal_weight_removed == pytest.approx(24.0)


def test_spatial_variance_is_invariant_to_global_weight_scaling() -> None:
    values = np.asarray([1.0, 2.0, 5.0, 9.0])
    weights = np.asarray(
        [
            [0.0, 1.0, 2.0, 1.0],
            [3.0, 0.0, 1.0, 2.0],
            [2.0, 4.0, 0.0, 1.0],
            [1.0, 1.0, 5.0, 0.0],
        ]
    )

    first = spatial_variance(values, weights)
    second = spatial_variance(values, 17.0 * weights)

    assert first.value == pytest.approx(second.value)
    assert not first.symmetric_weights


def test_psd_matches_direct_formula_and_row_permutation() -> None:
    y = np.asarray([0.0, 1.0, 4.0, 5.0, 9.0, 10.0])
    strata = np.asarray(["a", "a", "b", "b", "c", "c"])
    weights = _complete_weights(len(y))

    result = power_spatial_determinant(y, strata, weights)
    global_variance = spatial_variance(y, weights).value
    within = 0.0
    for label in np.unique(strata):
        indices = np.flatnonzero(strata == label)
        within += (
            len(indices)
            * spatial_variance(y[indices], weights[np.ix_(indices, indices)]).value
        )
    expected = 1.0 - within / (len(y) * global_variance)

    permutation = np.asarray([5, 0, 3, 1, 4, 2])
    permuted = power_spatial_determinant(
        y[permutation],
        strata[permutation],
        weights[np.ix_(permutation, permutation)],
    )

    assert result.value == pytest.approx(expected)
    assert permuted.value == pytest.approx(result.value)
    assert result.strata_frame()["count"].tolist() == [2, 2, 2]


def test_missing_rows_subset_values_labels_and_weights_together() -> None:
    y = [0.0, 1.0, np.nan, 4.0, 5.0, 9.0, 10.0]
    strata = ["a", "a", "b", "b", "b", "c", "c"]
    weights = _complete_weights(7)

    result = power_spatial_determinant(y, strata, weights)

    assert result.dropped_count == 1
    assert result.used_indices == (0, 1, 3, 4, 5, 6)
    with pytest.raises(MissingDataError):
        power_spatial_determinant(y, strata, weights, missing="raise")


def test_island_and_internal_stratum_island_contracts_are_explicit() -> None:
    y = np.asarray([0.0, 1.0, 4.0, 5.0])
    strata = np.asarray([0, 0, 1, 1])
    weights = np.asarray(
        [
            [0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
        ]
    )
    power_spatial_determinant(y, strata, weights)

    broken = weights.copy()
    broken[2, 3] = 0.0
    broken[3, 2] = 0.0
    with pytest.raises(InvalidDataError, match="island"):
        power_spatial_determinant(y, strata, broken)
    with pytest.raises(InvalidDataError, match="positive total"):
        power_spatial_determinant(y, strata, broken, allow_islands=True)


def test_cpsd_is_one_when_response_equals_original_factor() -> None:
    x = np.asarray([0.0, 1.0, 2.0, 8.0, 9.0, 10.0])
    labels = np.asarray([1, 1, 1, 2, 2, 2])
    weights = _complete_weights(len(x))

    result = compensated_spatial_determinant(x, x, labels, weights)

    assert result.value == pytest.approx(1.0)
    assert result.response_psd.value == pytest.approx(result.information_psd.value)


def test_psmd_is_mean_of_accepted_cpsd_candidates() -> None:
    x = np.arange(24, dtype=float)
    y = np.repeat([0.0, 5.0, 10.0, 15.0], 6)
    weights = _complete_weights(len(x))

    result = multilevel_spatial_determinant(
        y,
        x,
        weights,
        n_strata=(2, 3, 4),
        method="quantile",
    )
    accepted = [
        candidate.result.value
        for candidate in result.candidates
        if candidate.result is not None
    ]

    assert result.value == pytest.approx(float(np.mean(accepted)))
    assert result.accepted_levels == (2, 3, 4)
    assert list(result.candidates_frame()["requested_strata"]) == [2, 3, 4]


def test_permutation_inference_is_reproducible() -> None:
    y = np.asarray([0.0, 0.2, 4.0, 4.2, 9.0, 9.2])
    strata = np.asarray([1, 1, 2, 2, 3, 3])
    weights = _complete_weights(len(y))

    first = power_spatial_determinant(
        y,
        strata,
        weights,
        permutations=19,
        random_state=42,
    )
    second = power_spatial_determinant(
        y,
        strata,
        weights,
        permutations=19,
        random_state=42,
    )

    assert first.p_value == second.p_value
    assert first.null_mean == second.null_mean
    assert first.p_value is not None and 0.0 < first.p_value <= 1.0


def test_spade_handles_explicit_continuous_and_categorical_factors() -> None:
    x = np.arange(24, dtype=float)
    y = np.repeat([0.0, 5.0, 10.0, 15.0], 6)
    category = np.repeat(["north", "south"], 12)
    factors = pd.DataFrame({"trend": x, "region": category})
    weights = _complete_weights(len(x))

    result = SPADE(n_strata=(2, 3, 4), method="quantile").fit(
        y,
        factors,
        weights,
        continuous_factors=("trend",),
    )
    frame = result.to_frame()

    assert result.continuous_factors == ("trend",)
    assert result.categorical_factors == ("region",)
    assert set(frame["statistic"]) == {"PSD", "PSMD"}
    with pytest.raises(InvalidDataError, match="unknown columns"):
        SPADE().fit(y, factors, weights, continuous_factors=("missing",))
