# Logic SVM - Support Vector Machine Baseline (Detailed Technical Specification)

This document presents the detailed architectural design, feature scaling, walk-forward training windows, risk management overlays, model interpretability framework, and execution model of the **Support Vector Machine (SVM) Baseline Bot**. There are two identical implementations that differ only by their data paths:
1. **Original Version (`svm_baseline.py`)**: Runs on the original daily market dataset (located in the `dataset/` directory) and outputs results to the `data-backtest/` directory, with summary results in `results/svm/`.
2. **Robust/Stress-Tested Version (`svm2.py`)**: Runs on the perturbed daily market dataset (located in the `dataset_robust/` directory) and outputs results to the `data-backtest2/` directory, with summary results in `results2/svm/`.

Both versions share the exact same trading logic, feature calculation, feature scaling, model parameters, and risk management framework.

---

## 1. Architecture Overview & System Role

The SVM Baseline Bot is a **supervised machine learning control model** designed to represent the **boundary-based classification approach**. By comparing Support Vector Machines (Boundary-based) against XGBoost (Tree-boosting) on identical data feeds, technical features, and risk overlays, we can isolate the impact of different learning paradigms (decision boundary margins vs. recursive feature space partitioning) on high-noise financial time series.

```
Baseline (Technical Rules)
  → RMDB (Rules + Risk Gates)                  ← Isolates impact of Risk Gates
    → SVM (RBF Kernel Boundary + Risk Gates)    ← Isolates Boundary vs Boosting (NEW)
      → XGBoost (ML Boosting + Risk Gates)      ← Isolates value of LLM Reasoning
        → LLM Agent (LLM Decisions + Risk Gates)
```

### Core Architecture:
1.  **Tabular Feature Input**: Receives 12 numeric features computed from historical price action and volume (identical to prompt inputs).
2.  **Feature Standardization**: Fits a z-score standardizer on training features and scales both training and testing datasets. Since SVM computes distances in geometric space, feature scaling is mandatory.
3.  **Walk-Forward SVM Classifier**: Fits a Support Vector Classifier (SVC) with a Radial Basis Function (RBF) kernel on pre-stress historical windows and predicts next-day price direction.
4.  **Risk Management overlay**: Applies the exact same 1% risk-per-trade position sizing, dynamic stop-loss, and ATR-based volatility gate as the RMDB, XGBoost, and LLM bots.
5.  **Transaction Fees & Slippage**: Incorporates a taker fee of **0.05%** per transaction, a bid-ask spread of **0.02%**, and execution price slippage models (S0, S1, S2).
6.  **Interpretability Engine**: Performs permutation importance analysis on out-of-sample data to identify which technical indicators drive model predictions.

---

## 2. Feature Engineering & Target Labelling

Features are calculated on the full chronological daily dataset from 2004 to 2023 to avoid cold-start problems (ensuring EMA50 and ATR100 are fully populated from day 1 of the test window).

### A. Technical Indicator Features
*   **Relative Strength Index (RSI-14)**:
    $$\text{RSI} = 100 - \frac{100}{1 + \text{RS}}, \quad \text{where } \text{RS} = \frac{\text{EMA}(\text{U}, 14)}{\text{EMA}(\text{D}, 14)}$$
*   **Moving Average Convergence Divergence (MACD)**:
    $$\text{MACD Line} = \text{EMA}(Close, 12) - \text{EMA}(Close, 26)$$
    $$\text{Signal Line} = \text{EMA}(\text{MACD Line}, 9)$$
    $$\text{Histogram} = \text{MACD Line} - \text{Signal Line}$$
*   **Exponential Moving Averages (EMA-20 & EMA-50)**:
    $$\text{EMA}_t = \alpha \times Close_t + (1 - \alpha) \times \text{EMA}_{t-1}, \quad \alpha = \frac{2}{N+1}$$
*   **Average True Range (ATR-14)**:
    $$\text{TR} = \max\left( \text{High}_t - \text{Low}_t, |\text{High}_t - Close_{t-1}|, |\text{Low}_t - Close_{t-1}| \right)$$
    $$\text{ATR}_t = \frac{\text{ATR}_{t-1} \times 13 + \text{TR}_t}{14}$$
*   **Volume Ratio**:
    $$\text{Volume Ratio} = \frac{\text{Volume}_t}{\frac{1}{20}\sum_{i=0}^{19} \text{Volume}_{t-i}}$$

### B. Price Context Features
*   **Price Returns (1-day, 5-day, 20-day)**:
    $$\text{close\_pct\_kd}_t = \frac{Close_t}{Close_{t-k}} - 1, \quad k \in \{1, 5, 20\}$$

### C. Volatility Gate Flag
*   **vol\_gate\_flag**: A binary variable indicating if the short-term ATR exceeds 2.0x the rolling mean ATR:
    $$\text{vol\_gate\_flag} = \begin{cases} 1 & \text{if } \text{ATR}_{14, t} > 2.0 \times \left( \frac{1}{20} \sum_{i=0}^{19} \text{ATR}_{14, t-i} \right) \\ 0 & \text{otherwise} \end{cases}$$

### D. Target Variable
*   **forward\_return\_sign**: The direction of price change for the next trading day:
    $$\text{forward\_return} = \frac{Close_{t+1}}{Close_t} - 1$$
    $$\text{forward\_return\_sign} = \begin{cases} 1 & \text{if } \text{forward\_return} > 0 \\ 0 & \text{otherwise} \end{cases}$$

---

## 3. Walk-Forward Training Schema

To prevent lookahead bias (data leakage), the SVM model is trained strictly on out-of-sample historical periods preceding the stress windows.

| Period Name | Training Window (In-Sample) | Stress Backtesting Window (Out-of-Sample) |
| :--- | :--- | :--- |
| **2008-2009** | Jan 1, 2005 - Dec 31, 2007 | Jan 1, 2008 - Dec 31, 2009 |
| **2020-2021** | Jan 1, 2017 - Dec 31, 2019 | Jan 1, 2020 - Dec 31, 2021 |
| **2022-2023** | Jan 1, 2019 - Dec 31, 2021 | Jan 1, 2022 - Dec 31, 2023 |
| **2024-2025** | Jan 1, 2021 - Dec 31, 2023 | Jan 1, 2024 - Dec 31, 2025 |

---

## 4. Feature Standardization & SVM Model Configuration

### A. Z-Score Standardization
SVM is highly sensitive to the scale of features since it constructs a decision boundary based on geometric distances. We standardize features by fitting a `StandardScaler` on the training set and applying it to both training and test features:
$$X_{\text{scaled}} = \frac{X - \mu_{\text{train}}}{\sigma_{\text{train}}}$$

### B. SVM Hyper-parameters
The Support Vector Classifier (SVC) is configured with an RBF kernel and class weighting to address imbalance:
*   `kernel`: `rbf` (Radial Basis Function, maps features to a high-dimensional space)
*   `C`: `1.0` (regularization parameter, controls margin softness and prevents overfitting)
*   `gamma`: `scale` (kernel coefficient, set dynamically based on number of features)
*   `class_weight`: $\{0: 1.0, 1: \frac{N_{\text{negative}}}{N_{\text{positive}}}\}$ (compensates for target imbalances)
*   `probability`: `True` (enables Platt scaling to generate probability output)
*   `random_state`: `42` (ensures deterministic output)

### C. Signal Threshold
To match the trading conservatism of other baselines, a long position is entered **only if** the model's Platt probability estimate exceeds $55\%$:
$$\text{Signal}_t = \begin{cases} 1 \text{ (Long)} & \text{if } P(\text{Price rises}) > 0.55 \\ 0 \text{ (Flat)} & \text{otherwise} \end{cases}$$

---

## 5. Risk-Managed Trading Rules

Once a signal is generated, it must satisfy the risk-management gates before execution:

*   **Entry Prevention (Volatility Gate)**: No trades are entered if `vol_gate_flag == 1`.
*   **Stop Loss (SL)**: Set at a fixed $2.0 \times \text{ATR}$ distance from entry price:
    $$\text{SL}_{\text{Long}} = \text{Entry Price} - 2.0 \times \text{ATR}_{14}$$
*   **Take Profit (TP)**: In-trade position management depends on the exit signal (i.e. model probability drops below $55\%$):
    $$\text{Exit Signal}_t = \begin{cases} \text{True} & \text{if } P(\text{Price rises}) \le 0.55 \\ \text{False} & \text{otherwise} \end{cases}$$
*   **Position Sizing (1% Risk Gate)**: The trade quantity is calculated to risk exactly 1% of current account equity:
    $$\text{Quantity} = \frac{\text{Equity} \times 0.01}{\text{Entry Price} - \text{SL Price}}$$
    $$\text{Leverage} = \frac{\text{Quantity} \times \text{Entry Price}}{\text{Margin Allocated}}$$
*   **Capital Constraint**: The position value cannot exceed 95% of total account equity.

---

## 6. Percentage-Based Slippage Robustness (S0, S1, S2)

During backtesting, execution prices are adjusted to account for slippage and spread based on the `BACKTEST_SLIPPAGE_MODE` environment variable:

*   **S0 (Dynamic ATR-based Slippage)**: Slippage is derived dynamically from market volatility.
    *   $\text{Slippage} = 0.1 \times \text{ATR}$
    *   $\text{Spread} = \text{Current Price} \times \text{Spread Percentage}$ (default 0.02%)
    *   $\text{Entry Price}_{\text{Long}} = \text{Current Price} + \text{Slippage} + 0.5 \times \text{Spread}$
    *   $\text{Exit Price}_{\text{Long}} = \text{Current Price} - \text{Slippage} - 0.5 \times \text{Spread}$
*   **S1 (Fixed 0.05% Slippage)**: Simulates standard market slippage.
    *   $\text{Slippage} = \text{Current Price} \times 0.0005$
    *   $\text{Entry Price}_{\text{Long}} = \text{Current Price} + \text{Slippage} + 0.5 \times \text{Spread}$
    *   $\text{Exit Price}_{\text{Long}} = \text{Current Price} - \text{Slippage} - 0.5 \times \text{Spread}$
*   **S2 (Fixed 0.10% Slippage)**: Simulates high-slippage market stress.
    *   $\text{Slippage} = \text{Current Price} \times 0.0010$
    *   $\text{Entry Price}_{\text{Long}} = \text{Current Price} + \text{Slippage} + 0.5 \times \text{Spread}$
    *   $\text{Exit Price}_{\text{Long}} = \text{Current Price} - \text{Slippage} - 0.5 \times \text{Spread}$
