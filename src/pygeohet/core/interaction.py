"""Classification rules for classical two-factor interaction detection."""

from __future__ import annotations

from enum import StrEnum

import numpy as np


class InteractionType(StrEnum):
    """Five classical q-based interaction classes."""

    WEAKEN_NONLINEAR = "weaken_nonlinear"
    WEAKEN_UNIVARIATE = "weaken_univariate"
    INDEPENDENT = "independent"
    ENHANCE_BIVARIATE = "enhance_bivariate"
    ENHANCE_NONLINEAR = "enhance_nonlinear"


def classify_interaction(
    q_1: float,
    q_2: float,
    q_overlay: float,
    *,
    atol: float = 1e-12,
    rtol: float = 1e-9,
) -> InteractionType:
    """Classify q(X1∩X2) relative to q(X1), q(X2), and their sum."""

    values = np.asarray([q_1, q_2, q_overlay], dtype=float)
    if not bool(np.isfinite(values).all()):
        raise ValueError("interaction q values must be finite")
    if not bool(((values >= 0.0) & (values <= 1.0)).all()):
        raise ValueError("interaction q values must lie in [0, 1]")
    if atol < 0.0 or rtol < 0.0:
        raise ValueError("interaction tolerances must be nonnegative")

    lower = min(q_1, q_2)
    upper = max(q_1, q_2)
    additive = q_1 + q_2

    if q_overlay < lower and not np.isclose(q_overlay, lower, atol=atol, rtol=rtol):
        return InteractionType.WEAKEN_NONLINEAR
    if q_overlay < upper and not np.isclose(q_overlay, upper, atol=atol, rtol=rtol):
        return InteractionType.WEAKEN_UNIVARIATE
    if np.isclose(q_overlay, additive, atol=atol, rtol=rtol):
        return InteractionType.INDEPENDENT
    if q_overlay > additive and not np.isclose(
        q_overlay, additive, atol=atol, rtol=rtol
    ):
        return InteractionType.ENHANCE_NONLINEAR
    return InteractionType.ENHANCE_BIVARIATE
