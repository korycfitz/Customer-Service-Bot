"""Review triage: classify an Olist review into a validated, structured result."""
import json
import time
from typing import Literal, Optional, Tuple

import ollama
from pydantic import BaseModel, ValidationError

MODELS = ["qwen3.5:0.8b", "qwen3.5:2b"]
DEFAULT_MODEL = MODELS[0]

Category = Literal[
  "delivery_delay",
  "not_received",
  "wrong_or_missing_item",
  "damaged_or_defective",
  "product_quality",
  "seller_or_support",
  "billing_or_refund",
  "positive_feedback",
  "other",
]
CATEGORIES = list(Category.__args__)


class TriageResult(BaseModel):
  category: Category
  severity: Literal["low", "medium", "high"]
  sentiment: Literal["negative", "neutral", "positive"]
  needs_response: bool
  summary_en: str


SYSTEM_PROMPT = """You triage customer reviews from a Brazilian e-commerce marketplace (Olist).
Reviews are in Portuguese. Return ONLY a JSON object with these fields:

category (pick the main issue):
- delivery_delay: order arrived late or is late
- not_received: customer says the order never arrived
- wrong_or_missing_item: wrong product sent, or items missing from the order
- damaged_or_defective: product arrived broken or does not work
- product_quality: product works but is poor quality or not as described
- seller_or_support: complaint about seller or support communication
- billing_or_refund: payment, charge, invoice, cancellation or refund problems
- positive_feedback: satisfied customer, no issue
- other: anything else

severity:
- high: customer has not received the product, received a broken/wrong one, or lost money
- medium: real problem but the customer has the product (delay, quality, poor service)
- low: praise, minor remark, or no issue

sentiment: negative, neutral or positive.
needs_response: true if a support agent should contact the customer, false otherwise.
summary_en: one short English sentence describing the review.

Examples (simulated, written for this prompt):
Review: "Comprei há 30 dias e até agora nada chegou." Stars: 1
{"category": "not_received", "severity": "high", "sentiment": "negative", "needs_response": true, "summary_en": "Customer has not received the order after 30 days."}
Review: "Chegou antes do prazo, produto ótimo!" Stars: 5
{"category": "positive_feedback", "severity": "low", "sentiment": "positive", "needs_response": false, "summary_en": "Order arrived early and the product is great."}
Review: "Veio a cor errada, pedi azul e recebi preto." Stars: 2
{"category": "wrong_or_missing_item", "severity": "high", "sentiment": "negative", "needs_response": true, "summary_en": "Customer received the wrong color."}
"""

# Texts used in the few-shot examples above; the holdout must not contain them.
FEW_SHOT_TEXTS = [
  "Comprei há 30 dias e até agora nada chegou.",
  "Chegou antes do prazo, produto ótimo!",
  "Veio a cor errada, pedi azul e recebi preto.",
]


def _user_message(text: str, score: Optional[int]) -> str:
  stars = f" Stars: {score}" if score is not None else ""
  return f'Review: "{text}"{stars}'


def triage_review(
  text: str, score: Optional[int] = None, model: str = DEFAULT_MODEL
) -> Tuple[Optional[TriageResult], dict]:
  """Triage one review. Returns (result or None if still invalid after one retry, meta)."""
  messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": _user_message(text, score)},
  ]
  meta = {"model": model, "retries": 0, "valid": False, "latency_s": 0.0,
          "prompt_tokens": 0, "completion_tokens": 0, "error": None}

  for attempt in range(2):
    start = time.perf_counter()
    response = ollama.chat(
      model=model,
      messages=messages,
      format=TriageResult.model_json_schema(),
      options={"temperature": 0},
      think=False,
    )
    meta["latency_s"] += time.perf_counter() - start
    meta["prompt_tokens"] += response.get("prompt_eval_count") or 0
    meta["completion_tokens"] += response.get("eval_count") or 0
    content = response["message"]["content"]

    try:
      result = TriageResult.model_validate_json(content)
      meta["valid"] = True
      meta["error"] = None
      return result, meta
    except ValidationError as e:
      meta["error"] = str(e)
      if attempt == 0:
        meta["retries"] = 1
        messages += [
          {"role": "assistant", "content": content},
          {"role": "user", "content": f"That output was invalid:\n{e}\nReturn corrected JSON only."},
        ]

  return None, meta


if __name__ == "__main__":
  result, meta = triage_review("O produto chegou quebrado e ninguém responde.", 1)
  print(json.dumps(result.model_dump() if result else None, indent=2, ensure_ascii=False))
  print(meta)
