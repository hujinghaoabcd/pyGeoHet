import numpy as np
import pandas as pd
import pytest

from pygeohet.exceptions import InvalidDataError, MissingDataError
from pygeohet.models.srsgd import (
    SRSGeoDetector,
    spatial_rough_set_measure,
    srs_ecological_detector,
    srs_factor_detector,
    srs_interaction_detector,
)


@pytest.fixture
def paper_example() -> tuple[pd.DataFrame, np.ndarray]:
    table = pd.DataFrame(
        {
            "a1": ["a", "b", "b", "b", "b", "c", "c", "d", "c", "a", "a"],
            "a2": ["b", "a", "a", "c", "c", "b", "c", "c", "b", "b", "b"],
            "a3": ["a", "a", "a", "a", "a", "c", "b", "b", "c", "a", "a"],
            "d": ["a", "a", "a", "b", "a", "a", "b", "b", "b", "b", "b"],
        }
    )
    adjacency = np.asarray(
        [
            [0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
            [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
        ],
        dtype=int,
    )
    return table, adjacency


def test_figure_one_a1_matches_hand_calculation(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    result = spatial_rough_set_measure(table["d"], table[["a1"]], adjacency)

    expected_local = np.asarray(
        [0.5, 0.0, 1.0, 0.6, 0.625, 1.0, 1.0, 1.0 / 3.0, 1.0, 1.0, 1.0]
    )
    expected_regions = (6, 6, 3, 5, 8, 4, 4, 6, 4, 5, 4)
    expected_positive = (3, 0, 3, 3, 5, 4, 4, 2, 4, 5, 4)

    assert np.asarray(result.local_quality, dtype=float) == pytest.approx(
        expected_local
    )
    assert result.region_size == expected_regions
    assert result.positive_region_size == expected_positive
    assert result.D == pytest.approx(0.7325757575757575)
    assert result.SE == pytest.approx(3.245554302578003)
    assert result.normalized_spatial_entropy == pytest.approx(
        result.SE / np.log2(len(table))
    )


def test_exact_feature_union_is_monotone(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    single = spatial_rough_set_measure(table["d"], table[["a1"]], adjacency)
    joint = spatial_rough_set_measure(table["d"], table[["a1", "a2"]], adjacency)

    assert joint.D == pytest.approx(0.8143939393939393)
    assert joint.SE == pytest.approx(3.3720204818904733)
    assert joint.D >= single.D
    assert np.all(
        np.asarray(joint.local_quality, dtype=float)
        >= np.asarray(single.local_quality, dtype=float)
    )


def test_interaction_reports_nonnegative_gain_and_entropy_direction(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    result = srs_interaction_detector(
        table["d"],
        table[["a1", "a2", "a3"]],
        adjacency,
        baseline="a1",
    )
    by_added = {
        comparison.added_features: comparison for comparison in result.comparisons
    }

    a2 = by_added[("a2",)]
    assert a2.power_gain == pytest.approx(0.8143939393939393 - 0.7325757575757575)
    assert a2.heterogeneity_change == "decreased"

    a3 = by_added[("a3",)]
    assert a3.power_gain == pytest.approx(0.0)
    assert a3.p_value == pytest.approx(1.0)
    assert a3.heterogeneity_change == "unchanged"


def test_factor_and_ecological_detectors_share_complete_sample(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    factors = srs_factor_detector(table["d"], table[["a1", "a2", "a3"]], adjacency)
    ecological = srs_ecological_detector(
        table["d"], table[["a1", "a2", "a3"]], adjacency
    )

    assert set(factors.factors) == {"a1", "a2", "a3"}
    assert len(ecological.comparisons) == 3
    assert all(
        comparison.result_1.used_indices == comparison.result_2.used_indices
        for comparison in ecological.comparisons
    )
    assert not factors.to_frame().empty
    assert not ecological.to_frame().empty


def test_row_and_adjacency_permutation_preserves_measure(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    permutation = np.asarray([5, 2, 10, 0, 7, 4, 1, 9, 3, 8, 6])
    original = spatial_rough_set_measure(table["d"], table[["a1"]], adjacency)
    permuted = spatial_rough_set_measure(
        table.iloc[permutation]["d"].reset_index(drop=True),
        table.iloc[permutation][["a1"]].reset_index(drop=True),
        adjacency[np.ix_(permutation, permutation)],
    )

    restored = np.empty(len(table), dtype=float)
    restored[permutation] = np.asarray(permuted.local_quality, dtype=float)
    assert permuted.D == pytest.approx(original.D)
    assert permuted.SE == pytest.approx(original.SE)
    assert restored == pytest.approx(np.asarray(original.local_quality, dtype=float))


def test_focal_object_is_added_even_when_diagonal_is_zero(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    with_diagonal = adjacency.copy()
    np.fill_diagonal(with_diagonal, 1)

    first = spatial_rough_set_measure(table["d"], table[["a1"]], adjacency)
    second = spatial_rough_set_measure(table["d"], table[["a1"]], with_diagonal)

    assert second.local_quality == first.local_quality
    assert second.region_size == first.region_size


def test_islands_are_explicit_and_opt_in(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    isolated = adjacency.copy()
    isolated[0, :] = 0
    isolated[:, 0] = 0

    with pytest.raises(InvalidDataError, match="without neighbours"):
        spatial_rough_set_measure(table["d"], table[["a1"]], isolated)

    result = spatial_rough_set_measure(
        table["d"],
        table[["a1"]],
        isolated,
        allow_islands=True,
    )
    assert result.island_indices == (0,)
    assert result.region_size[0] == 1
    assert result.positive_region_size[0] == 1
    assert result.local_quality[0] == pytest.approx(1.0)


def test_missing_rows_subset_both_adjacency_axes(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    changed = table.copy()
    changed.loc[2, "a1"] = None

    result = spatial_rough_set_measure(changed["d"], changed[["a1"]], adjacency)

    assert result.dropped_count == 1
    assert result.local_quality[2] is None
    assert result.region_size[2] is None
    assert 2 not in result.used_indices
    with pytest.raises(MissingDataError):
        spatial_rough_set_measure(
            changed["d"], changed[["a1"]], adjacency, missing="raise"
        )


def test_continuous_target_and_factor_are_rejected(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    continuous_target = np.linspace(0.1, 1.1, len(table))
    with pytest.raises(InvalidDataError, match="nominal or deliberately discretized"):
        spatial_rough_set_measure(continuous_target, table[["a1"]], adjacency)

    continuous_factor = pd.DataFrame({"x": np.linspace(0.1, 1.1, len(table))})
    with pytest.raises(InvalidDataError, match="nominal or deliberately discretized"):
        spatial_rough_set_measure(table["d"], continuous_factor, adjacency)


def test_asymmetric_adjacency_requires_explicit_relaxation(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    directed = adjacency.copy()
    directed[0, 1] = 0

    with pytest.raises(InvalidDataError, match="must be symmetric"):
        spatial_rough_set_measure(table["d"], table[["a1"]], directed)

    result = spatial_rough_set_measure(
        table["d"],
        table[["a1"]],
        directed,
        require_symmetric=False,
    )
    assert result.adjacency_symmetric is False


def test_seeded_paper_style_sample_is_reproducible(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    first = spatial_rough_set_measure(
        table["d"],
        table[["a1"]],
        adjacency,
        sample_size=6,
        random_state=9,
    )
    second = spatial_rough_set_measure(
        table["d"],
        table[["a1"]],
        adjacency,
        sample_size=6,
        random_state=9,
    )

    assert first.test_sample_indices == second.test_sample_indices
    assert first.t_statistic == second.t_statistic
    assert first.p_value == second.p_value


def test_integrated_workflow_returns_three_detector_families(
    paper_example: tuple[pd.DataFrame, np.ndarray],
) -> None:
    table, adjacency = paper_example
    result = SRSGeoDetector(baseline="a1").fit(
        table["d"], table[["a1", "a2", "a3"]], adjacency
    )

    assert len(result.factor.factors) == 3
    assert len(result.ecological.comparisons) == 3
    assert len(result.interaction.comparisons) == 2
    assert "SRSGeoDetectorResult" in result.summary()
