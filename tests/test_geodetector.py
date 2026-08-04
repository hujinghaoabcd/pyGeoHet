import pandas as pd

from pygeohet import GeoDetector, geodetector


def test_integrated_workflow_runs_all_classical_detectors() -> None:
    data = pd.DataFrame(
        {
            "y": [1.0, 1.2, 2.0, 2.2, 4.0, 4.2, 5.0, 5.2],
            "x1": ["a", "a", "b", "b", "a", "a", "b", "b"],
            "x2": ["u", "u", "u", "u", "v", "v", "v", "v"],
        }
    )
    result = GeoDetector().fit(data["y"], data[["x1", "x2"]])

    assert set(result.factor.factors) == {"x1", "x2"}
    assert len(result.risk.comparisons) == 2
    assert result.interaction is not None
    assert len(result.interaction.comparisons) == 1
    assert result.ecological is not None
    assert len(result.ecological.comparisons) == 1
    assert "Factor detector" in result.summary()


def test_functional_workflow_supports_one_factor() -> None:
    result = geodetector(
        [1.0, 1.2, 4.0, 4.2],
        ["a", "a", "b", "b"],
    )
    assert result.interaction is None
    assert result.ecological is None
    assert len(result.risk.comparisons) == 1
