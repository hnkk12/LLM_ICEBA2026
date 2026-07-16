# Statistical Significance Report
Generated on: 2026-07-16T15:48:40.544757+00:00

This report evaluates the statistical significance of differences in performance between the LLM Trading Decision Agent and the rule-based baseline bot.

## Performance Comparison Summary

| Metric | LLM Trading Agent | Rule-Based Baseline | Difference |
| :--- | :---: | :---: | :---: |
| **Model / Agent** | meta-llama/llama-3.3-70b-instruct | Rule-Based Baseline | - |
| **Total Net Profit** | $89.80 | $41.01 | $+48.78 |
| **Return %** | +8.98% | +4.10% | +4.88% |
| **Max Drawdown** | 5.81% | 5.18% | 0.62% |
| **Sharpe Ratio** | 0.67 | 0.43 | +0.23 |
| **Sortino Ratio** | 0.95 | 0.65 | +0.30 |
| **Profit Factor** | 1.19 | 0.88 | +0.30 |
| **Recovery Factor** | 1.55 | 0.79 | +0.75 |
| **VaR (95% Daily)** | 0.61% | 0.35% | +0.26% |
| **CVaR (95% Daily)** | 0.97% | 0.80% | +0.17% |
| **Total Trades** | 141 | 197 | -56 |
| **Win Rate** | 42.6% | 39.6% | +3.0% |

## Hypothesis Testing

### 1. Student's t-test (Welch's Formulation)
* **Null Hypothesis ($H_0$)**: There is no difference in the mean daily return between the LLM agent and the baseline.
* **Alternative Hypothesis ($H_a$)**: There is a significant difference in the mean daily return.
* **t-statistic**: `0.3792`
* **p-value**: `7.0457e-01`
* **Result**: Fail to reject $H_0$ (Not Statistically Significant) at 5% level.

### 2. Mann-Whitney U Test (Non-Parametric)
* **Null Hypothesis ($H_0$)**: The distributions of daily returns for both agents are identical.
* **Alternative Hypothesis ($H_a$)**: The distributions are shifted (one agent stochastically dominates the other).
* **U-statistic**: `260052.00`
* **p-value**: `4.7988e-01`
* **Result**: Fail to reject $H_0$ (Not Statistically Significant) at 5% level.

## Bootstrap Confidence Intervals (95% Confidence)
We generated 1,000 bootstrap resamples with replacement to compute the distribution of differences in risk-adjusted performance metrics.

### Sharpe Ratio Difference (LLM - Baseline)
* **Mean Sharpe Difference**: `+0.2182`
* **95% Bootstrap CI**: `[-1.3827, 1.7908]`
* **Significance**: Not Statistically Significant (CI contains 0.0)

### Sortino Ratio Difference (LLM - Baseline)
* **Mean Sortino Difference**: `+0.2695`
* **95% Bootstrap CI**: `[-2.1726, 2.6935]`
* **Significance**: Not Statistically Significant (CI contains 0.0)

## Risk & Drawdown Distribution Analysis

| Drawdown Statistic | LLM Trading Agent | Rule-Based Baseline |
| :--- | :---: | :---: |
| **Maximum Drawdown** | 5.81% | 5.18% |
| **Mean Intrabar Drawdown** | 2.37% | 2.14% |
| **Drawdown Volatility (StdDev)** | 1.46% | 1.55% |

## Conclusion & Research Interpretation
The LLM trading decision agent achieved a final return of **+8.98%** compared to **+4.10%** for the baseline.
Based on the t-test p-value of `7.05e-01`, the performance difference is NOT statistically significant.
Furthermore, the bootstrap 95% confidence interval for Sharpe difference is `[-1.3827, 1.7908]`, confirming that the difference in risk-adjusted performance is NOT statistically robust.

This research suggests that LLM cognitive capabilities under financial crisis regimes do not yield a statistically significant advantage over simple momentum rules when considering transaction friction (spread/slippage).