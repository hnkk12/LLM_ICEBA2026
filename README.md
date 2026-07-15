# ICEBA 2026 Anonymous Artifact Replication Package

This repository contains the replication code and dataset package for the paper submitted to the **International Conference on Internet and Business Applications (ICEBA 2026)**.

The project evaluates and compares different financial trading systems across historical stress periods (2008-2009, 2020-2021, 2022-2023, 2024-2025):
1. **Rule-Based Baseline**: Technical-indicator rules (EMA, RSI, Bollinger Bands).
2. **RMDB**: Volatility-regulated rule-based baseline.
3. **SVM (Original & Robust)**: Support Vector Machine walk-forward classifier.
4. **XGBoost (Original & Robust)**: XGBoost walk-forward classifier with SHAP explainability.
5. **LLM Agent (Original & Robust)**: Reasoning trading agent (using meta-llama/llama-3.3-70b-instruct).

---

## 📂 Repository Structure

- `dataset/`: Historical daily price datasets for Apple (AAPL) and Gold (GOLD).
- `dataset_robust/`: Block-scrambled and noise-perturbed synthetic datasets (for robustness stress-testing).
- `dataset_blinded/`: Obfuscated synthetic datasets (asset/date-blinded) used to audit LLM memory leakage/data contamination.
- `data-backtest/`: Raw and compiled backtest outputs for the Standard/Original experiments.
- `data-backtest2/`: Raw and compiled backtest outputs for the Robust experiments.
- `manuscript_tables/`: Compiled `.csv` tables mapped directly to the tables presented in the scientific manuscript.
- `results/` & `results2/`: Explainable AI (XAI) diagnostics, including SHAP beeswarm plots, feature gain importance charts, and aggregated ML performance csvs.
- `prompts/`: Core system prompt instructions defining the LLM trading rules and risk gates.
- `scripts/`: Python orchestration scripts (stats verification, diagnostics, backtest runners).
- `Figures/`: Contains the 25 generated academic and statistical charts used in the scientific manuscript.
- `paper/`: Contains the Word document templates and compiled paper outputs (both blinded and unblinded).
- `generate_figures.py`: Generates the 25 academic figures from backtest and results databases.
- `write_academic_paper.py`: Compiles the final scientific manuscript docm files using python-docx and local statistics databases.
- `ANONYMITY_AND_QC_REPORT_V12.txt`: Anonymity audit log confirming double-blind compliance (removal of author names, emails, local paths).
- `ARTIFACT_MANIFEST_V12.csv`: Checksum verification manifest generated automatically to ensure dataset and code integrity.


---

## 🛠️ Installation & Setup

1. **Clone or Extract the Package**:
   Ensure you are in the project root directory:
   ```bash
   cd LLM_ICEBA2026
   ```

2. **Install Dependencies**:
   Install the required Python packages using the package list:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the safe reviewer template to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your OpenRouter API Key (e.g. `OPENROUTER_API_KEY=sk-or-v1-...`) to run fresh LLM backtests.

---

## 🚀 Replicating Experimental Results

All comparative tables and figures can be regenerated using the following steps:

### 1. Run Rule-Based Baselines (Baseline & RMDB)
To re-run the rule-based backtests for all periods and slippage scenarios:
```bash
python scripts/run_baseline.py
python scripts/run_rmdb.py
```
*(Note: Set `BACKTEST_DISABLE_TELEGRAM=true` inside `.env` to bypass Telegram API rate limiting and complete backtesting stubs in seconds).*

### 2. Run Machine Learning Models (SVM & XGBoost)
To train, walk-forward validate, and backtest the ML baselines:
* **Original Models**:
  ```bash
  python svm_baseline.py
  python xgboost_baseline.py
  ```
* **Robust Models**:
  ```bash
  python svm2.py
  python xgboost2.py
  ```
Running these ML scripts will automatically compute features, execute walk-forward validation over all stress periods, generate the SHAP beeswarm plot summaries, and output to `results/` and `results2/`.

### 3. Run LLM Agent Backtests
Configure the target asset, period, and slippage scenario in `.env` (e.g., `BACKTEST_SYMBOLS=AAPL`, `BACKTEST_START=2024-01-01`, `BACKTEST_END=2025-12-31`, `BACKTEST_SLIPPAGE_MODE=S0`), then execute:
* **Original LLM Agent**:
  ```bash
  python backtest.py
  ```
* **Robust LLM Agent**:
  ```bash
  python backtest2.py
  ```

### 4. Compile Manuscript Tables & Statistics
After running the backtests, compile the unified Table II, Table III, and Table V metrics:
```bash
python scripts/compile_manuscript_tables.py
```
To run the statistical significance boot-strap delta testing (validating return improvements):
```bash
python scripts/run_stats_significance.py
```

### 5. Generate Academic Figures & Compile Paper
To regenerate the 25 academic statistical charts from the compiled manuscript metrics:
```bash
python generate_figures.py
```
To compile the final Microsoft Word manuscript files (both `paper.docm` and `paper_blind.docm`) using python-docx:
```bash
python write_academic_paper.py
```

### 6. Generate Checksum Manifest
To regenerate the SHA-256 manifest to log any changes:
```bash
python scripts/generate_manifest.py
```


---

## 🔒 Anonymity & Replication Compliance

- **No Personal Identifiers**: All text files, source codes, and outputs have been audited. No author names, institutional names, personal email addresses, or specific local directory paths are retained.
- **Double-Blind Review**: Reviewers can execute prompt testing on `dataset_blinded/` to inspect LLM behaviors under zero historical-name and crisis-year cues.
