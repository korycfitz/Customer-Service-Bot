"""Sample 20 held-out reviews (4 per star rating) for hand labelling."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dataset import load_reviews  # noqa: E402
from triage import FEW_SHOT_TEXTS  # noqa: E402

SEED = 42
PER_STAR = 4
OUT = ROOT / "data" / "holdout_20.csv"


def main():
  reviews = load_reviews()
  reviews = reviews[~reviews["review_comment_message"].str.strip().isin(FEW_SHOT_TEXTS)]

  sample = reviews.groupby("review_score").sample(PER_STAR, random_state=SEED).reset_index(drop=True)
  out = sample[["review_id", "review_score", "review_comment_title", "review_comment_message"]].rename(
    columns={"review_comment_title": "title", "review_comment_message": "message"}
  )
  out["message"] = out["message"].str.replace(r"\s+", " ", regex=True).str.strip()
  for col in ["gold_category", "gold_severity", "gold_needs_response"]:
    out[col] = ""

  OUT.parent.mkdir(exist_ok=True)
  out.to_csv(OUT, index=False)
  print(f"Wrote {len(out)} rows to {OUT}")
  print("Fill in the gold_* columns and save as data/holdout_20_labeled.csv")


if __name__ == "__main__":
  main()
