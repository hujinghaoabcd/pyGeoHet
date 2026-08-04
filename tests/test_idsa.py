import numpy as np
import pandas as pd
import pytest

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.idsa import (
    IDSA,
    fuzzy_overlay,
    optimize_spatial_discretization,
    power_interactive_determinant,
)


def _complete_weights(n: int) -> np.ndarray:
    weights = np.ones((n, n), dtype=float)
    np.fill_diagonal(weights, 0.0)
    return weights


def test_fuzzy_and_or_match_manual_risk_memberships() -> None:
    y = np.asarray([0.0, 2.0, 8.0, 10.0])
    factors = pd.DataFrame(
        {
            "a": [1, 1, 2, 2],
            "b": [1, 2, 1, 2],
        }
    )

    fuzzy_and = fuzzy_overlay(y, factors, operation="and")
    fuzzy_or = fuzzy_overlay(y, factors, operation="or")

    assert fuzzy_and.labels == (
        ("a", 1),
        ("a", 1),
        ("b", 1),
        ("b", 2),
    )
    assert fuzzy_or.labels == (
        ("b", 1),
        ("b", 2),
        ("a", 2),
        ("a", 2),
    )
    risk = fuzzy_and.risk_frame().set_index(["factor", "stratum"])
    assert risk.loc[("a", 1), "membership"] == pytest.approx(0.0)
    assert risk.loc[("a", 2), "membership"] == pytest.approx(1.0)
    assert risk.loc[("b", 1), "membership"] == pytest.approx(0.375)
    assert risk.loc[("b", 2), "membership"] == pytest.approx(0.625)


def test_fuzzy_ties_use_explicit_factor_order() -> None:
    y = np.asarray([0.0, 2.0, 2.0, 4.0])
    factors = pd.DataFrame(
        {
            "first": [1, 1, 2, 2],
            "second": [1, 2, 1, 2],
        }
    )

    first = fuzzy_overlay(y, factors, tie_policy="first")
    last = fuzzy_overlay(y, factors, tie_policy="last")

    assert first.labels[0] == ("first", 1)
    assert last.labels[0] == ("second", 1)
    assert first.labels[3] == ("first", 2)
    assert last.labels[3] == ("second", 2)
    assert first.tied_row_count == 2


def test_constant_risk_and_missing_contracts_are_explicit() -> None:
    factors = pd.DataFrame({"a": [1, 1, 2, 2], "b": [1, 2, 1, 2]})
    with pytest.raises(InvalidDataError, match="memberships are undefined"):
        fuzzy_overlay(np.ones(4), factors)

    y = [0.0, 1.0, np.nan, 3.0, 4.0, 5.0]
    expanded = pd.DataFrame(
        {
            "a": [1, 1, 1, 2, 2, 2],
            "b": [1, 1, 2, 2, 3, 3],
        }
    )
    result = fuzzy_overlay(y, expanded)
    assert result.labels[2] is None
    assert result.dropped_count == 1
    with pytest.raises(MissingDataError):
        fuzzy_overlay(y, expanded, missing="raise")


def test_pid_components_follow_published_ratio() -> None:
    base_y = np.asarray([0.0, 2.0, 8.0, 10.0])
    y = np.tile(base_y, 3)
    factors = pd.DataFrame(
        {
            "a": np.tile([1, 1, 2, 2], 3),
            "b": np.tile([1, 2, 1, 2], 3),
        }
    )
    weights = _complete_weights(len(y))

    result = power_interactive_determinant(y, factors, weights)
    within = sum(
        item.within_weighted_variance for item in result.information_components.values()
    )
    total = sum(
        item.total_weighted_variance for item in result.information_components.values()
    )

    assert result.phi == pytest.approx(1.0 - within / total)
    assert result.value == pytest.approx(result.theta.value / result.phi)
    assert result.overlay.zone_count == 3
    assert result.finely_divided_zone_count == 0


def test_pid_canonicalizes_shifted_ordinal_codes() -> None:
    y = np.tile(np.asarray([0.0, 2.0, 8.0, 10.0]), 3)
    original = pd.DataFrame(
        {
            "a": np.tile([1, 1, 2, 2], 3),
            "b": np.tile([1, 2, 1, 2], 3),
        }
    )
    shifted = original * 10 + 7
    weights = _complete_weights(len(y))

    first = power_interactive_determinant(y, original, weights)
    second = power_interactive_determinant(y, shifted, weights)

    assert second.value == pytest.approx(first.value)
    assert second.theta.value == pytest.approx(first.theta.value)
    assert second.phi == pytest.approx(first.phi)


def test_pid_permutation_inference_recomputes_fuzzy_zones() -> None:
    y = np.tile(np.asarray([0.0, 2.0, 8.0, 10.0]), 5)
    factors = pd.DataFrame(
        {
            "a": np.tile([1, 1, 2, 2], 5),
            "b": np.tile([1, 2, 1, 2], 5),
        }
    )
    weights = _complete_weights(len(y))

    first = power_interactive_determinant(
        y,
        factors,
        weights,
        permutations=19,
        random_state=42,
    )
    second = power_interactive_determinant(
        y,
        factors,
        weights,
        permutations=19,
        random_state=42,
    )

    assert first.p_value == second.p_value
    assert first.valid_permutations + first.failed_permutations == 19
    assert first.metadata["overlay_recomputed_under_permutation"] is True


def test_spatial_discretization_prefers_simpler_cpsd_tie() -> None:
    x = np.arange(24, dtype=float)
    y = x.copy()
    weights = _complete_weights(len(x))

    result = optimize_spatial_discretization(
        y,
        x,
        weights,
        methods=("quantile", "equal_interval"),
        n_strata=(2, 3),
    )

    assert result.best.method == "quantile"
    assert result.best.requested_strata == 2
    assert result.best.result is not None
    assert result.best.result.value == pytest.approx(1.0)
    assert len(result.candidates) == 4


def test_idsa_exhaustive_and_greedy_return_auditable_models() -> None:
    x1_base = np.repeat(np.arange(4, dtype=float), 4)
    x2_base = np.tile(np.repeat(np.arange(2, dtype=float), 2), 4)
    x3_base = np.tile(np.arange(4, dtype=float), 4)
    x1 = np.tile(x1_base, 4)
    x2 = np.tile(x2_base, 4)
    x3 = np.tile(x3_base, 4)
    y = 4.0 * x1 + 2.0 * x2 + 0.5 * x3
    factors = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3})
    weights = _complete_weights(len(y))

    exhaustive = IDSA(
        methods=("quantile",),
        n_strata=(2, 3),
        search="exhaustive",
    ).fit(y, factors, weights)
    greedy = IDSA(
        methods=("quantile",),
        n_strata=(2, 3),
        search="greedy",
    ).fit(y, factors, weights)

    assert exhaustive.best.result is not None
    assert len(exhaustive.best.factors) >= 2
    assert len(exhaustive.combinations) == 4
    assert set(exhaustive.discretizations) == {"x1", "x2", "x3"}
    assert greedy.best.result is not None
    assert not greedy.combinations_frame().empty
    assert len(greedy.best.result.overlay.labels) == len(y)


def test_idsa_joint_missing_sample_is_restored() -> None:
    y = np.tile(np.asarray([0.0, 2.0, 8.0, 10.0]), 4)
    x1 = np.tile([0.0, 0.0, 1.0, 1.0], 4)
    x2 = np.tile([0.0, 1.0, 0.0, 1.0], 4)
    x1[3] = np.nan
    factors = pd.DataFrame({"x1": x1, "x2": x2})
    weights = _complete_weights(len(y))

    result = IDSA(
        methods=("quantile",),
        n_strata=(2,),
        search="exhaustive",
    ).fit(y, factors, weights)

    assert result.discrete_labels["x1"][3] is None
    assert result.best.result is not None
    assert result.best.result.overlay.labels[3] is None
