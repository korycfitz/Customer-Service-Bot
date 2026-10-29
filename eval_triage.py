"""Week 1 acceptance run: triage the 20 labelled holdout reviews with each model and compare."""
import argparse
import statistics
from pathlib import Path

import ollama
import pandas as pd

from triage import CATEGORIES, MODELS, triage_review

ROOT = Path(__file__).resolve().parent
LABELED = ROOT / "data" / "holdout_20_labeled.csv"
RESULTS = ROOT / "results"


def macro_f1(gold, pred, labels):
  scores = []
  for label in labels:
    tp = sum(g == label and p == label for g, p in zip(gold, pred))
    fp = sum(g != label and p == label for g, p in zip(gold, pred))
    fn = sum(g == label and p != label for g, p in zip(gold, pred))
    if tp + fp + fn == 0:
      continue  # label absent from both gold and predictions
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
  return sum(scores) / len(scores) if scores else 0.0


def p95(values):
  ordered = sorted(values)
  return ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))]


def model_sizes_gb():
  try:
    return {m.model: m.size / 1e9 for m in ollama.list().models}
  except Exception:
    return {}


def parse_bool(value):
  return str(value).strip().lower() in {"true", "1", "yes", "y", "t"}


def evaluate(model, holdout):
  rows = []
  for _, r in holdout.iterrows():
    text = r["message"] if pd.isna(r["title"]) else f"{r['title']}. {r['message']}"
    result, meta = triage_review(text, int(r["review_score"]), model)
    pred = result.model_dump() if result else {}
    rows.append({
      "review_id": r["review_id"],
      "review_score": r["review_score"],
      "message": r["message"],
      "gold_category": r["gold_category"],
      "pred_category": pred.get("category"),
      "gold_severity": r["gold_severity"],
      "pred_severity": pred.get("severity"),
      "gold_needs_response": parse_bool(r["gold_needs_response"]),
      "pred_needs_response": pred.get("needs_response"),
      "pred_summary_en": pred.get("summary_en"),
      **meta,
    })
    print(f"  {r['review_id'][:8]} gold={r['gold_category']:<22} pred={pred.get('category')}")
  return pd.DataFrame(rows)


def summarize(model, df, size_gb):
  n = len(df)
  tokens = df["completion_tokens"].sum()
  return {
    "model": model,
    "n": n,
    "schema_valid_rate": df["valid"].mean(),
    "retry_rate": df["retries"].mean(),
    "category_accuracy": (df["gold_category"] == df["pred_category"]).mean(),
    "category_macro_f1": macro_f1(df["gold_category"].tolist(), df["pred_category"].tolist(), CATEGORIES),
    "severity_accuracy": (df["gold_severity"] == df["pred_severity"]).mean(),
    "needs_response_accuracy": (df["gold_needs_response"] == df["pred_needs_response"]).mean(),
    "mean_latency_s": df["latency_s"].mean(),
    "p95_latency_s": p95(df["latency_s"].tolist()),
    "tokens_per_s": tokens / df["latency_s"].sum() if df["latency_s"].sum() else 0.0,
    "size_gb": size_gb,
    "cost_usd": 0.0,
  }


def write_report(summaries, frames):
  lines = [
    "# Week 1: Review Triage Model Comparison",
    "",
    f"Holdout: {summaries[0]['n']} hand-labelled Olist reviews (4 per star rating, seed 42).",
    "All models run locally through Ollama, so API cost is $0.",
    "",
    "| Metric | " + " | ".join(s["model"] for s in summaries) + " |",
    "|---|" + "---|" * len(summaries),
  ]
  fmt = {
    "schema_valid_rate": "{:.0%}", "retry_rate": "{:.0%}", "category_accuracy": "{:.0%}",
    "category_macro_f1": "{:.2f}", "severity_accuracy": "{:.0%}", "needs_response_accuracy": "{:.0%}",
    "mean_latency_s": "{:.2f}s", "p95_latency_s": "{:.2f}s", "tokens_per_s": "{:.1f}",
    "size_gb": "{:.2f} GB", "cost_usd": "${:.2f}",
  }
  for key, f in fmt.items():
    cells = [f.format(s[key]) if s[key] is not None else "n/a" for s in summaries]
    lines.append(f"| {key} | " + " | ".join(cells) + " |")

  for s, df in zip(summaries, frames):
    misses = df[df["gold_category"] != df["pred_category"]]
    lines += ["", f"## Category misses: {s['model']} ({len(misses)})", ""]
    for _, m in misses.iterrows():
      lines.append(f"- `{m['review_id'][:8]}` gold **{m['gold_category']}**, "
                   f"pred **{m['pred_category']}**: {m['message'][:120]}")

  best = max(summaries, key=lambda s: (s["category_accuracy"], s["schema_valid_rate"], -s["mean_latency_s"]))
  lines += [
    "",
    "## Recommendation",
    "",
    f"`{best['model']}` scores highest on category accuracy ({best['category_accuracy']:.0%}), "
    f"breaking ties on schema validity and then latency. "
    "Weigh this against memory use and latency in the table above before choosing a default.",
  ]
  (RESULTS / "model_comparison.md").write_text("\n".join(lines) + "\n")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--models", nargs="+", default=MODELS)
  args = parser.parse_args()

  holdout = pd.read_csv(LABELED)
  missing = holdout[["gold_category", "gold_severity", "gold_needs_response"]].isna().any(axis=1)
  if missing.any():
    raise SystemExit(f"{missing.sum()} holdout rows are missing gold labels in {LABELED}")
  bad = set(holdout["gold_category"]) - set(CATEGORIES)
  if bad:
    raise SystemExit(f"Unknown gold categories: {bad}")

  RESULTS.mkdir(exist_ok=True)
  sizes = model_sizes_gb()
  summaries, frames = [], []
  for model in args.models:
    print(f"Evaluating {model}")
    df = evaluate(model, holdout)
    df.to_csv(RESULTS / f"predictions_{model.replace(':', '_')}.csv", index=False)
    summaries.append(summarize(model, df, sizes.get(model)))
    frames.append(df)

  write_report(summaries, frames)
  print(pd.DataFrame(summaries).to_string(index=False))
  print(f"Report written to {RESULTS / 'model_comparison.md'}")


if __name__ == "__main__":
  main()
