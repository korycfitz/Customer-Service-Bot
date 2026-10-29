# Source Provenance

## Dataset

| | |
|---|---|
| Name | Brazilian E-Commerce Public Dataset by Olist |
| Source | Kaggle, [`olistbr/brazilian-ecommerce`](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| Version used | Kaggle dataset version 2 (the latest at the time of the run, fetched by `kagglehub`) |
| License | CC BY-NC-SA 4.0 (as listed on the Kaggle page) |
| How it is fetched | `dataset.py` → `kagglehub.load_dataset(KaggleDatasetAdapter.PANDAS, "olistbr/brazilian-ecommerce", <file>)` |
| Nature | A historical snapshot of real, anonymized orders from 2016–2018. **It is not a live order system.** |

### Files used

| File | Used for | Rows |
|---|---|---|
| `olist_order_reviews_dataset.csv` | Review triage (Week 1) | 99,224 total; 40,950 with a written comment |
| `olist_orders_dataset.csv` | Loaded by `load_orders()`; reserved for order investigation in later weeks | — |

### How the 20 held-out reviews were derived

`scripts/make_holdout.py` produces them deterministically:

1. Load the reviews and keep only rows with a non-empty `review_comment_message` (40,950 rows).
2. Remove any review whose text matches one of the few-shot examples in the prompt. Those examples are invented, so this only guards against leakage.
3. Take a stratified random sample of 4 reviews per star rating (1–5) with `random_state=42`, for 20 reviews.
4. Copy `review_id`, `review_score`, `review_comment_title` → `title`, and `review_comment_message` → `message`. The message is changed in only one way: whitespace and line breaks are collapsed.

The review text is the customers' original Portuguese. The English glosses in `docs/TEST_CASES.md` were written for readability and are not part of the dataset.

### Labels

The `gold_category`, `gold_severity` and `gold_needs_response` columns in `data/holdout_20_labeled.csv` are **not part of Olist**. An AI assistant (Claude) drafted them using the rules in the prompt in `triage.py`, and the project author then reviewed and approved them. Six borderline cases were flagged for extra review (rows 2, 3, 8, 9, 11 and 20 in `docs/TEST_CASES.md`).

## Simulated content

The prompt in `triage.py` contains three few-shot example reviews and answers. They are **invented (simulated)**, not taken from Olist. Any support message or policy text produced by this project is simulated and is labelled that way (the command-line output includes `"simulated": true`).

## Models

| Model | Ollama tag | Ollama ID | Size | Provider |
|---|---|---|---|---|
| Qwen3.5 0.8B | `qwen3.5:0.8b` | `d9c89605f39a` | 1.2 GB | Qwen (Alibaba Cloud), served locally through [Ollama](https://ollama.com/library/qwen3.5) |
| Qwen3.5 2B | `qwen3.5:2b` | `dfaf2605162e` | 3.1 GB | Same as above |

Inference settings: `temperature=0`, `think=False`, and JSON-schema-constrained output (`format=TriageResult.model_json_schema()`). The models run locally, with no API calls and no cost.

## Software versions (at time of the results run)

| Component | Version |
|---|---|
| Python | 3.9.6 |
| Ollama | 0.40.12 |
| `ollama` (Python) | 0.6.3 |
| `kagglehub` | 0.3.13 |
| `pandas` | 2.3.3 |
| `pydantic` | 2.13.5 |
| Hardware | Apple M2, 8 GB RAM |
