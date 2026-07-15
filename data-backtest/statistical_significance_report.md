# Statistical Significance Report
Generated on: 2026-07-15T17:14:01.726426+00:00

This report evaluates the statistical significance of differences in performance between the LLM Trading Decision Agent and the rule-based baseline bot.

## Performance Comparison Summary

| Metric | LLM Trading Agent | Rule-Based Baseline | Difference |
| :--- | :---: | :---: | :---: |
| **Model / Agent** | meta-llama/llama-3.3-70b-instruct | Rule-Based Baseline | - |
| **Total Net Profit** | $89.80 | $-100.52 | $+190.31 |
| **Return %** | +8.98% | -10.05% | +19.03% |
| **Max Drawdown** | 5.81% | 10.59% | -4.79% |
| **Sharpe Ratio** | 0.67 | -1.08 | +1.75 |
| **Sortino Ratio** | 0.95 | -1.47 | +2.42 |
| **Profit Factor** | 1.19 | 0.88 | +0.30 |
| **Recovery Factor** | 1.55 | -0.95 | +2.49 |
| **VaR (95% Daily)** | 0.61% | 0.54% | +0.07% |
| **CVaR (95% Daily)** | 0.97% | 0.84% | +0.13% |
| **Total Trades** | 141 | 78 | +63 |
| **Win Rate** | 42.6% | 41.0% | +1.5% |

## Hypothesis Testing

### 1. Student's t-test (Welch's Formulation)
* **Null Hypothesis ($H_0$)**: There is no difference in the mean daily return between the LLM agent and the baseline.
* **Alternative Hypothesis ($H_a$)**: There is a significant difference in the mean daily return.
* **t-statistic**: `1.5473`
* **p-value**: `1.2200e-01`
* **Result**: Fail to reject $H_0$ (Not Statistically Significant) at 5% level.

### 2. Mann-Whitney U Test (Non-Parametric)
* **Null Hypothesis ($H_0$)**: The distributions of daily returns for both agents are identical.
* **Alternative Hypothesis ($H_a$)**: The distributions are shifted (one agent stochastically dominates the other).
* **U-statistic**: `270758.00`
* **p-value**: `4.4975e-01`
* **Result**: Fail to reject $H_0$ (Not Statistically Significant) at 5% level.

## Bootstrap Confidence Intervals (95% Confidence)
We generated 1,000 bootstrap resamples with replacement to compute the distribution of differences in risk-adjusted performance metrics.

### Sharpe Ratio Difference (LLM - Baseline)
* **Mean Sharpe Difference**: `+1.2945`
* **95% Bootstrap CI**: `[-0.4646, 2.8720]`
* **Significance**: Not Statistically Significant (CI contains 0.0)

### Sortino Ratio Difference (LLM - Baseline)
* **Mean Sortino Difference**: `+1.8030`
* **95% Bootstrap CI**: `[-0.6663, 4.1037]`
* **Significance**: Not Statistically Significant (CI contains 0.0)

## Risk & Drawdown Distribution Analysis

| Drawdown Statistic | LLM Trading Agent | Rule-Based Baseline |
| :--- | :---: | :---: |
| **Maximum Drawdown** | 5.81% | 10.59% |
| **Mean Intrabar Drawdown** | 2.37% | 5.16% |
| **Drawdown Volatility (StdDev)** | 1.46% | 2.79% |

## Conclusion & Research Interpretation
The LLM trading decision agent achieved a final return of **+8.98%** compared to **-10.05%** for the baseline.
Based on the t-test p-value of `1.22e-01`, the performance difference is NOT statistically significant.
Furthermore, the bootstrap 95% confidence interval for Sharpe difference is `[-0.4646, 2.8720]`, confirming that the difference in risk-adjusted performance is NOT statistically robust.

This research suggests that LLM cognitive capabilities under financial crisis regimes do not yield a statistically significant advantage over simple momentum rules when considering transaction friction (spread/slippage).