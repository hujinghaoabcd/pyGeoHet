import pandas as pd
import pytest

from pygeohet import FactorDetector
from pygeohet.exceptions import InvalidDataError


def test_stringified_factor_names_must_be_unique() -> None:
    frame = pd.DataFrame([["a", "u"], ["a", "u"], ["b", "v"], ["b", "v"]])
    frame.columns = [1, "1"]
    with pytest.raises(InvalidDataError):
        FactorDetector().fit([1.0, 1.2, 4.0, 4.2], frame)


def test_inputs_are_aligned_positionally_not_by_pandas_index() -> None:
    y = pd.Series([1.0, 1.2, 4.0, 4.2], index=[10, 11, 12, 13])
    x = pd.Series(["a", "a", "b", "b"], index=[100, 101, 102, 103])
    result = FactorDetector().fit(y, x)
    assert result["factor"].n_observations == 4
    assert result["factor"].q > 0.9
