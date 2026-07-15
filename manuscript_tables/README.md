# Manuscript verification tables for ICEBA 2026 V5

All performance and diagnostic tables are generated from retained artifact files. The main manuscript uses `total_return_pct` from `data-backtest/*/backtest_results.json`; it does not use hand-entered return values.

Files:
- `performance_detail_from_backtest_json.csv`: case-level values for every system/scenario.
- `performance_summary_total_return_from_json.csv`: main aggregate performance table.
- `trade_diagnostics_from_json.csv`: trade count and win-rate diagnostics.
- `paired_bootstrap_return_delta_vs_llm.csv`: paired bootstrap diagnostics against the LLM.
- `casewise_dominance_vs_llm.csv`: case-wise win counts for SVM/XGBoost versus the LLM.
- `reference_baselines_summary.csv`: cash and buy-and-hold references.
- `agentic_minimality_gate_summary.csv`: deployment-governance ledger used in the paper.

Raw provider metadata logs are omitted for anonymity. Prompt templates, parsed decisions, trade histories, portfolio states, and JSON summaries are retained.
