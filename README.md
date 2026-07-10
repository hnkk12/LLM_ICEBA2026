# PRICAI 2026 Anonymous Artifact Package V12

This package supports a double-anonymous submission on agentic minimality in structured financial decision systems. It is designed for review-time audit, not for live trading or financial advice.

## What is included

- `dataset/`: retained daily OHLCV-style production series.
- `dataset_robust/`: block-shuffled and noise-perturbed diagnostic series.
- `dataset_blinded/`: label/date-blinded perturbed series for LLM memory-leakage inspection.
- `data-backtest/` and `data-backtest2/`: parsed decisions, portfolio states, trade histories, and retained JSON summaries.
- `manuscript_tables/`: tables regenerated from retained backtest outputs.
- `prompts/`: fixed prompt templates and structured-action instructions used for the LLM signal engine.
- `scripts/`: analysis and verification scripts.
- `ARTIFACT_MANIFEST_V12.csv`: file-level checksum manifest.
- `ANONYMITY_AND_QC_REPORT_V12.txt`: zero-flag anonymity and reproducibility scan.

## Deliberate omissions

Raw provider request-response metadata logs are not included because they can contain platform-specific identifiers, cost metadata, request headers, or IDs. The package retains prompt templates, parsed decisions, trade histories, JSON summaries, and checksum manifests so that the numerical claims in the paper remain auditable without exposing provider-level metadata. Fresh hosted-LLM calls require reviewer-provided credentials and endpoint configuration; the manuscript results can be checked from retained outputs without re-calling the provider.

## Reproducibility notes

The manuscript tables are intended to be checked against the retained JSON summaries in `data-backtest/` and `data-backtest2/`. The submission frames the study as a stress-test protocol and governance evaluation, not as an investment recommendation.


## V12 leakage-diagnostic clarification
The manuscript explicitly treats famous crisis windows as a validity threat for pretrained LLMs. The production runs retain real dates and asset identities because a real deployment would observe them. For review-time leakage inspection, `scripts/generate_blinded_diagnostics.py` creates `dataset_blinded/`, where series are block-shuffled, noise-perturbed, re-indexed to neutral dates, and renamed with synthetic labels. These files are diagnostic only and are not used as a second performance leaderboard.

## V12 final polish
Figure-label literals and bibliography/citation alignment were checked in the source package. The final paper uses the same retained numerical outputs as this artifact; only final presentation polish changed.
