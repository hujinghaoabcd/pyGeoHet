"""Repair Stage 5B tuple labels, typing and version; removed after execution."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spade_path = ROOT / "src/pygeohet/models/spade_core.py"
spade = spade_path.read_text(encoding="utf-8")
old = '''    labels_array = np.asarray(strata, dtype=object)
    labels = tuple(pd.unique(pd.Series(labels_array, dtype=object)))
    if len(labels) < 2:
        raise InvalidDataError("at least two spatial strata are required")

    counts: list[int] = []
    for label in labels:
        counts.append(int(np.count_nonzero(labels_array == label)))
'''
new = '''    labels_array = np.asarray(strata, dtype=object).reshape(-1)
    label_codes, unique_labels = pd.factorize(
        pd.Series(labels_array, dtype=object),
        sort=False,
    )
    if bool((label_codes < 0).any()):
        raise InvalidDataError("spatial strata must not contain missing labels")
    labels = tuple(unique_labels.tolist())
    if len(labels) < 2:
        raise InvalidDataError("at least two spatial strata are required")

    counts = [
        int(np.count_nonzero(label_codes == code)) for code in range(len(labels))
    ]
'''
if old not in spade:
    raise SystemExit("SPADE label block was not found")
spade = spade.replace(old, new, 1)
old_loop = '''    for label, count in zip(labels, counts, strict=True):
        indices = np.flatnonzero(labels_array == label)
'''
new_loop = '''    for code, (label, count) in enumerate(zip(labels, counts, strict=True)):
        indices = np.flatnonzero(label_codes == code)
'''
if old_loop not in spade:
    raise SystemExit("SPADE contribution loop was not found")
spade = spade.replace(old_loop, new_loop, 1)
spade_path.write_text(spade, encoding="utf-8")

idsa_path = ROOT / "src/pygeohet/models/idsa.py"
idsa = idsa_path.read_text(encoding="utf-8")
idsa = idsa.replace(
    "from typing import Any, Literal\n",
    "from typing import Any, Literal, cast\n",
    1,
)
idsa = idsa.replace(
    "    return operation, tie_policy\n",
    "    return cast(FuzzyOperation, operation), cast(FuzzyTiePolicy, tie_policy)\n",
    1,
)
idsa = idsa.replace(
    "        factor_order = tuple(numeric.columns)\n",
    "        factor_order: tuple[str, ...] = tuple(str(name) for name in numeric.columns)\n",
    1,
)
old_current = '''            best = _select_best_combination(
                pair_attempts,
                factor_rank,
                self.pid_tolerance,
            )
            current = best.factors
            current_value = best.result.value if best.result is not None else -np.inf
'''
new_current = '''            best = _select_best_combination(
                pair_attempts,
                factor_rank,
                self.pid_tolerance,
            )
            assert best.result is not None
            current: tuple[str, ...] = best.factors
            current_value = best.result.value
'''
if old_current not in idsa:
    raise SystemExit("IDSA initial greedy block was not found")
idsa = idsa.replace(old_current, new_current, 1)
old_stage = '''                best = stage_best
                current = best.factors
                current_value = best.result.value
'''
new_stage = '''                best = stage_best
                current = stage_best.factors
                current_value = stage_best.result.value
'''
if old_stage not in idsa:
    raise SystemExit("IDSA iterative greedy block was not found")
idsa = idsa.replace(old_stage, new_stage, 1)
idsa_path.write_text(idsa, encoding="utf-8")

version_path = ROOT / "src/pygeohet/_version.py"
version_path.write_text('__version__ = "0.0.8"\n', encoding="utf-8")

test_path = ROOT / "tests/test_spade.py"
tests = test_path.read_text(encoding="utf-8")
marker = "def test_psd_matches_direct_formula_and_row_permutation() -> None:\n"
regression = '''def test_psd_accepts_hashable_tuple_strata() -> None:
    y = np.asarray([0.0, 1.0, 4.0, 5.0, 9.0, 10.0])
    strata = np.empty(len(y), dtype=object)
    strata[:] = [
        ("a", 1),
        ("a", 1),
        ("b", 1),
        ("b", 1),
        ("c", 2),
        ("c", 2),
    ]
    result = power_spatial_determinant(y, strata, _complete_weights(len(y)))

    assert result.strata_frame()["count"].tolist() == [2, 2, 2]
    assert result.value > 0.0


'''
if regression not in tests:
    if marker not in tests:
        raise SystemExit("SPADE test insertion point was not found")
    tests = tests.replace(marker, regression + marker, 1)
test_path.write_text(tests, encoding="utf-8")

(ROOT / ".stage5b-ci-fix-complete").write_text(
    "Delete after restoring the final CI workflow.\n",
    encoding="utf-8",
)
Path(__file__).unlink()
