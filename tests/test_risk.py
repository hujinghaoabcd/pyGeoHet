import numpy as np
import pytest
from scipy.stats import t as student_t

from pygeohet import RiskDetector


def test_risk_detector_matches_manual_welch_test() -> None:
    y = np.array([1.0, 1.2, 1.4, 3.0, 3.5, 4.0])
    x = np.array(["a", "a", "a", "b", "b", "b"])
    result = RiskDetector().fit(y, x)
    comparison = result.comparisons[0]

    y1 = y[:3]
    y2 = y[3:]
    var1 = np.var(y1, ddof=1)
    var2 = np.var(y2, ddof=1)
    a = var1 / len(y1)
    b = var2 / len(y2)
    expected_t = (np.mean(y1) - np.mean(y2)) / np.sqrt(a + b)
    expected_df = (a + b) ** 2 / (a**2 / 2 + b**2 / 2)
    expected_p = 2.0 * student_t.sf(abs(expected_t), expected_df)

    assert comparison.t_statistic == pytest.approx(expected_t)
    assert comparison.df == pytest.approx(expected_df)
    assert comparison.p_value == pytest.approx(expected_p)
    assert comparison.significant is True


def test_risk_detector_reports_means_and_symmetric_matrix() -> None:
    y = [1.0, 1.2, 3.0, 3.2, 5.0, 5.2]
    x = ["a", "a", "b", "b", "c", "c"]
    result = RiskDetector().fit(y, x)
    means = result.means_frame()
    matrix = result.pvalue_matrix("factor")

    assert means.shape[0] == 3
    assert means.set_index("stratum").loc["a", "mean"] == pytest.approx(1.1)
    assert matrix.loc["a", "b"] == pytest.approx(matrix.loc["b", "a"])
    assert np.allclose(np.diag(matrix), 1.0)


def test_zero_variance_groups_have_deterministic_limits() -> None:
    different = RiskDetector().fit([1.0, 1.0, 2.0, 2.0], ["a", "a", "b", "b"])
    same = RiskDetector().fit([1.0, 1.0, 1.0, 1.0], ["a", "a", "b", "b"])

    assert np.isinf(different.comparisons[0].t_statistic)
    assert different.comparisons[0].p_value == 0.0
    assert same.comparisons[0].t_statistic == 0.0
    assert same.comparisons[0].p_value == 1.0
