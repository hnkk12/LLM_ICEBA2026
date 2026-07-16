"""Read-only integrity checks for the ICEBA 2026 artifact package.

This validator deliberately treats ``data-backtest`` as the primary benchmark
and ``data-backtest2`` as an auxiliary synthetic anti-leakage audit. It does
not require a full robust LLM factorial because robust LLM inference is
intentionally restricted to S0 to control provider cost.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PRIMARY = {
    "meta-llama/llama-3.3-70b-instruct": 24,
    "Rule-Based Baseline": 24,
    "Risk-Managed Deterministic Baseline": 24,
    "SVM Baseline": 24,
    "XGBoost Baseline": 24,
}
EXPECTED_ROBUST = {
    "meta-llama/llama-3.3-70b-instruct": 8,  # S0 only by design
    "Rule-Based Baseline": 24,
    "Risk-Managed Deterministic Baseline": 24,
    "SVM Baseline": 24,
    "XGBoost Baseline": 24,
}


def check_runs(directory: Path, expected: dict[str, int]) -> list[str]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    runs = [p for p in directory.iterdir() if p.is_dir() and p.name != "cache"]
    for run_dir in runs:
        result_path = run_dir / "backtest_results.json"
        settings_path = run_dir / "settings.json"
        if not result_path.exists():
            errors.append(f"{directory.name}/{run_dir.name}: missing backtest_results.json")
            continue
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            model = result.get("llm", {}).get("model", "")
            counts[model] += 1
            run_id = str(result.get("run_id", "")).lower()
            directory_id = run_dir.name.lower()
            # Historical LLM GOLD runs use GOLD_AI_* while the directory uses
            # GOLD_BACKTEST_*; both identify the same experiment.
            equivalent_id = run_id.replace("_ai_", "_backtest_")
            if equivalent_id != directory_id:
                errors.append(f"{run_dir}: run_id does not match directory")
            capital = result.get("capital", {})
            start = float(capital["start"])
            final = float(capital["final_equity"])
            reported = float(capital["total_return_pct"])
            calculated = (final / start - 1.0) * 100.0
            if abs(calculated - reported) > 0.001:
                errors.append(f"{run_dir}: return arithmetic mismatch")
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{result_path}: invalid JSON/result ({exc})")
            continue

        model = result.get("llm", {}).get("model", "")
        # SVM/XGBoost export their settings in the JSON metadata rather than
        # a separate settings.json file.
        if not settings_path.exists() and model in {
            "Rule-Based Baseline",
            "Risk-Managed Deterministic Baseline",
            "meta-llama/llama-3.3-70b-instruct",
        }:
            errors.append(f"{run_dir}: missing settings.json")
            continue
        if not settings_path.exists():
            continue
        try:
            mode = json.loads(settings_path.read_text(encoding="utf-8")).get("slippage_mode")
            suffix = run_dir.name.upper().split("_")[-1]
            if suffix in {"S0", "S1", "S2"} and mode != suffix:
                errors.append(f"{run_dir}: settings slippage {mode!r} != directory {suffix}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{settings_path}: invalid settings ({exc})")

    if counts != Counter(expected):
        errors.append(
            f"{directory.name}: model counts {dict(counts)} != expected {expected}"
        )
    return errors


def check_manifest() -> list[str]:
    path = ROOT / "ARTIFACT_MANIFEST_V12.csv"
    errors: list[str] = []
    if not path.exists():
        return ["ARTIFACT_MANIFEST_V12.csv is missing"]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rel = row.get("relative_path", "")
            if Path(rel).name in {
                "ai_messages.csv",
                "ai_decisions.csv",
                "trade_history.csv",
                "portfolio_state.csv",
                "portfolio_state.json",
                "backtest_results.json",
            }:
                errors.append(f"manifest contains runtime artifact: {rel}")
    return errors


def main() -> int:
    errors = []
    errors.extend(check_runs(ROOT / "data-backtest", EXPECTED_PRIMARY))
    errors.extend(check_runs(ROOT / "data-backtest2", EXPECTED_ROBUST))
    errors.extend(check_manifest())
    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDATION PASSED")
    print("- primary benchmark: 120 runs")
    print("- robust audit: 104 runs (LLM S0 only by design)")
    print("- run IDs, return arithmetic, scenario labels, and manifest exclusions: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
