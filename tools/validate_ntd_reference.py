"""Validate pyGeoHet against the non-redistributed NTD reference dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from pygeohet import GeoDetector


def _assert_close(actual: float, expected: float, tolerance: float, label: str) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"{label}: actual={actual:.16g}, expected={expected:.16g}, "
            f"tolerance={tolerance}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path, help="Path to the NTD disease CSV")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("tests/fixtures/reference/ntd_classic_reference.json"),
    )
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    digest = hashlib.sha256(args.csv.read_bytes()).hexdigest()
    expected_digest = fixture["input"]["sha256"]
    if digest != expected_digest:
        raise AssertionError(
            f"input SHA-256 mismatch: actual={digest}, expected={expected_digest}"
        )

    data = pd.read_csv(args.csv).rename(columns=fixture["input"]["column_mapping"])
    factors = data[["watershed", "elevation", "soiltype"]]
    result = GeoDetector(ecological_alternative="two-sided").fit(
        data["incidence"], factors
    )
    compatibility = GeoDetector(ecological_alternative="greater").fit(
        data["incidence"], factors
    )
    tolerances = fixture["tolerances"]

    factor_expected = fixture["gdverse_gd_vignette"]["factor"]
    for row in result.factor.to_frame().itertuples(index=False):
        expected = factor_expected[row.factor]
        _assert_close(row.q, expected["q"], tolerances["q_abs"], f"{row.factor}.q")
        _assert_close(
            row.p_value,
            expected["p_value"],
            tolerances["p_abs"],
            f"{row.factor}.p_value",
        )

    interaction_expected = fixture["gdverse_gd_vignette"]["interaction"]
    for row in result.interaction.to_frame().itertuples(index=False):
        key = f"{row.factor_1}__{row.factor_2}"
        if row.interaction != interaction_expected[key]:
            raise AssertionError(
                f"{key}.interaction: actual={row.interaction}, "
                f"expected={interaction_expected[key]}"
            )

    actual_risk = {
        factor: int(count)
        for factor, count in result.risk.comparisons_frame()
        .groupby("factor")["significant"]
        .sum()
        .items()
    }
    if actual_risk != fixture["gdverse_gd_vignette"]["risk_significant_pair_counts"]:
        raise AssertionError(
            f"risk significant-pair counts differ: actual={actual_risk}"
        )

    expected_ecological = fixture["gdverse_gd_vignette"][
        "ecological_greater_tail_significant"
    ]
    for row in compatibility.ecological.to_frame().itertuples(index=False):
        key = f"{row.factor_1}__{row.factor_2}"
        if bool(row.significant) is not bool(expected_ecological[key]):
            raise AssertionError(
                f"{key}.ecological compatibility: actual={row.significant}, "
                f"expected={expected_ecological[key]}"
            )

    print("NTD reference validation passed.")


if __name__ == "__main__":
    main()
