"""
Master script to run all 2024-2025 backtests (except LLM)
Runs Rule-based Baseline, RMDB, SVM, XGBoost, and recompiles tables.
"""

import subprocess
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_rule_baselines():
    env_base = os.environ.copy()
    
    # 1. Run Rule-based Baseline & RMDB
    for system in ["baseline", "rmdb"]:
        for asset in ["AAPL", "GOLD"]:
            for scenario in ["S0", "S1", "S2"]:
                run_id = f"{asset}_{system.upper()}_2024_2025_{scenario}"
                
                # Setup environments
                env = env_base.copy()
                env["BACKTEST_START"] = "2024-01-01T00:00:00Z"
                env["BACKTEST_END"] = "2025-12-31T23:59:59Z"
                env["BACKTEST_INTERVAL"] = "1d"
                env["BACKTEST_SYMBOLS"] = asset
                env["BACKTEST_SLIPPAGE_MODE"] = scenario
                env["BACKTEST_RUN_ID"] = run_id
                
                script_path = PROJECT_ROOT / "scripts" / f"run_{system}.py"
                print(f"\n>>> Running {system.upper()} for {asset} under {scenario} ({run_id})...")
                
                subprocess.run(
                    [sys.executable, str(script_path)],
                    env=env,
                    cwd=str(PROJECT_ROOT),
                    check=True
                )

def run_ml_baselines():
    # Run SVM and XGBoost (original & robust)
    ml_scripts = [
        "svm_baseline.py",
        "svm2.py",
        "xgboost_baseline.py",
        "xgboost2.py"
    ]
    
    env = os.environ.copy()
    env["BACKTEST_PERIOD"] = "2024-2025"
    
    for script in ml_scripts:
        print(f"\n>>> Running machine learning script: {script}...")
        script_path = PROJECT_ROOT / script
        subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            cwd=str(PROJECT_ROOT),
            check=True
        )

def main():
    print("=== STARTING 2024-2025 BACKTESTS FOR ALL SYSTEMS (EXCEPT LLM) ===")
    
    # Set encoding environment variables to prevent UnicodeEncodeErrors on Windows
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    
    # 1. Run Baseline and RMDB
    run_rule_baselines()
    
    # 2. Run SVM and XGBoost
    run_ml_baselines()
    
    # 3. Compile manuscript tables
    print("\n>>> Compiling manuscript tables...")
    compile_script = PROJECT_ROOT / "scripts" / "compile_manuscript_tables.py"
    subprocess.run(
        [sys.executable, str(compile_script)],
        cwd=str(PROJECT_ROOT),
        check=True
    )
    
    # 4. Generate manifest
    print("\n>>> Re-generating checksum manifest...")
    manifest_script = PROJECT_ROOT / "scripts" / "generate_manifest.py"
    subprocess.run(
        [sys.executable, str(manifest_script)],
        cwd=str(PROJECT_ROOT),
        check=True
    )
    
    print("\n=== ALL 2024-2025 BACKTESTS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()
