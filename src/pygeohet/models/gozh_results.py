"""Immutable results for geographically optimal zone trees."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygeohet.core.interaction import InteractionType
from pygeohet.results import QStatisticResult

GOZHFactorType = Literal["continuous", "categorical"]
GOZHStopReason = Literal[
    "split",
    "min_split_size",
    "min_leaf_size",
    "max_depth",
    "constant_node",
    "no_candidate",
    "min_gain",
    "min_relative_gain",
]


@dataclass(frozen=True)
class GOZHSplitResult:
    """The selected binary split at one internal GOZH node."""

    factor: str
    factor_type: GOZHFactorType
    threshold: float | None
    left_categories: tuple[Any, ...]
    right_categories: tuple[Any, ...]
    child_ssw: float
    gain: float
    relative_gain: float
    left_count: int
    right_count: int
    candidate_count: int

    def to_series(self) -> pd.Series:
        """Return split evidence as a labelled series."""

        return pd.Series(
            {
                "factor": self.factor,
                "factor_type": self.factor_type,
                "threshold": self.threshold,
                "left_categories": self.left_categories,
                "right_categories": self.right_categories,
                "child_ssw": self.child_ssw,
                "gain": self.gain,
                "relative_gain": self.relative_gain,
                "left_count": self.left_count,
                "right_count": self.right_count,
                "candidate_count": self.candidate_count,
            }
        )


@dataclass(frozen=True)
class GOZHNodeResult:
    """One node in a deterministic GOZH binary tree."""

    path: tuple[int, ...]
    depth: int
    observation_indices: tuple[int, ...]
    count: int
    mean: float
    ssw: float
    terminal: bool
    stop_reason: GOZHStopReason
    split: GOZHSplitResult | None = None
    left_path: tuple[int, ...] | None = None
    right_path: tuple[int, ...] | None = None
    terminal_label: int | None = None

    def to_series(self) -> pd.Series:
        """Return node evidence as a labelled series."""

        split = self.split
        return pd.Series(
            {
                "path": self.path,
                "depth": self.depth,
                "count": self.count,
                "mean": self.mean,
                "ssw": self.ssw,
                "terminal": self.terminal,
                "stop_reason": self.stop_reason,
                "terminal_label": self.terminal_label,
                "factor": None if split is None else split.factor,
                "factor_type": None if split is None else split.factor_type,
                "threshold": None if split is None else split.threshold,
                "left_categories": (
                    None if split is None else split.left_categories
                ),
                "right_categories": (
                    None if split is None else split.right_categories
                ),
                "gain": None if split is None else split.gain,
                "relative_gain": None if split is None else split.relative_gain,
                "left_count": None if split is None else split.left_count,
                "right_count": None if split is None else split.right_count,
                "candidate_count": (
                    None if split is None else split.candidate_count
                ),
                "observation_indices": self.observation_indices,
            }
        )


@dataclass(frozen=True)
class GOZHTreeResult:
    """One fitted GOZH tree and complete terminal-zone evidence."""

    factors: tuple[str, ...]
    factor_types: Mapping[str, GOZHFactorType]
    nodes: tuple[GOZHNodeResult, ...]
    labels: tuple[int | None, ...]
    omega: float
    within_ss: float
    total_ss: float
    q_result: QStatisticResult | None
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]
    min_split_size: int
    min_leaf_size: int
    max_depth: int | None
    min_gain: float
    min_relative_gain: float
    objective_tolerance: float
    p_value: float | None = None
    permutations: int = 0
    null_mean: float | None = None
    null_standard_deviation: float | None = None
    random_state: int | None = None
    selection_adjusted: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "factor_types",
            MappingProxyType(dict(self.factor_types)),
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def n_zones(self) -> int:
        """Return the number of terminal zones."""

        return sum(node.terminal for node in self.nodes)

    @property
    def terminal_nodes(self) -> tuple[GOZHNodeResult, ...]:
        """Return terminal nodes ordered from left to right."""

        return tuple(
            sorted(
                (node for node in self.nodes if node.terminal),
                key=lambda node: node.path,
            )
        )

    def labels_array(self, *, missing_value: float = np.nan) -> np.ndarray:
        """Return aligned terminal labels, replacing dropped rows."""

        return np.asarray(
            [missing_value if label is None else label for label in self.labels],
            dtype=float,
        )

    def labels_series(self) -> pd.Series:
        """Return aligned terminal labels as an object series."""

        return pd.Series(self.labels, dtype=object, name="zone")

    def nodes_frame(self) -> pd.DataFrame:
        """Return the complete node table."""

        return pd.DataFrame([node.to_series() for node in self.nodes])

    def terminal_frame(self) -> pd.DataFrame:
        """Return one row per terminal zone."""

        return pd.DataFrame([node.to_series() for node in self.terminal_nodes])

    def to_series(self) -> pd.Series:
        """Return scalar tree fields."""

        return pd.Series(
            {
                "factors": self.factors,
                "omega": self.omega,
                "p_value": self.p_value,
                "conditional_q_p_value": (
                    None if self.q_result is None else self.q_result.p_value
                ),
                "n_zones": self.n_zones,
                "n_observations": self.n_observations,
                "dropped_count": self.dropped_count,
                "within_ss": self.within_ss,
                "total_ss": self.total_ss,
                "permutations": self.permutations,
                "selection_adjusted": self.selection_adjusted,
            }
        )

    def summary(self) -> str:
        """Return a compact terminal-friendly summary."""

        p_text = "None" if self.p_value is None else f"{self.p_value:.6g}"
        return (
            "GOZHTreeResult("
            f"factors={self.factors!r}, omega={self.omega:.6g}, "
            f"zones={self.n_zones}, p={p_text}, n={self.n_observations})"
        )


@dataclass(frozen=True)
class GOZHInteractionResult:
    """Individual and joint optimized trees for one factor pair."""

    factor_1: str
    factor_2: str
    omega_1: float
    omega_2: float
    omega_joint: float
    interaction_type: InteractionType
    joint_tree: GOZHTreeResult

    def to_series(self) -> pd.Series:
        """Return one interaction comparison row."""

        return pd.Series(
            {
                "factor_1": self.factor_1,
                "factor_2": self.factor_2,
                "omega_1": self.omega_1,
                "omega_2": self.omega_2,
                "omega_joint": self.omega_joint,
                "interaction_type": self.interaction_type.value,
                "joint_zones": self.joint_tree.n_zones,
                "joint_p_value": self.joint_tree.p_value,
            }
        )


@dataclass(frozen=True)
class GOZHSubsetCandidateResult:
    """One attempted multi-factor GOZH subset."""

    factors: tuple[str, ...]
    tree: GOZHTreeResult | None
    accepted: bool
    rejection_reason: str | None

    @property
    def omega(self) -> float | None:
        return None if self.tree is None else self.tree.omega

    def to_series(self) -> pd.Series:
        """Return one subset-search row."""

        return pd.Series(
            {
                "factors": self.factors,
                "size": len(self.factors),
                "accepted": self.accepted,
                "rejection_reason": self.rejection_reason,
                "omega": self.omega,
                "n_zones": None if self.tree is None else self.tree.n_zones,
                "p_value": None if self.tree is None else self.tree.p_value,
            }
        )


@dataclass(frozen=True)
class GOZHContributionResult:
    """One variable-removal contribution from the selected factor set."""

    factor: str
    full_omega: float
    reduced_omega: float
    raw_reduction: float
    adjusted_reduction: float | None
    relative_importance: float | None
    contribution: float | None
    valid: bool
    reason: str | None

    def to_series(self) -> pd.Series:
        """Return one contribution row."""

        return pd.Series(
            {
                "factor": self.factor,
                "full_omega": self.full_omega,
                "reduced_omega": self.reduced_omega,
                "raw_reduction": self.raw_reduction,
                "adjusted_reduction": self.adjusted_reduction,
                "relative_importance": self.relative_importance,
                "contribution": self.contribution,
                "valid": self.valid,
                "reason": self.reason,
            }
        )


@dataclass(frozen=True)
class GOZHSubsetSearchResult:
    """All attempted factor subsets, the selected tree, and removal allocation."""

    candidates: tuple[GOZHSubsetCandidateResult, ...]
    best: GOZHSubsetCandidateResult
    contributions: tuple[GOZHContributionResult, ...]
    omega_tolerance: float
    max_subset_size: int
    max_combinations: int

    def candidates_frame(self) -> pd.DataFrame:
        """Return every attempted factor subset."""

        return pd.DataFrame([candidate.to_series() for candidate in self.candidates])

    def contributions_frame(self) -> pd.DataFrame:
        """Return variable-removal contribution evidence."""

        return pd.DataFrame(
            [contribution.to_series() for contribution in self.contributions]
        )

    def summary(self) -> str:
        """Return a compact subset-search summary."""

        assert self.best.tree is not None
        return (
            "GOZHSubsetSearchResult("
            f"best={self.best.factors!r}, omega={self.best.tree.omega:.6g}, "
            f"attempted={len(self.candidates)})"
        )


@dataclass(frozen=True)
class GOZHResult:
    """Integrated individual, joint, pairwise, and subset GOZH evidence."""

    individual: Mapping[str, GOZHTreeResult]
    joint: GOZHTreeResult
    interactions: tuple[GOZHInteractionResult, ...]
    subset_search: GOZHSubsetSearchResult | None
    n_observations: int
    total_length: int
    dropped_count: int
    used_indices: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "individual", MappingProxyType(dict(self.individual)))

    def __getitem__(self, factor: str) -> GOZHTreeResult:
        return self.individual[factor]

    def individual_frame(self) -> pd.DataFrame:
        """Return one row per individually optimized factor."""

        rows: list[dict[str, Any]] = []
        for factor, tree in self.individual.items():
            row = tree.to_series().to_dict()
            row["factor"] = factor
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        frame = pd.DataFrame(rows)
        columns = ["factor", *[column for column in frame if column != "factor"]]
        return frame.loc[:, columns].sort_values(
            ["omega", "factor"],
            ascending=[False, True],
            kind="stable",
            ignore_index=True,
        )

    def interactions_frame(self) -> pd.DataFrame:
        """Return all pairwise optimized interactions."""

        return pd.DataFrame(
            [interaction.to_series() for interaction in self.interactions]
        )

    def summary(self) -> str:
        """Return individual scores followed by the joint model."""

        parts = [
            "GOZH individual factors",
            self.individual_frame().to_string(index=False),
            "",
            f"Joint: {self.joint.summary()}",
        ]
        if self.subset_search is not None:
            parts.extend(["", self.subset_search.summary()])
        return "\n".join(parts)
