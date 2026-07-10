# Blinded Perturbed-Series Diagnostics

This folder supports the manuscript's memory-leakage threat analysis for pretrained LLMs.
It is not a second leaderboard.

Generation logic:
1. Split each retained OHLCV-style series into contiguous 10-row blocks.
2. Shuffle blocks to reduce famous crisis trajectory recognition while preserving local continuity.
3. Inject small Gaussian noise into OHLC prices and recompute percentage change.
4. Re-index dates to a neutral synthetic business-day calendar beginning 2000-01-03.
5. Replace instrument/window cues with synthetic labels such as `SYNTH_A_W1_BLINDED.csv`.

The production experiments retain real dates and asset identities because operational systems observe them.
These blinded files are provided so reviewers can inspect or rerun prompt diagnostics with reduced
historical-name and crisis-year salience.
