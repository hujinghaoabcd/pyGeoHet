import numpy as np
import pytest

from pygeohet import (
    evaluate_stratification,
    optimize_stratification,
    stratify,
)


def test_equal_interval_preserves_lower_boundary() -> None:
    result = stratify([0.0, 2.0, 4.0, 6.0], method="equal", n_strata=3)

    assert result.cut_points == pytest.approx((2.0, 4.0))
    assert result.labels == (1, 1, 2, 3)


def test_quantile_collapses_duplicate_edges_without_splitting_ties() -> None:
    result = stratify(
        [1.0, 1.0, 1.0, 2.0, 3.0, 4.0],
        method="quantile",
        n_strata=4,
    )

    assert result.actual_strata < 4
    assert result.collapsed_strata > 0
    assert len(set(result.labels[:3])) == 1


def test_natural_breaks_finds_three_clear_clusters() -> None:
    values = [1.0, 1.1, 1.2, 10.0, 10.1, 10.2, 30.0, 30.1, 30.2]
    result = stratify(values, method="natural", n_strata=3)

    assert result.labels == (1, 1, 1, 2, 2, 2, 3, 3, 3)
    assert result.actual_strata == 3


def test_geometric_rejects_nonpositive_input() -> None:
    result = stratify([-1.0, 1.0, 2.0], method="geometric", n_strata=2)

    assert result.rejected
    assert "strictly positive" in str(result.rejection_reason)


def test_standard_deviation_uses_sample_standard_deviation() -> None:
    values = [0.0, 1.0, 2.0, 3.0, 4.0]
    result = stratify(values, method="sd", n_strata=3)

    expected_sd = np.std(values, ddof=1)
    assert result.metadata["sample_standard_deviation"] == pytest.approx(expected_sd)


def test_head_tail_breaks_determines_its_own_class_count() -> None:
    result = stratify(
        [1.0, 1.0, 1.0, 2.0, 3.0, 10.0, 100.0],
        method="headtails",
        n_strata=None,
    )

    assert result.requested_strata is None
    assert result.actual_strata >= 2
    assert result.metadata["threshold"] == 0.4


def test_missing_values_remain_aligned() -> None:
    result = stratify([1.0, None, 2.0, 3.0], method="equal", n_strata=2)

    assert result.labels[1] is None
    assert result.dropped_count == 1
    assert len(result.labels) == 4


def test_evaluation_matches_direct_q_and_is_auditable() -> None:
    y = [1.0, 1.2, 8.0, 8.2]
    stratification = stratify([0.0, 1.0, 10.0, 11.0], method="equal", n_strata=2)
    evaluation = evaluate_stratification(y, stratification)

    assert evaluation.accepted
    assert evaluation.q_result is not None
    assert evaluation.q_result.q > 0.99


def test_optimizer_retains_rejected_candidates_and_tie_rule() -> None:
    y = [1.0, 1.0, 8.0, 8.0, 1.1, 8.1]
    x = [-3.0, -2.0, 2.0, 3.0, -1.0, 1.0]
    result = optimize_stratification(
        y,
        x,
        methods=["geometric", "equal", "quantile"],
        n_strata=[2, 3],
    )
    frame = result.candidates_frame()

    assert len(frame) == 6
    assert (~frame["accepted"]).any()
    assert result.best is not None
    assert "maximum q" in result.tie_rule


def test_optimizer_uses_joint_complete_cases() -> None:
    result = optimize_stratification(
        [1.0, None, 8.0, 8.1],
        [0.0, 1000.0, 10.0, 11.0],
        methods=["equal"],
        n_strata=[2],
        min_stratum_size=1,
    )

    assert result.best is not None
    assert result.best.stratification.dropped_count == 1
    assert result.best.stratification.labels[1] is None
