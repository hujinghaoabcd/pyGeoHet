import numpy as np
import pandas as pd
import pytest

from pygeohet import EcologicalDetector


def test_ecological_detector_uses_joint_sample_and_primary_f_ratio() -> None:
    y = np.array([1.0, 1.2, 1.1, 4.0, 4.2, 4.1, 2.0, 5.0])
    factors = pd.DataFrame(
        {
            "strong": ["a", "a", "a", "b", "b", "b", "a", "b"],
            "weak": ["u", "u", "v", "v", "u", "v", "u", None],
        }
    )
    result = EcologicalDetector().fit(y, factors)
    comparison = result.comparisons[0]

    assert comparison.dropped_count == 1
    expected_f = (
        comparison.factor_1_result.within_ss / comparison.factor_2_result.within_ss
    )
    assert comparison.f_statistic == pytest.approx(expected_f)
    assert comparison.df1 == 6
    assert comparison.df2 == 6
    assert 0.0 <= comparison.p_value <= 1.0


def test_ecological_two_sided_p_value_is_orientation_invariant() -> None:
    y = [1.0, 1.1, 1.2, 5.0, 5.1, 5.2, 2.0, 4.0]
    x1 = ["a", "a", "a", "b", "b", "b", "a", "b"]
    x2 = ["u", "u", "v", "v", "u", "v", "u", "v"]

    forward = EcologicalDetector().fit(y, {"x1": x1, "x2": x2}).comparisons[0]
    reverse = EcologicalDetector().fit(y, {"x2": x2, "x1": x1}).comparisons[0]

    assert forward.f_statistic * reverse.f_statistic == pytest.approx(1.0)
    assert forward.p_value == pytest.approx(reverse.p_value)


def test_more_explanatory_factor_has_lower_within_ss_when_significant() -> None:
    y = [1.0, 1.0, 1.1, 1.1, 8.0, 8.0, 8.1, 8.1]
    strong = ["a", "a", "a", "a", "b", "b", "b", "b"]
    weak = ["u", "u", "v", "v", "u", "u", "v", "v"]
    comparison = (
        EcologicalDetector(alpha=0.2)
        .fit(y, {"strong": strong, "weak": weak})
        .comparisons[0]
    )

    assert comparison.factor_1_result.within_ss < comparison.factor_2_result.within_ss
    if comparison.significant:
        assert comparison.more_explanatory == "strong"


def test_greater_compatibility_is_order_dependent_by_design() -> None:
    y = [1.0, 1.0, 1.1, 1.1, 8.0, 8.0, 8.1, 8.1]
    strong = ["a", "a", "a", "a", "b", "b", "b", "b"]
    weak = ["u", "u", "v", "v", "u", "u", "v", "v"]

    forward = (
        EcologicalDetector(alternative="greater")
        .fit(y, {"strong": strong, "weak": weak})
        .comparisons[0]
    )
    reverse = (
        EcologicalDetector(alternative="greater")
        .fit(y, {"weak": weak, "strong": strong})
        .comparisons[0]
    )

    assert forward.p_value != pytest.approx(reverse.p_value)
    assert forward.f_statistic * reverse.f_statistic == pytest.approx(1.0)
