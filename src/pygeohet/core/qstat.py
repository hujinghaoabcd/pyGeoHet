"""Classical q-statistic for spatially stratified heterogeneity."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ncf

from pygeohet.exceptions import ConstantResponseError
from pygeohet.results import QStatisticResult
from pygeohet.validation import MissingPolicy, prepare_factor_data


def q_statistic(
    y: Any,
    strata: Any,
    *,
    missing: MissingPolicy = "drop",
    min_stratum_size: int = 2,
) -> QStatisticResult:
    """Compute the classical q-statistic and noncentral-F significance."""

    prepared = prepare_factor_data(
        y,
        strata,
        missing=missing,
        min_stratum_size=min_stratum_size,
    )
    y_array = prepared.y
    labels = prepared.strata
    n = int(y_array.size)
    n_strata = int(len(prepared.counts))

    overall_mean = float(np.mean(y_array))
    centered = y_array - overall_mean
    total_ss = float(np.dot(centered, centered))
    scale = max(1.0, float(np.dot(y_array, y_array)))
    if total_ss <= np.finfo(float).eps * scale:
        raise ConstantResponseError("y must have nonzero total sum of squares")

    frame = pd.DataFrame({"y": y_array, "strata": labels})
    grouped = frame.groupby("strata", sort=False, observed=True)["y"]
    means = grouped.mean()
    counts = grouped.size().astype(int)

    mean_by_row = frame["strata"].map(means).to_numpy(dtype=float)
    residuals = y_array - mean_by_row
    within_ss = float(np.dot(residuals, residuals))
    between_ss = float(total_ss - within_ss)

    tolerance = 128.0 * np.finfo(float).eps * max(1.0, total_ss)
    if abs(within_ss) <= tolerance:
        within_ss = 0.0
    if abs(between_ss) <= tolerance:
        between_ss = 0.0
    within_ss = min(max(within_ss, 0.0), total_ss)
    between_ss = min(max(between_ss, 0.0), total_ss)

    q = float(min(max(between_ss / total_ss, 0.0), 1.0))
    df1 = n_strata - 1
    df2 = n - n_strata
    if q >= 1.0:
        f_statistic = float("inf")
    elif q <= 0.0:
        f_statistic = 0.0
    else:
        f_statistic = float((df2 * q) / (df1 * (1.0 - q)))

    population_variance = total_ss / n
    mean_values = means.to_numpy(dtype=float)
    count_values = counts.to_numpy(dtype=float)
    first_term = float(np.dot(mean_values, mean_values))
    weighted_mean_sum = float(np.dot(mean_values, np.sqrt(count_values)))
    noncentrality = (first_term - weighted_mean_sum**2 / n) / population_variance
    noncentrality = float(max(noncentrality, 0.0))

    if np.isinf(f_statistic):
        p_value = 0.0
    else:
        p_value = float(ncf.sf(f_statistic, df1, df2, noncentrality))
        p_value = float(min(max(p_value, 0.0), 1.0))

    count_mapping = {label: int(count) for label, count in counts.items()}
    return QStatisticResult(
        q=q,
        p_value=p_value,
        f_statistic=f_statistic,
        noncentrality=noncentrality,
        df1=df1,
        df2=df2,
        n_observations=n,
        n_strata=n_strata,
        stratum_counts=count_mapping,
        within_ss=within_ss,
        between_ss=between_ss,
        total_ss=total_ss,
        dropped_count=prepared.dropped_count,
    )
