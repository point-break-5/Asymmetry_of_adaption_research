"""Data preparation for parity fine-tuning.

Builds supervised examples from newly_generated_answers/explicit_answers_local_base.csv.

The training signal is a *contrast*, not a single behaviour. Each event contributes three
examples that share the same topic and differ only in the declared literacy level:

    High -> the model's own original High response  (anchor: don't lose expert behaviour)
    Mid  -> the parity rewrite                      (target: simpler register, entities kept)
    Low  -> the parity rewrite                      (target: simplest register, entities kept)

Training only on Mid/Low would teach the model to write simply for everyone and quietly
destroy the High-literacy behaviour the audit measures against. Including High with its own
unchanged response anchors that end of the scale, so what the model learns is the mapping
from literacy signal to register -- while holding content constant.

Prompts are taken verbatim from the System_Prompt / User_Prompt columns, so what the model
trains on is byte-identical to what it will be prompted with at evaluation time.
"""
from __future__ import annotations

import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEVELS = ["High Literacy", "Mid Literacy", "Low Literacy"]
ANCHOR_LEVEL = "High Literacy"

IGNORE_INDEX = -100


def load_rows(path: Path) -> list[dict]:
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    sep = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter=sep))


def group_by_event(rows: list[dict]) -> dict[str, dict[str, dict]]:
    by: dict[str, dict[str, dict]] = {}
    for r in rows:
        by.setdefault(r["ID"], {})[r["Literacy_Level"]] = r
    return {k: v for k, v in by.items() if all(l in v for l in LEVELS)}


def split_event_ids(event_ids, test_frac: float = 0.20, seed: int = 42):
    """Event-level split, matching audit_utils.split_event_ids exactly.

    Splitting on events rather than rows is the whole point: all three literacy levels of an
    event are near-duplicates of one another, so a row-level split would put a paraphrase of
    every test target into the training set.
    """
    ids = sorted(str(i) for i in event_ids)
    rng = random.Random(seed)
    rng.shuffle(ids)
    n_test = max(1, round(len(ids) * test_frac))
    return sorted(ids[n_test:]), sorted(ids[:n_test])


# ---------------------------------------------------------------- target quality filter

_ENTITY = re.compile(
    r"\b(?:Article|Art\.|Section|Sec\.|Clause|Recital|Regulation|Directive|Paragraph)\s*\d+[A-Za-z0-9().\-]*"
    r"|[€$£]\s?[\d,]+(?:\.\d+)?"
    r"|\b\d+(?:\.\d+)?\s?%"
    r"|\b\d+\s+(?:days?|weeks?|months?|years?|hours?|minutes?)\b"
    r"|\b(?:19|20)\d{2}\b"
    r"|\b\d[\d,]*(?:\.\d+)?\b",
    re.IGNORECASE,
)


def _entities(text: str) -> set[str]:
    return {re.sub(r"\s+", " ", m).strip().lower().rstrip(".") for m in _ENTITY.findall(text or "")}


def entity_coverage(reference: str, candidate: str) -> float:
    ref = _entities(reference)
    return 1.0 if not ref else len(ref & _entities(candidate)) / len(ref)


def fk_grade(text: str) -> float:
    """Flesch-Kincaid grade (Eq. 1). Local copy so this module stays import-light."""
    words = re.findall(r"[A-Za-z']+", text or "")
    sents = [x for x in re.split(r"[.!?]+", text or "") if x.strip()]
    if not words or not sents:
        return 0.0
    def syl(w):
        w = re.sub(r"[^a-z]", "", w.lower())
        if not w:
            return 0
        n = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
            n -= 1
        return max(n, 1)
    return 0.39 * (len(words) / len(sents)) + 11.8 * (sum(syl(w) for w in words) / len(words)) - 15.59


def satisfies_objective(ev: dict[str, dict], target_column: str, reference_column: str,
                        min_coverage: float) -> bool:
    """The training objective, evaluated per event: entity parity AND a descending register.

    Filtering on coverage alone admits events whose rewrite kept the entities but flattened
    the register -- exactly the behaviour the fine-tune must not learn. Requiring both means
    every surviving example demonstrates the full target behaviour rather than half of it.
    """
    ref = ev[ANCHOR_LEVEL].get(reference_column) or ""
    fk = [fk_grade(ev[l].get(target_column) or "") for l in LEVELS]
    if not (fk[0] > fk[1] > fk[2]):
        return False
    return all(entity_coverage(ref, ev[l].get(target_column) or "") >= min_coverage
               for l in LEVELS[1:])


def build_records(events: dict[str, dict[str, dict]], keep_ids: set[str],
                  target_column: str = "parity_answer",
                  reference_column: str = "cleaned_answer",
                  min_coverage: float = 0.85,
                  balance_anchor: bool = True,
                  require_joint: bool = True,
                  seed: int = 42) -> tuple[list[dict], dict]:
    """One record per (event, level). Returns (records, stats).

    A Mid/Low target below `min_coverage` is dropped rather than trained on: the rewrite
    distribution is bimodal (median 1.00, p10 0.17), and the bad tail actively teaches the
    entity-dropping behaviour this fine-tune exists to remove. Anchor rows are always kept.
    """
    records, dropped = [], {"missing": 0, "low_coverage": 0, "empty": 0, "objective_unmet": 0}

    for eid in sorted(keep_ids):
        ev = events.get(eid)
        if not ev:
            dropped["missing"] += 1
            continue
        if require_joint and not satisfies_objective(ev, target_column, reference_column,
                                                     min_coverage):
            dropped["objective_unmet"] += 1
            continue
        high_ref = ev[ANCHOR_LEVEL].get(reference_column) or ""

        for level in LEVELS:
            row = ev[level]
            target = (row.get(target_column) or "").strip()
            if not target:
                dropped["empty"] += 1
                continue
            if level != ANCHOR_LEVEL:
                if entity_coverage(high_ref, target) < min_coverage:
                    dropped["low_coverage"] += 1
                    continue
            records.append({
                "event_id": eid,
                "level": level,
                "messages": [
                    {"role": "system", "content": row["System_Prompt"]},
                    {"role": "user", "content": row["User_Prompt"]},
                    {"role": "assistant", "content": target},
                ],
            })

    # Filtering removes only Mid/Low, so the anchor ends up over-represented (~47% of the
    # set). Down-sampling it to the mean of the other two keeps the three levels balanced,
    # so the contrast the model learns is not dominated by High-literacy examples.
    if balance_anchor:
        n_other = [sum(1 for r in records if r["level"] == l) for l in LEVELS if l != ANCHOR_LEVEL]
        target_n = max(1, round(sum(n_other) / len(n_other)))
        anchors = [r for r in records if r["level"] == ANCHOR_LEVEL]
        if len(anchors) > target_n:
            rng = random.Random(seed)
            keep = set(id(r) for r in rng.sample(anchors, target_n))
            records = [r for r in records if r["level"] != ANCHOR_LEVEL or id(r) in keep]
            dropped["anchor_balanced"] = len(anchors) - target_n

    records.sort(key=lambda r: (r["event_id"], LEVELS.index(r["level"])))
    stats = {"records": len(records), "events": len(keep_ids), "dropped": dropped,
             "by_level": {l: sum(1 for r in records if r["level"] == l) for l in LEVELS}}
    return records, stats


# ---------------------------------------------------------------- label masking

def mask_labels(prefix_ids: list[int], full_ids: list[int]) -> list[int] | None:
    """Loss on the assistant turn only.

    Returns labels, or None when the example is unusable. Everything up to and including the
    generation prompt is set to IGNORE_INDEX; without this the model is trained to reproduce
    the persona template, which is identical across two thirds of the dataset and would
    dominate the loss.
    """
    n = len(prefix_ids)
    if n >= len(full_ids):
        return None                                   # nothing to learn from
    if full_ids[:n] != prefix_ids:
        # tokenizer did not produce a clean prefix (rare template quirk); locate it instead
        n = _common_prefix_len(prefix_ids, full_ids)
        if n == 0 or n >= len(full_ids):
            return None
    labels = list(full_ids)
    labels[:n] = [IGNORE_INDEX] * n
    if all(l == IGNORE_INDEX for l in labels):
        return None
    return labels


def _common_prefix_len(a: list[int], b: list[int]) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def chat_ids(tokenizer, messages: list[dict], add_generation_prompt: bool) -> list[int]:
    """Token ids for a chat template, normalised across transformers versions.

    transformers >= 4.56 (and all of v5) default `apply_chat_template(tokenize=True)` to
    `return_dict=True`, so it hands back a BatchEncoding rather than a list of ids. Calling
    `list()` on that yields the dict KEYS -- ['input_ids', 'attention_mask'] -- which makes
    every prefix and full sequence length 2, so mask_labels sees len(prefix) >= len(full) and
    rejects the example. The symptom is a dataset of size zero with skipped['unmaskable']
    equal to the corpus size.

    Ask for a plain list where the kwarg exists, then unwrap defensively for every shape the
    call can return: BatchEncoding, dict, tensor, or a batched list-of-lists.
    """
    base = dict(tokenize=True, add_generation_prompt=add_generation_prompt)
    out = None
    for extra in ({"return_dict": False, "enable_thinking": False},
                  {"return_dict": False},
                  {"enable_thinking": False},
                  {}):
        try:
            out = tokenizer.apply_chat_template(messages, **base, **extra)
            break
        except TypeError:
            continue
    if out is None:
        raise RuntimeError("apply_chat_template rejected every keyword combination")

    if hasattr(out, "input_ids"):
        out = out.input_ids
    elif isinstance(out, dict):
        out = out["input_ids"]
    if hasattr(out, "tolist"):
        out = out.tolist()
    if len(out) and isinstance(out[0], (list, tuple)):
        out = out[0]

    ids = [int(t) for t in out]
    if not ids:
        raise RuntimeError("chat template produced no tokens")
    return ids


def encode_pair(tokenizer, messages: list[dict]) -> tuple[list[int], list[int]]:
    """(prefix, full) ids: system+user+generation prompt, and the same plus the assistant turn."""
    return (chat_ids(tokenizer, messages[:-1], add_generation_prompt=True),
            chat_ids(tokenizer, messages, add_generation_prompt=False))


def make_training_args(training_arguments_cls, *, warmup_ratio: float | None = None,
                       total_steps: int | None = None, **kw):
    """Build TrainingArguments across transformers versions. Returns (args, dropped).

    Version drift this handles:
      * `evaluation_strategy` was renamed `eval_strategy` in 4.46 and removed in 5.x.
      * `warmup_ratio` was removed in 5.x; `warmup_steps` remains, so the ratio is converted
        against the real step count.

    Introspecting the signature beats a try/except chain, which reports whichever argument
    the *fallback* tripped over rather than the one actually at fault -- e.g. a rejected
    `warmup_ratio` surfacing as "unexpected keyword argument 'evaluation_strategy'".
    """
    import inspect

    sig = set(inspect.signature(training_arguments_cls.__init__).parameters)

    if "eval_strategy" in kw and "eval_strategy" not in sig:
        if "evaluation_strategy" in sig:
            kw["evaluation_strategy"] = kw.pop("eval_strategy")

    if warmup_ratio:
        if "warmup_ratio" in sig:
            kw["warmup_ratio"] = warmup_ratio
        elif "warmup_steps" in sig and total_steps:
            kw["warmup_steps"] = max(1, int(round(warmup_ratio * total_steps)))

    dropped = sorted(k for k in kw if k not in sig)
    for k in dropped:
        kw.pop(k)
    return training_arguments_cls(**kw), dropped


def save_split(path: Path, train_ids, test_ids, meta: dict | None = None) -> None:
    """Persist the split so the post-training evaluation scores the same held-out events."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"train_ids": sorted(train_ids), "test_ids": sorted(test_ids),
               "n_train": len(train_ids), "n_test": len(test_ids)}
    if meta:
        payload.update(meta)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_split(path: Path) -> tuple[list[str], list[str]]:
    d = json.loads(Path(path).read_text())
    return d["train_ids"], d["test_ids"]
