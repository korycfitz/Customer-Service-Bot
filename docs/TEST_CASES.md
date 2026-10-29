# Test Cases and Expected Results (Week 1)

There are two kinds of tests:

1. **Unit tests** (`tests/test_triage_schema.py`): these check the code's validation and retry logic. They run offline and are deterministic.
2. **Held-out triage cases** (`data/holdout_20_labeled.csv`): these check the model's answers against human-reviewed expected labels.

## 1. Unit tests

Run with `pytest tests/`. Every test is expected to pass.

| Test | Input | Expected result |
|---|---|---|
| `test_valid_json_parses` | Well-formed triage JSON | Parsed into `TriageResult`; `category == "damaged_or_defective"` |
| `test_bad_category_rejected` | `category: "shipping"` (not in the allowed list) | `ValidationError` raised |
| `test_missing_field_rejected` | JSON with no `severity` | `ValidationError` raised |
| `test_non_json_rejected` | `"not json at all"` | `ValidationError` raised |
| `test_retries_once_then_succeeds` | Model returns invalid output, then valid JSON (mocked) | 2 model calls; result returned; `meta.retries == 1`; tokens summed across both calls |
| `test_gives_up_after_one_retry` | Model returns `{}` twice (mocked) | 2 model calls, then stops; result is `None`; `meta.valid == False`; error recorded |

Latest run: **6 passed**.

## 2. Command-line smoke test

```bash
python customer_service_app.py --text "O produto chegou quebrado" --score 1
```

Expected: valid JSON with `"simulated": true`, a `category` (expected `damaged_or_defective`), `severity: "high"`, `needs_response: true`, and an English `summary_en`.

## 3. Held-out triage cases (20)

The reviews are real Olist reviews, 4 per star rating (seed 42). The expected labels were drafted, then reviewed and approved by a human. ✅ means the model's category matched the expected category; ❌ shows what the model predicted instead. Each model's results for severity and `needs_response` are in `results/predictions_<model>.csv` (that file is generated locally and not committed).

| # | Stars | Review (English gloss) | Expected category | Expected severity | Expected needs_response | qwen3.5:0.8b category | qwen3.5:2b category |
|---|---|---|---|---|---|---|---|
| 1 | 1 | Not delivered yet / delivery delay | `not_received` | high | true | ❌ delivery_delay | ❌ delivery_delay |
| 2 | 1 | 30 days after purchase the store said the item is out of stock | `seller_or_support` | high | true | ❌ delivery_delay | ❌ not_received |
| 3 | 1 | Other items arrived but the HDMI cable was not delivered | `wrong_or_missing_item` | high | true | ❌ delivery_delay | ❌ not_received |
| 4 | 1 | Not satisfied, I still haven't received the product | `not_received` | high | true | ✅ | ✅ |
| 5 | 2 | Both trackers didn't work; returned, waiting for refund | `damaged_or_defective` | high | true | ❌ product_quality | ❌ delivery_delay |
| 6 | 2 | Got the product but want shipping refunded; had to pick it up at the post office | `billing_or_refund` | medium | true | ✅ | ✅ |
| 7 | 2 | Bought two vases but only received one | `wrong_or_missing_item` | high | true | ✅ | ✅ |
| 8 | 2 | It came totally wrong; please answer my email about the return | `wrong_or_missing_item` | high | true | ✅ | ✅ |
| 9 | 3 | Works like the original but material is worse; photo differs | `product_quality` | medium | true | ✅ | ✅ |
| 10 | 3 | I recommend it | `positive_feedback` | low | false | ✅ | ✅ |
| 11 | 3 | Product as expected but packaging too plain for a gift | `product_quality` | low | false | ✅ | ✅ |
| 12 | 3 | Problem with one cartridge; the black one doesn't work | `damaged_or_defective` | high | true | ❌ product_quality | ❌ product_quality |
| 13 | 4 | Very good and pretty | `positive_feedback` | low | false | ✅ | ✅ |
| 14 | 4 | The bags are lovely, liked them a lot | `positive_feedback` | low | false | ✅ | ✅ |
| 15 | 4 | Satisfied with the purchase, keep up the service | `positive_feedback` | low | false | ✅ | ✅ |
| 16 | 4 | Product as advertised, fast delivery, liked it | `positive_feedback` | low | false | ✅ | ✅ |
| 17 | 5 | Arrived as ordered and early; lens works fine, very satisfied | `positive_feedback` | low | false | ❌ delivery_delay | ✅ |
| 18 | 5 | Very good! Keep it up | `positive_feedback` | low | false | ✅ | ✅ |
| 19 | 5 | Recommend it, on-time delivery, driver installed fine | `positive_feedback` | low | false | ✅ | ✅ |
| 20 | 5 | Could you list the bag's measurements; otherwise great | `other` | low | false | ❌ product_quality | ❌ product_quality |

**Category matches:** qwen3.5:0.8b 13/20, qwen3.5:2b 14/20. The full metrics are in [RESULTS.md](RESULTS.md).
