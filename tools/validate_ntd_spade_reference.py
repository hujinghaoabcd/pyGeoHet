"""Validate the non-redistributed gdverse NTD SPADE reference case."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from pygeohet import power_spatial_determinant

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "reference"
    / "ntd_spade_reference.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_prepared_data(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise SystemExit(
            "This optional validator requires geopandas and a spatial-index backend."
        ) from exc

    disease = gpd.read_file(path, layer="disease")
    watershed = gpd.read_file(path, layer="watershed")
    elevation = gpd.read_file(path, layer="elevation")
    soiltype = gpd.read_file(path, layer="soiltype")

    points = disease.copy()
    points.geometry = points.geometry.centroid
    prepared = gpd.sjoin(
        points,
        watershed[["watershed", "geometry"]],
        how="left",
        predicate="intersects",
    ).drop(columns=["index_right"])
    prepared = gpd.sjoin(
        prepared,
        elevation[["elevation", "geometry"]],
        how="left",
        predicate="intersects",
    ).drop(columns=["index_right"])
    prepared = gpd.sjoin(
        prepared,
        soiltype[["soiltype", "geometry"]],
        how="left",
        predicate="intersects",
    ).drop(columns=["index_right"])
    prepared = prepared.dropna(
        subset=["incidence", "watershed", "elevation", "soiltype"]
    ).reset_index(drop=True)

    coordinates = np.column_stack(
        (prepared.geometry.x.to_numpy(), prepared.geometry.y.to_numpy())
    )
    differences = coordinates[:, None, :] - coordinates[None, :, :]
    squared_distance = np.sum(differences * differences, axis=2, dtype=float)
    weights = np.zeros_like(squared_distance)
    mask = squared_distance > 0.0
    weights[mask] = 1.0 / squared_distance[mask]
    return (
        prepared["incidence"].to_numpy(dtype=float),
        prepared["soiltype"].to_numpy(),
        weights,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gpkg", type=Path, help="Path to gdverse NTDs.gpkg")
    args = parser.parse_args()

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    actual_hash = _sha256(args.gpkg)
    expected_hash = fixture["source_data_sha256"]
    if actual_hash != expected_hash:
        raise SystemExit(
            f"SHA-256 mismatch: expected {expected_hash}, received {actual_hash}"
        )

    y, strata, weights = _load_prepared_data(args.gpkg)
    expected_n = fixture["preparation"]["complete_observations"]
    if len(y) != expected_n:
        raise SystemExit(
            f"Expected {expected_n} complete observations, received {len(y)}"
        )

    result = power_spatial_determinant(y, strata, weights)
    expected = fixture["expected"]["psd_full_precision"]
    tolerance = fixture["tolerance"]["absolute_full_precision"]
    if not np.isclose(result.value, expected, rtol=0.0, atol=tolerance):
        raise SystemExit(
            f"PSD mismatch: expected {expected:.16g}, received {result.value:.16g}"
        )

    print(result.summary())
    print(f"SHA-256: {actual_hash}")
    print(f"PSD: {result.value:.16g}")
    print("NTD SPADE reference validation passed.")


if __name__ == "__main__":
    main()
