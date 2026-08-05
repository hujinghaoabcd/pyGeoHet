import numpy as np
import pandas as pd
import pytest

from pygeohet.exceptions import InvalidDataError, MissingDataError, SmallStratumError
from pygeohet.models.information import (
    InformationConsistency,
    continuous_information_consistency,
    information_consistency,
    nominal_information_consistency,
)


def _binary_entropy(probability: float) -> float:
    return -probability * np.log(probability) - (1.0 - probability) * np.log(
        1.0 - probability
    )


def test_nominal_perfect_consistency_is_one() -> None:
    target = ["low", "low", "high", "high"]
    strata = ["a", "a", "b", "b"]

    result = nominal_information_consistency(target, strata)

    assert result.IN == pytest.approx(1.0)
    assert result.conditional_entropy == pytest.approx(0.0)
    assert result.mutual_information == pytest.approx(result.target_entropy)
    assert len(result.contingency_frame()) == 2


def test_nominal_independence_is_zero() -> None:
    target = [0, 1, 0, 1, 0, 1, 0, 1]
    strata = ["a", "a", "b", "b", "c", "c", "d", "d"]

    result = nominal_information_consistency(target, strata)

    assert result.IN == pytest.approx(0.0)
    assert result.conditional_entropy == pytest.approx(result.target_entropy)
    assert result.mutual_information == pytest.approx(0.0)


def test_nominal_partial_consistency_matches_hand_calculation() -> None:
    target = [0, 0, 1, 1]
    strata = ["a", "a", "a", "b"]
    expected_entropy = np.log(2.0)
    expected_conditional = 0.75 * _binary_entropy(2.0 / 3.0)
    expected = 1.0 - expected_conditional / expected_entropy

    result = nominal_information_consistency(
        target,
        strata,
        min_stratum_size=1,
    )

    assert result.target_entropy == pytest.approx(expected_entropy)
    assert result.conditional_entropy == pytest.approx(expected_conditional)
    assert result.IN == pytest.approx(expected)


def test_nominal_category_relabeling_is_invariant() -> None:
    target = [0, 0, 1, 1, 2, 2]
    strata = [1, 1, 2, 2, 2, 3]
    first = nominal_information_consistency(
        target,
        strata,
        min_stratum_size=1,
    )
    second = nominal_information_consistency(
        ["x", "x", "z", "z", "y", "y"],
        ["north", "north", "west", "west", "west", "east"],
        min_stratum_size=1,
    )

    assert second.IN == pytest.approx(first.IN)
    assert second.target_entropy == pytest.approx(first.target_entropy)
    assert second.conditional_entropy == pytest.approx(first.conditional_entropy)


def test_nominal_permutation_is_seeded_and_corrected() -> None:
    target = np.repeat([0, 1], 10)
    strata = np.repeat(["a", "b"], 10)

    first = nominal_information_consistency(
        target,
        strata,
        permutations=19,
        random_state=7,
    )
    second = nominal_information_consistency(
        target,
        strata,
        permutations=19,
        random_state=7,
    )

    assert first.p_value == second.p_value
    assert first.null_mean == second.null_mean
    assert first.p_value is not None
    assert 1.0 / 20.0 <= first.p_value <= 1.0
    assert first.metadata["p_value"] == "(1 + exceedances) / (B + 1)"


def test_nominal_constant_target_is_undefined() -> None:
    with pytest.raises(InvalidDataError, match="target is constant"):
        nominal_information_consistency([1, 1, 1, 1], ["a", "a", "b", "b"])


def test_continuous_separated_strata_match_hand_calculation() -> None:
    target = np.asarray([0.0, 0.0, 1.0, 1.0, 10.0, 10.0, 11.0, 11.0])
    strata = np.asarray(["a"] * 4 + ["b"] * 4)
    expected_kl = np.log(2.0)
    expected = np.arctan(expected_kl) / (np.pi / 2.0)

    result = continuous_information_consistency(
        target,
        strata,
        bins=(-0.5, 5.5, 11.5),
    )

    assert result.IC == pytest.approx(expected)
    assert result.global_histogram_probabilities == pytest.approx((0.5, 0.5))
    assert all(
        contribution.kl_divergence == pytest.approx(expected_kl)
        for contribution in result.contributions
    )
    assert sum(
        contribution.weighted_contribution
        for contribution in result.contributions
    ) == pytest.approx(result.IC)


def test_continuous_identical_stratum_distributions_are_zero() -> None:
    target = np.tile([0.0, 1.0], 4)
    strata = np.repeat(["a", "b", "c", "d"], 2)

    result = continuous_information_consistency(
        target,
        strata,
        bins=(-0.5, 0.5, 1.5),
    )

    assert result.IC == pytest.approx(0.0)
    assert all(
        contribution.kl_divergence == pytest.approx(0.0)
        for contribution in result.contributions
    )


def test_continuous_affine_transformation_is_invariant_with_automatic_bins() -> None:
    target = np.asarray([0.0, 0.4, 0.8, 1.2, 5.0, 5.4, 5.8, 6.2])
    strata = np.asarray(["a"] * 4 + ["b"] * 4)

    first = continuous_information_consistency(target, strata, bins="sturges")
    second = continuous_information_consistency(
        3.0 * target + 7.0,
        strata,
        bins="sturges",
    )

    assert second.IC == pytest.approx(first.IC)
    assert second.global_histogram_probabilities == pytest.approx(
        first.global_histogram_probabilities
    )
    assert [item.kl_divergence for item in second.contributions] == pytest.approx(
        [item.kl_divergence for item in first.contributions]
    )


def test_continuous_permutation_is_seeded_and_uses_fixed_edges() -> None:
    target = np.asarray([0.0, 0.2, 0.4, 0.6, 5.0, 5.2, 5.4, 5.6])
    strata = np.asarray(["a"] * 4 + ["b"] * 4)

    first = continuous_information_consistency(
        target,
        strata,
        bins=3,
        permutations=19,
        random_state=11,
    )
    second = continuous_information_consistency(
        target,
        strata,
        bins=3,
        permutations=19,
        random_state=11,
    )

    assert first.p_value == second.p_value
    assert first.null_mean == second.null_mean
    assert first.bin_edges == second.bin_edges
    assert first.p_value is not None
    assert 1.0 / 20.0 <= first.p_value <= 1.0


def test_continuous_histogram_methods_return_valid_edges() -> None:
    target = np.linspace(0.0, 10.0, 40)
    strata = np.repeat(["a", "b"], 20)

    for method in ("sturges", "square_root", "rice", "scott", "fd"):
        result = continuous_information_consistency(target, strata, bins=method)
        assert 0.0 <= result.IC <= 1.0
        assert result.bin_count >= 2
        assert np.all(np.diff(result.bin_edges) > 0.0)


def test_continuous_invalid_edges_and_small_strata_are_explicit() -> None:
    target = [0.0, 1.0, 2.0, 3.0]
    strata = ["a", "a", "a", "b"]

    with pytest.raises(ValueError, match="cover the complete target range"):
        continuous_information_consistency(
            target,
            strata,
            bins=(0.5, 1.5, 2.5),
            min_stratum_size=1,
        )
    with pytest.raises(SmallStratumError):
        continuous_information_consistency(target, strata, bins=2)


def test_information_workflow_uses_one_joint_complete_sample() -> None:
    target = pd.Series([0, 0, 1, 1, 0, 1, 0, 1], dtype=object)
    factors = pd.DataFrame(
        {
            "perfect": ["a", "a", "b", "b", "a", "b", "a", "b"],
            "mixed": ["a", "b", "a", "b", "a", "b", None, "b"],
        }
    )

    result = InformationConsistency(target_kind="nominal").fit(target, factors)

    assert result.dropped_count == 1
    assert result.used_indices == (0, 1, 2, 3, 4, 5, 7)
    assert all(item.used_indices == result.used_indices for item in result.factors.values())
    assert result["perfect"].IN > result["mixed"].IN
    assert list(result.to_frame()["factor"])[0] == "perfect"


def test_functional_workflow_and_missing_raise() -> None:
    target = [0.0, 0.5, 4.0, 4.5, 8.0, 8.5]
    factors = pd.DataFrame(
        {
            "grouped": [1, 1, 2, 2, 3, 3],
            "mixed": [1, 2, 3, 1, 2, 3],
        }
    )
    result = information_consistency(
        target,
        factors,
        target_kind="continuous",
        bins=3,
    )

    assert result.target_kind == "continuous"
    assert result["grouped"].IC > result["mixed"].IC

    factors.loc[1, "mixed"] = None
    with pytest.raises(MissingDataError):
        InformationConsistency(
            target_kind="continuous",
            missing="raise",
            bins=3,
        ).fit(target, factors)
