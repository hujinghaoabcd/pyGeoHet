import pandas as pd
import pytest

from pygeohet import OPGD, opgd


def _continuous_case() -> tuple[list[float], pd.DataFrame]:
    y = [
        1.0,
        1.1,
        0.9,
        1.2,
        5.0,
        5.1,
        4.9,
        5.2,
        10.0,
        10.1,
        9.9,
        10.2,
    ]
    factors = pd.DataFrame(
        {
            "x1": [0.0, 0.2, 0.4, 0.6, 5.0, 5.2, 5.4, 5.6, 10.0, 10.2, 10.4, 10.6],
            "x2": [1.0, 1.2, 1.4, 1.6, 3.0, 3.2, 3.4, 3.6, 8.0, 8.2, 8.4, 8.6],
        }
    )
    return y, factors


def test_opgd_retains_candidates_and_runs_classical_workflow() -> None:
    y, factors = _continuous_case()
    result = OPGD(
        methods=["equal", "quantile", "natural"],
        n_strata=[2, 3],
    ).fit(y, factors)

    assert set(result.optimizations) == {"x1", "x2"}
    assert len(result.candidates_frame()) == 12
    assert result.discretized_frame().shape == factors.shape
    assert result.detector.factor["x1"].q > 0.9
    assert result.detector.interaction is not None


def test_opgd_functional_interface_and_optimal_frame() -> None:
    y, factors = _continuous_case()
    result = opgd(
        y,
        factors[["x1"]],
        methods=["equal", "natural"],
        n_strata=[2, 3],
    )
    optimum = result.optimal_frame().iloc[0]

    assert optimum["factor"] == "x1"
    assert optimum["q"] == pytest.approx(result.detector.factor["x1"].q)
    assert result.detector.interaction is None


def test_opgd_raises_when_every_candidate_is_invalid() -> None:
    y = [1.0, 2.0, 3.0, 4.0]
    factors = pd.DataFrame({"x": [-2.0, -1.0, 1.0, 2.0]})

    with pytest.raises(ValueError, match="no valid discretization"):
        OPGD(methods=["geometric"], n_strata=[2]).fit(y, factors)
