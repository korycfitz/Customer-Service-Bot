# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
from functools import lru_cache

import kagglehub
from kagglehub import KaggleDatasetAdapter

DATASET = "olistbr/brazilian-ecommerce"


def _load(file_path):
  # Load the latest version. See the documentation for additional arguments:
  # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
  return kagglehub.load_dataset(KaggleDatasetAdapter.PANDAS, DATASET, file_path)


@lru_cache(maxsize=None)
def load_orders():
  return _load("olist_orders_dataset.csv")


@lru_cache(maxsize=None)
def load_reviews():
  """Reviews that have a written comment (the only ones worth triaging)."""
  df = _load("olist_order_reviews_dataset.csv")
  has_text = df["review_comment_message"].fillna("").str.strip() != ""
  return df[has_text].reset_index(drop=True)


if __name__ == "__main__":
  print("First 5 records:", load_orders().head())
