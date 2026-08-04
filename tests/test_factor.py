import numpy as np
import pandas as pd
import pytest

from pygeohet import FactorDetector, factor_detector


def test_factor_detector_preserves_factor_order() -> None:
    frame = pd.DataFrame(
        {
            "strong": ["a", "a", "b", "b", "c", "c"],
            "weak": ["x", "y", "x", "y", "x", "y"],
        }
    )
    y = [1.0, 1.1, 4.0, 4.2, 8.0, 8.1]
    result = FactorDetector().fit(y, frame)
    table = result.to_frame()
    assert table["factor"].tolist() == ["strong", "weak"]
    assert result["strong"].q > result["weak"].q


def test_functional_interface_accepts_mapping() -> None:
    result = factor_detector(
        [1.0, 1.1, 4.0, 4.2],
        {"zone": ["a", "a", "b", "b"]},
    )
    assert result["zone"].q == pytest.approx(0.9973197534173144)


def test_one_dimensional_factor_gets_stable_name() -> None:
    result = FactorDetector().fit(
        np.array([1.0, 1.2, 4.8, 5.0]),
        np.array([0, 0, 1, 1]),
    )
    assert list(result.factors) == ["factor"]


def test_factorwise_missing_counts_are_visible() -> None:
    y = [1.0, 1.2, 4.8, 5.0, 9.0, 9.2]
    factors = pd.DataFrame(
        {
            "complete": ["a", "a", "b", "b", "c", "c"],
            "incomplete": ["a", "a", "b", "b", None, None],
        }
    )
    result = FactorDetector().fit(y, factors)
    assert result["complete"].n_observations == 6
    assert result["incomplete"].n_observations == 4
    assert result["incomplete"].dropped_count == 2
