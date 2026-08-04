"""Apply the final IDSA type-annotation repair; removed after execution."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "src/pygeohet/models/idsa.py"
text = path.read_text(encoding="utf-8")

first_old = "            current = (ranked[0],)\n"
first_new = "            current: tuple[str, ...] = (ranked[0],)\n"
if first_old in text:
    text = text.replace(first_old, first_new, 1)
elif first_new not in text:
    raise SystemExit("initial greedy current assignment was not found")

second_old = "            current: tuple[str, ...] = best.factors\n"
second_new = "            current = best.factors\n"
if second_old in text:
    text = text.replace(second_old, second_new, 1)
elif second_new not in text:
    raise SystemExit("post-pair greedy current assignment was not found")

path.write_text(text, encoding="utf-8")
(ROOT / ".idsa-mypy-fix-complete").write_text(
    "Delete after restoring the final CI workflow.\n",
    encoding="utf-8",
)
Path(__file__).unlink()
