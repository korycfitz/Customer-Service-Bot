# Customer-Service-Bot

A customer-support and operations assistant built on the [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Olist is a historical snapshot, not a live order system. Any policies or support messages this project produces are **simulated**.

**Current status: Week 1.** The assistant triages customer reviews: it assigns each one a category, a severity, a sentiment, whether it needs a response, and a short English summary. It is validated on 20 held-out reviews, and two local Qwen models are compared.

## Submission evidence (Week 1)

| Evidence | Where |
|---|---|
| Runnable code | `customer_service_app.py`, `triage.py`, `eval_triage.py`, `dataset.py` |
| Setup instructions | [Setup](#setup), below |
| Source provenance | [docs/PROVENANCE.md](docs/PROVENANCE.md) |
| Diagram | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Test cases with expected results | [docs/TEST_CASES.md](docs/TEST_CASES.md) and `tests/` |
| Results report | [docs/RESULTS.md](docs/RESULTS.md) (auto-generated metrics: [results/model_comparison.md](results/model_comparison.md)) |

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/download), to run the Qwen models locally (no API key or cost)
- About 5 GB of free disk space for the two models

## Setup

1. **Clone the repo and create a virtual environment**

   ```bash
   git clone https://github.com/korycfitz/Customer-Service-Bot.git
   cd Customer-Service-Bot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Ollama and download the models**

   ```bash
   brew install ollama        # macOS; other platforms: https://ollama.com/download
   ollama serve               # leave this running in its own terminal
   ollama pull qwen3.5:0.8b
   ollama pull qwen3.5:2b
   ```

3. **Dataset.** You don't need to download it yourself. `dataset.py` fetches it from Kaggle with `kagglehub` the first time it runs, and caches it locally after that. If the download fails, sign in to Kaggle and set up `kagglehub` credentials (see the [kagglehub README](https://github.com/Kaggle/kagglehub)).

## Usage

**Triage a single review:**

```bash
python customer_service_app.py --text "O produto chegou quebrado" --score 1
python customer_service_app.py --review-id 7d8d252cc0ae002b13db033ec1cd9dcb
```

**Run the Week 1 evaluation** (both models on the 20 labelled reviews):

```bash
python eval_triage.py
```

This writes `results/model_comparison.md` (a metrics table, the reviews each model missed, and a recommendation) and a `results/predictions_<model>.csv` file for each model.

**Run the tests** (offline; Ollama isn't needed):

```bash
pytest tests/
```

**Regenerate the holdout set** (optional; this overwrites `data/holdout_20.csv`):

```bash
python scripts/make_holdout.py
```

## Project layout

| Path | Purpose |
|---|---|
| `dataset.py` | Loads Olist orders and reviews from Kaggle |
| `triage.py` | Prompt, output schema, and validated triage call with one retry |
| `customer_service_app.py` | Command-line tool to triage one review |
| `eval_triage.py` | Week 1 evaluation and model comparison |
| `scripts/make_holdout.py` | Samples 20 reviews (4 per star rating, seed 42) |
| `data/holdout_20_labeled.csv` | Held-out reviews with gold labels (drafted, then reviewed by a human) |
| `results/model_comparison.md` | Latest comparison report |
| `tests/` | Offline tests for the schema and retry behavior |
| `docs/` | Provenance, architecture diagram, test cases, and results report |
