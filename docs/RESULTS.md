# Week 1 Results Report: Review Triage and Model Choice

## Acceptance checks

| Week 1 check | Status | Evidence |
|---|---|---|
| Validated review triage on 20 held-out examples | Done | `data/holdout_20_labeled.csv`, [TEST_CASES.md](TEST_CASES.md), every output schema-validated |
| Model-choice comparison | Done | The table below and [`results/model_comparison.md`](../results/model_comparison.md) |

The targets here are proposed grading criteria, not claims about what accuracy is achievable.

## Setup

- **Task:** given a Portuguese Olist review and its star rating, return `category`, `severity`, `sentiment`, `needs_response` and `summary_en`.
- **Held-out set:** 20 real reviews, 4 per star rating, with human-reviewed gold labels (see [PROVENANCE.md](PROVENANCE.md)).
- **Models:** `qwen3.5:0.8b` and `qwen3.5:2b` through Ollama, run locally on an Apple M2 with 8 GB RAM, at temperature 0 with JSON-schema-constrained output.
- **Reproduce:** `python eval_triage.py`

## Results

| Metric | qwen3.5:0.8b | qwen3.5:2b |
|---|---|---|
| Schema-valid rate | 100% | 100% |
| Retry rate | 0% | 0% |
| Category accuracy | 65% (13/20) | 70% (14/20) |
| Category macro-F1 | 0.44 | 0.43 |
| Severity accuracy | 70% | 95% |
| Needs-response accuracy | 95% | 100% |
| Mean latency | 2.25 s | 5.02 s |
| p95 latency | 4.10 s | 9.67 s |
| Throughput | 21.3 tok/s | 10.2 tok/s |
| Model size | 1.24 GB | 3.12 GB |
| Cost | $0 | $0 |

## Analysis

- **Validation works.** Both models produced schema-valid output for 20 of 20 reviews without needing a retry. Constrained decoding together with Pydantic validation means downstream code never receives malformed triage output.
- **The 2B model is better at urgency.** It gets severity right 95% of the time, against 70% for the 0.8B model, and it never misses a review that needs a response. This matters most operationally, because severity and `needs_response` decide what a support agent sees first.
- **Category accuracy is similar and limited by hard cases.** Both models miss the same six reviews (rows 1, 2, 3, 5, 12 and 20 in [TEST_CASES.md](TEST_CASES.md)). Common patterns:
  - Undelivered orders are called `delivery_delay` or `not_received` instead of the gold label: row 1 should be `not_received`, and row 3, a missing item from a partly delivered order, should be `wrong_or_missing_item`.
  - Broken products are called `product_quality` or `delivery_delay` instead of `damaged_or_defective` (rows 5 and 12).
  - Two borderline rows (2 and 20) are missed by both models.

  The 0.8B model's only extra miss is row 17, a positive review about early delivery that it labelled `delivery_delay`.

  Macro-F1 (about 0.44) is much lower than accuracy because 9 of the 20 reviews are `positive_feedback`, which both models handle easily. The rarer complaint categories pull macro-F1 down.
- **Cost.** The 2B model is about 2.2× slower per review and uses about 2.5× the memory. It still fits on an 8 GB laptop.

## Recommendation

**Use `qwen3.5:2b` as the default triage model.** Its severity and needs-response accuracy is clearly higher, and those are the fields that drive which reviews get prioritized. About 5 s per review is acceptable for batch triage. Keep `qwen3.5:0.8b` as a fallback for memory-constrained or latency-sensitive use.

## Limitations

- **Small sample.** With 20 cases, one review changes accuracy by 5 points, so the difference in category accuracy (65% vs 70%) is not significant.
- **Label subjectivity.** Several reviews could reasonably fit two categories. The labels were AI-drafted and then human-reviewed, not independently double-labelled.
- **Latency varies between runs.** An earlier run measured 1.30 s and 2.40 s mean latency, against 2.25 s and 5.02 s here, with identical accuracy. Timing depends on machine load and on whether the model was already loaded. Accuracy metrics were stable across both runs.
- **Few-shot examples.** The prompt uses three invented, simulated examples. No held-out review appears in the prompt.

## Next steps (Week 2+)

- Add one more few-shot example each for `not_received` and `damaged_or_defective`, targeting the shared misses. Validate the change on a separate development set, not on this held-out set.
- Add a warm-up call before timing in `eval_triage.py` so latency is measured consistently.
