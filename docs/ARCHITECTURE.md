# Architecture (Week 1)

## Triage flow

```mermaid
flowchart LR
    K[(Kaggle<br/>olistbr/brazilian-ecommerce)] -->|kagglehub| D[dataset.py<br/>load_reviews]
    D --> APP[customer_service_app.py<br/>--text / --review-id]
    D --> H[scripts/make_holdout.py<br/>4 per star, seed 42]
    H --> L[(data/holdout_20_labeled.csv<br/>gold labels, human-reviewed)]

    APP --> T
    L --> E[eval_triage.py]
    E --> T

    subgraph T[triage.py · triage_review]
        direction TB
        P[System prompt<br/>categories, severity rules,<br/>simulated few-shot examples] --> O[Ollama · Qwen3.5<br/>temperature 0, JSON schema]
        O --> V{Pydantic<br/>TriageResult valid?}
        V -->|no, first try| R[Retry once with<br/>the validation error]
        R --> O
        V -->|no, after retry| N[Return None + error]
        V -->|yes| OK[Return TriageResult + meta]
    end

    OK --> OUT[JSON output<br/>simulated: true]
    E -->|compare pred vs gold| REP[results/model_comparison.md<br/>results/predictions_*.csv]
```

## Components

| Component | Responsibility |
|---|---|
| `dataset.py` | Fetches the Olist files from Kaggle and caches them; filters reviews down to those with text |
| `triage.py` | The prompt, the `TriageResult` schema, and the model call with validation and one retry |
| `customer_service_app.py` | Command-line entry point that triages one review |
| `scripts/make_holdout.py` | Builds the 20-review held-out set |
| `eval_triage.py` | Runs every model in `MODELS` over the held-out set and writes metrics and the report |
| `tests/` | Offline unit tests for the schema and retry logic (`ollama.chat` is mocked) |

## Output schema

| Field | Type | Allowed values |
|---|---|---|
| `category` | enum | `delivery_delay`, `not_received`, `wrong_or_missing_item`, `damaged_or_defective`, `product_quality`, `seller_or_support`, `billing_or_refund`, `positive_feedback`, `other` |
| `severity` | enum | `low`, `medium`, `high` |
| `sentiment` | enum | `negative`, `neutral`, `positive` |
| `needs_response` | bool | `true` / `false` |
| `summary_en` | string | One English sentence |
