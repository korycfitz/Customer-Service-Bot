import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import triage  # noqa: E402
from triage import TriageResult, triage_review  # noqa: E402

VALID = {
  "category": "damaged_or_defective",
  "severity": "high",
  "sentiment": "negative",
  "needs_response": True,
  "summary_en": "Product arrived broken.",
}


def fake_response(content):
  return {"message": {"content": content}, "prompt_eval_count": 10, "eval_count": 5}


def test_valid_json_parses():
  assert TriageResult.model_validate_json(json.dumps(VALID)).category == "damaged_or_defective"


def test_bad_category_rejected():
  with pytest.raises(ValidationError):
    TriageResult.model_validate({**VALID, "category": "shipping"})


def test_missing_field_rejected():
  data = dict(VALID)
  del data["severity"]
  with pytest.raises(ValidationError):
    TriageResult.model_validate(data)


def test_non_json_rejected():
  with pytest.raises(ValidationError):
    TriageResult.model_validate_json("not json at all")


def test_retries_once_then_succeeds():
  responses = [fake_response("oops"), fake_response(json.dumps(VALID))]
  with patch.object(triage.ollama, "chat", side_effect=responses) as chat:
    result, meta = triage_review("Chegou quebrado", 1)
  assert chat.call_count == 2
  assert result is not None and meta["valid"] and meta["retries"] == 1
  assert meta["prompt_tokens"] == 20


def test_gives_up_after_one_retry():
  with patch.object(triage.ollama, "chat", return_value=fake_response("{}")) as chat:
    result, meta = triage_review("Chegou quebrado", 1)
  assert chat.call_count == 2
  assert result is None and not meta["valid"] and meta["error"]
