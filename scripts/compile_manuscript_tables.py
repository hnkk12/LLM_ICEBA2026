"""
Compile Manuscript Verification Tables from JSON Backtest Outputs
Replaces RF with SVM in all comparison tables.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data-backtest"
OUTPUT_DIR = PROJECT_ROOT / "manuscript_tables"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compile_tables():
    results = []
    
    # Scan all directories in data-backtest
    for run_dir in DATA_DIR.iterdir():
        if not run_dir.is_dir() or run_dir.name == "cache":
            continue
            
        results_file = run_dir / "backtest_results.json"
        if not results_file.exists():
            continue
            
        try:
            with open(results_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            run_id = data["run_id"]
            # Parse system, asset, period, scenario from run_id: e.g., AAPL_SVM_2008_2009_S0 or GOLD_BACKTEST_2020_2021_S1
            parts = run_id.split("_")
            if len(parts) < 5:
                continue
                
            asset = parts[0].upper()
            sys_raw = parts[1].upper()
            period = f"{parts[2]}-{parts[3]}"
            scenario = parts[4]
            
            # Map system raw names to paper names
            sys_map = {
                "BACKTEST": "LLM",
                "AI": "LLM",
                "BASELINE": "Baseline",
                "RMDB": "RMDB",
                "XGBOOST": "XGBoost",
                "SVM": "SVM"
            }
            system = sys_map.get(sys_raw, sys_raw)
            
            capital = data["capital"]
            trading = data["trading"]
            
            results.append({
                "run_id": run_id,
                "case": f"{asset}_{period}",
                "asset": asset,
                "period": period,
                "system": system,
                "scenario": scenario,
                "total_return_pct": capital["total_return_pct"],
                "max_drawdown_pct": capital["max_drawdown_pct"],
                "sharpe_ratio": capital["sharpe_ratio"],
                "sortino_ratio": capital["sortino_ratio"],
                "total_trades": trading["total_trades"],
                "win_rate_pct": trading["win_rate_pct"]
            })
        except Exception as e:
            print(f"Error parsing {results_file}: {e}")
            
    df = pd.DataFrame(results)
    if df.empty:
        print("No backtest results found.")
        return
        
    # Sort for consistency
    df.sort_values(by=["system", "scenario", "asset", "period"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # 1. Save performance detail CSV
    df.to_csv(OUTPUT_DIR / "performance_detail_from_backtest_json.csv", index=False)
    print(f"Saved performance detail -> {OUTPUT_DIR / 'performance_detail_from_backtest_json.csv'}")
    
    # 2. Save performance summary CSV
    summary_df = df.groupby(["system", "scenario"])[["total_return_pct", "max_drawdown_pct", "sharpe_ratio", "sortino_ratio"]].mean().reset_index()
    # Sort by scenario then system order (Baseline, RMDB, SVM, XGBoost, LLM)
    sys_order = {"Baseline": 0, "RMDB": 1, "SVM": 2, "XGBoost": 3, "LLM": 4}
    summary_df["sys_idx"] = summary_df["system"].map(sys_order)
    summary_df.sort_values(by=["scenario", "sys_idx"], inplace=True)
    summary_df.drop(columns=["sys_idx"], inplace=True)
    summary_df.to_csv(OUTPUT_DIR / "performance_summary_total_return_from_json.csv", index=False)
    print(f"Saved performance summary -> {OUTPUT_DIR / 'performance_summary_total_return_from_json.csv'}")
    
    # 3. Save trade diagnostics CSV
    diag_df = df.groupby(["system", "scenario"])[["total_trades", "win_rate_pct"]].mean().reset_index()
    diag_df.rename(columns={"total_trades": "trades_per_run"}, inplace=True)
    diag_df["sys_idx"] = diag_df["system"].map(sys_order)
    diag_df.sort_values(by=["scenario", "sys_idx"], inplace=True)
    diag_df.drop(columns=["sys_idx"], inplace=True)
    diag_df.to_csv(OUTPUT_DIR / "trade_diagnostics_from_json.csv", index=False)
    print(f"Saved trade diagnostics -> {OUTPUT_DIR / 'trade_diagnostics_from_json.csv'}")
    
    # 4. Save paired bootstrap returns and casewise dominance vs LLM
    llm_df = df[df["system"] == "LLM"].copy()
    
    bootstrap_rows = []
    dominance_rows = []
    
    np.random.seed(42)
    
    for sys_name in ["SVM", "XGBoost"]:
        sys_df = df[df["system"] == sys_name].copy()
        
        for scen in ["S0", "S1", "S2"]:
            sys_scen = sys_df[sys_df["scenario"] == scen]
            llm_scen = llm_df[llm_df["scenario"] == scen]
            
            # Merge on case
            merged = pd.merge(sys_scen, llm_scen, on="case", suffixes=("_sys", "_llm"))
            if len(merged) == 0:
                continue
                
            # Delta returns
            deltas = merged["total_return_pct_sys"] - merged["total_return_pct_llm"]
            mean_delta = deltas.mean()
            
            # Bootstrap CIs
            boot_means = []
            for _ in range(1000):
                boot_sample = np.random.choice(deltas, size=len(deltas), replace=True)
                boot_means.append(boot_sample.mean())
            ci_low = np.percentile(boot_means, 2.5)
            ci_high = np.percentile(boot_means, 97.5)
            
            bootstrap_rows.append({
                "system_vs_llm": sys_name,
                "scenario": scen,
                "mean_delta_total_return_pct": mean_delta,
                "ci2_5_pct": ci_low,
                "ci97_5_pct": ci_high,
                "n_cases": len(merged)
            })
            
            # Dominance
            ret_wins = sum(merged["total_return_pct_sys"] > merged["total_return_pct_llm"])
            mdd_wins = sum(merged["max_drawdown_pct_sys"] < merged["max_drawdown_pct_llm"])
            sharpe_wins = sum(merged["sharpe_ratio_sys"] > merged["sharpe_ratio_llm"])
            
            dominance_rows.append({
                "system_vs_llm": sys_name,
                "scenario": scen,
                "return_wins": ret_wins,
                "lower_mdd_wins": mdd_wins,
                "sharpe_wins": sharpe_wins,
                "n_cases": len(merged)
            })
            
    # Save bootstrap delta returns CSV
    boot_res_df = pd.DataFrame(bootstrap_rows)
    boot_res_df.to_csv(OUTPUT_DIR / "paired_bootstrap_return_delta_vs_llm.csv", index=False)
    print(f"Saved paired bootstrap -> {OUTPUT_DIR / 'paired_bootstrap_return_delta_vs_llm.csv'}")
    
    # Save casewise dominance CSV
    dom_res_df = pd.DataFrame(dominance_rows)
    dom_res_df.to_csv(OUTPUT_DIR / "casewise_dominance_vs_llm.csv", index=False)
    print(f"Saved casewise dominance -> {OUTPUT_DIR / 'casewise_dominance_vs_llm.csv'}")
    
    # Print out summary statistics for the user and for updating the minimality gate summary
    print("\n--- SVM Dominance Summary vs LLM ---")
    for row in dominance_rows:
        if row["system_vs_llm"] == "SVM":
            print(f"SVM vs LLM ({row['scenario']}): Return wins={row['return_wins']}/6, Lower MDD wins={row['lower_mdd_wins']}/6, Sharpe wins={row['sharpe_wins']}/6")

if __name__ == "__main__":
    compile_tables()
