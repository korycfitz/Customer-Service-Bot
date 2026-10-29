"""Customer-support assistant CLI (Week 1: review triage).

Olist is a historical snapshot, not a live order system. Any support message
or policy this app produces is SIMULATED.
"""
import argparse
import json

from triage import DEFAULT_MODEL, MODELS, triage_review


def main():
  parser = argparse.ArgumentParser(description="Triage an Olist customer review.")
  source = parser.add_mutually_exclusive_group(required=True)
  source.add_argument("--review-id", help="review_id from olist_order_reviews_dataset.csv")
  source.add_argument("--text", help="review text to triage")
  parser.add_argument("--score", type=int, help="star rating 1-5 (optional with --text)")
  parser.add_argument("--model", default=DEFAULT_MODEL, choices=MODELS)
  args = parser.parse_args()

  text, score = args.text, args.score
  if args.review_id:
    from dataset import load_reviews

    reviews = load_reviews()
    match = reviews[reviews["review_id"] == args.review_id]
    if match.empty:
      raise SystemExit(f"No review with a comment found for review_id {args.review_id}")
    row = match.iloc[0]
    text, score = row["review_comment_message"], int(row["review_score"])

  result, meta = triage_review(text, score, args.model)
  if result is None:
    raise SystemExit(f"Model output failed validation after retry: {meta['error']}")

  print(json.dumps({"simulated": True, **result.model_dump(), "meta": meta}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
  main()
