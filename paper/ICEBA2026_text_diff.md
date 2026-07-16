# Editorial diff for `ICEBA2026_submission_revised.pdf`

The original PDF remains unchanged. The revised PDF is generated as a separate file for review.

## 1. Insertion after Introduction

### Before

```text
[end of Introduction]

2. Related Work
```

### After

```text
[end of Introduction]

Theoretical Framing

Leakage-Aware Validity Criteria (LAVC). This study frames empirical validity as a conjunction of four criteria rather than as a single performance statistic. C1—Temporal separation: every fitted parameter and decision must be conditioned on information available no later than the forecast date; this criterion is operationalized by the chronological data construction and holdout windows in Section 3.1. C2—Cost-realism: reported economic value must survive explicitly stated execution frictions, with return and risk metrics recomputed under alternative slippage assumptions in Section 3.2. C3—Contamination audit: conclusions should be stress-tested after recognizable dates and asset identifiers are removed and observations are shuffled or perturbed; the auxiliary procedure is documented in Section 3.4. C4—Uncertainty reporting: aggregate rankings must be accompanied by sampling-based intervals and casewise dominance counts so that point estimates are not mistaken for simultaneous evidence of superiority; Section 3.3 specifies this reporting layer. Under LAVC, a model is considered empirically credible only to the extent that all four criteria are transparently addressed. The framework consequently separates evidence of predictive or economic association from stronger claims of deployability, robustness, or generalization beyond the evaluated assets and periods.

2. Related Work
```

## 2. Discussion governance insertion

### Before

```text
[existing discussion paragraphs]

The shuffled/noisy audit strengthens governance claims only in a limited sense.
```

### After

```text
[existing discussion paragraphs]

The governance implications are consistent with the risk-management orientation of the NIST AI Risk Management Framework (AI RMF): validity evidence, documented limitations, and traceable human oversight should accompany any transition from research backtest to operational use. They also align with the management-system perspective of ISO/IEC 42001, under which model documentation, accountability, monitoring, and controlled change are treated as lifecycle requirements. These frameworks do not validate the reported returns; rather, they provide governance lenses through which the LAVC criteria can be operationalized.

The shuffled/noisy audit strengthens governance claims only in a limited sense.
```

No numerical result, table, figure, reference entry, or primary/robust dataset definition was changed.
