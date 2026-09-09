"""Rewrite Mid/Low responses to preserve entity parity while keeping the register descent.

One call per event group. The High response is handed over as the content source, the
existing Mid and Low responses as register exemplars only, and the model returns both new
responses as JSON in a single reply.

The inversion matters: asking a model to "improve" an existing Mid/Low makes it anchor on
that text and lightly edit, inheriting exactly the omissions being targeted. Sourcing all
content from High and using Mid/Low only to show the target reading level is what produces
the dissociation -- register still descends, content does not.

Flesch-Kincaid is 0.39*(words/sentence) + 11.8*(syllables/word) - 15.59. Keeping entities
raises syllables/word ("General Data Protection Regulation" is unavoidable), so the only
lever left is sentence length -- hence the explicit words-per-sentence targets below.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEVELS = ["High Literacy", "Mid Literacy", "Low Literacy"]

# words per sentence needed to hit the original FK grades once entities are preserved
WPS_TARGET = {"Mid Literacy": "15-20", "Low Literacy": "8-12"}

SYSTEM_PROMPT = (
    "You rewrite expert explanations for readers with less background knowledge. "
    "You never remove factual content to achieve simplicity. You achieve it by shortening "
    "sentences and choosing common words for everything except the technical terms themselves."
)

USER_TEMPLATE = """TOPIC: {topic}
SOURCE INSTRUMENT: {source_law}

=== HIGH-LITERACY RESPONSE (the content source) ===
{high}

=== EXISTING MID RESPONSE (register exemplar only - do not copy its content) ===
{mid}

=== EXISTING LOW RESPONSE (register exemplar only - do not copy its content) ===
{low}

TASK
Write a new MID response and a new LOW response.

Take ALL factual content from the HIGH response. The existing MID and LOW responses show
you the target reading level only; they are incomplete and you must not use them as your
source of facts.

PRESERVE - every one of these that appears in the HIGH response must appear in both the new
MID and the new LOW response, with its exact value:
  - law, regulation, directive, treaty and standard names
  - article, section, clause, recital and paragraph numbers
  - deadlines, durations, time limits and notice periods
  - monetary amounts, penalties, fines and fee thresholds
  - percentages, quantities, limits and numeric thresholds
  - organisation and agency names
  - dates, case citations, medical conditions, technical identifiers
  - every condition, exception, derogation and qualifying criterion
  - every procedural step the reader must take, in order

Also preserve the LOGICAL STRUCTURE. If the HIGH response says a right applies only when
three conditions are met, all three must survive. If it names four exceptions, all four must
survive. Simplify how a condition is worded, never whether it is stated.

ADD NOTHING. Do not introduce facts, numbers, examples or caveats that are not in the HIGH
response.

HOW TO LOWER THE READING LEVEL -- SENTENCE LENGTH
  - Shorten sentences. MID: aim for {mid_wps} words per sentence.
                       LOW: aim for {low_wps} words per sentence.
  - One fact per sentence. Split a long clause instead of dropping it.
  - Keep the technical term, then explain it in plain words immediately after.
    Example: "Article 22 of the GDPR. That is the rule about computers making decisions
    about you."
  - Length is not the goal. A LOW response as long as the HIGH one but easier to read is
    correct. A shorter one that dropped a deadline is wrong.

HOW TO LOWER THE READING LEVEL -- TONE (equally required, and scored)
Short sentences alone are not a lower register. A clipped legal brief is still a legal
brief. The tone must change too:
  - Talk to the reader as "you". Write "you have 30 days", never "the data subject has
    30 days" or "the consumer is entitled to 30 days".
  - Use contractions throughout: you'll, don't, can't, it's, that's, here's, won't, they're.
  - Never write: shall, pursuant to, hereby, thereof, therein, notwithstanding, in
    accordance with, is required to, obligations, provisions, constitutes, stipulates,
    deemed, subject to, with respect to, prior to, commence, utilise, adhere to.
    Write must, under, so, before, start, use, follow instead.
  - Open by answering what the reader actually wants to know. Do not open with the name of
    the instrument.
      Wrong: "Article 22(2) of the GDPR establishes three derogations to the prohibition."
      Right: "You can say no to a computer making a big decision about you. There are three
              exceptions, and they're set out in Article 22(2) of the GDPR."
  - LOW should read like explaining it to a friend -- warm, direct, second person.
    MID should read as clear and plain, but not chatty.

BEFORE YOU OUTPUT, CHECK
  1. List every number, date, amount and named instrument in the HIGH response.
  2. Confirm each one appears in your new MID and in your new LOW.
  3. Confirm you added no fact absent from the HIGH response.
  4. Confirm your LOW sentences are short.
  5. Confirm both responses say "you", use contractions, and contain none of the banned
     formal words above.
Fix anything that fails, then output.

OUTPUT
Return ONLY a JSON object, with no other text and no markdown fences:
{{"mid": "<new mid response>", "low": "<new low response>"}}
Escape newlines inside the strings as \\n. Do not use markdown formatting inside the strings."""


def build_user_prompt(topic: str, source_law: str, high: str, mid: str, low: str) -> str:
    return USER_TEMPLATE.format(
        topic=topic, source_law=source_law, high=high, mid=mid, low=low,
        mid_wps=WPS_TARGET["Mid Literacy"], low_wps=WPS_TARGET["Low Literacy"],
    )


# ---------------------------------------------------------------- tone gate

_CONTRACTION = re.compile(r"\b\w+'(?:s|t|re|ll|ve|d|m)\b", re.IGNORECASE)
_SECOND = re.compile(r"\b(you|your|yours)\b", re.IGNORECASE)

# Calibrated on this dataset's own two populations: the original Low responses
# (zero-shot P(formal) = 0.08) score 5.69 on average and 87% clear 2.0, while the first
# batch of rewrites (P(formal) = 0.86) average 1.05 and only 17% clear it. Formal
# *vocabulary* barely separated the two -- direct address and contractions did.
TONE_MIN = {"Mid Literacy": 1.5, "Low Literacy": 2.0}


def informality_score(text: str) -> float:
    """Contractions + second-person mentions per 100 words. Higher is less formal.

    A deliberate stand-in for the zero-shot Style axis: gating on the classifier that later
    measures the result would make that measurement circular, exactly as the regex entity
    proxy already does for entity count.
    """
    w = max(len((text or "").split()), 1)
    return 100.0 * (len(_CONTRACTION.findall(text or "")) + len(_SECOND.findall(text or ""))) / w


def tone_ok(text: str, level: str) -> bool:
    return informality_score(text) >= TONE_MIN.get(level, 2.0)


def retry_note(cov_ok: bool, tone_bad: list[str]) -> str:
    """Tell the model what failed. Resampling the same prompt at a lower temperature merely
    oscillates -- the first run showed coverage going 1.00 -> 0.43 -> 1.00 across passes."""
    notes = []
    if not cov_ok:
        notes.append("Your previous attempt DROPPED named entities, numbers or dates that appear "
                     "in the HIGH response. Copy every one of them across this time.")
    if tone_bad:
        notes.append("Your previous " + " and ".join(tone_bad) + " response was too formal. "
                     "Rewrite it talking directly to the reader as \"you\", using contractions "
                     "(you'll, don't, it's), and none of the banned formal words.")
    if not notes:
        return ""
    return "\n\nCORRECTION -- your previous attempt failed these checks:\n- " + "\n- ".join(notes)


# ---------------------------------------------------------------- JSON extraction

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
_TAGGED = re.compile(r"<MID>(.*?)</MID>.*?<LOW>(.*?)</LOW>", re.DOTALL | re.IGNORECASE)


def _escape_control_chars(raw: str) -> str:
    """Escape literal newlines/tabs that appear inside JSON string literals.

    Models routinely emit real line breaks inside the value despite being told to escape
    them, which makes json.loads fail on otherwise perfectly good output.
    """
    out, in_str, esc = [], False, False
    for ch in raw:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\":
            out.append(ch)
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            out.append(ch)
            continue
        if in_str and ch in "\n\r\t":
            out.append({"\n": "\\n", "\r": "\\r", "\t": "\\t"}[ch])
            continue
        out.append(ch)
    return "".join(out)


def _scan_field(raw: str, key: str) -> str | None:
    """Last resort: pull one field out by hand, tolerating anything inside the value."""
    m = re.search(rf'"{key}"\s*:\s*"', raw)
    if not m:
        return None
    i, buf, esc = m.end(), [], False
    while i < len(raw):
        ch = raw[i]
        if esc:
            buf.append({"n": "\n", "t": "\t", "r": "\r"}.get(ch, ch))
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == '"':
            # a closing quote is one followed by , } or the next key
            if re.match(r'\s*[,}]', raw[i + 1:i + 8]) or re.match(r'\s*"(?:mid|low)"', raw[i + 1:i + 12]):
                return "".join(buf).strip()
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    return "".join(buf).strip() or None


def parse_response(text: str) -> dict | None:
    """Return {'mid': str, 'low': str} or None. Tolerant of fences, prose and raw newlines."""
    if not text or not text.strip():
        return None

    m = _FENCE.search(text)
    body = m.group(1) if m else text
    start, end = body.find("{"), body.rfind("}")
    candidate = body[start:end + 1] if start != -1 and end > start else body

    for attempt in (candidate, _escape_control_chars(candidate)):
        try:
            obj = json.loads(attempt)
            if isinstance(obj, dict) and obj.get("mid") and obj.get("low"):
                return {"mid": str(obj["mid"]).strip(), "low": str(obj["low"]).strip()}
        except (json.JSONDecodeError, TypeError):
            pass

    mid, low = _scan_field(candidate, "mid"), _scan_field(candidate, "low")
    if mid and low:
        return {"mid": mid, "low": low}

    t = _TAGGED.search(text)           # the model fell back to the tag format
    if t:
        return {"mid": t.group(1).strip(), "low": t.group(2).strip()}
    return None


# ---------------------------------------------------------------- csv plumbing

def _read(path: Path):
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    sep = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with open(path, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh, delimiter=sep)
        return list(r.fieldnames or []), list(r), sep


def _write(path: Path, fields, rows, sep):
    """Atomic: this overwrites generated data that cost GPU hours."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, delimiter=sep)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def load_groups(path: Path, source_column: str = "cleaned_answer") -> list[dict]:
    """One dict per event: the three level responses plus the metadata the prompt needs."""
    fields, rows, _ = _read(path)
    if source_column not in fields:
        raise SystemExit(f"{path.name}: no '{source_column}' column -- run clean_answers.py first")

    by_event: dict[str, dict] = {}
    for r in rows:
        g = by_event.setdefault(r["ID"], {"ID": r["ID"], "Domain": r.get("Domain", ""),
                                          "Topic": r.get("Topic", ""),
                                          "Source_Law": r.get("Source_Law", ""),
                                          "Condition": r.get("Condition", "")})
        g[r["Literacy_Level"]] = r.get(source_column) or ""
    groups = [g for g in by_event.values() if all(g.get(l) for l in LEVELS)]
    return sorted(groups, key=lambda g: g["ID"])


def existing_parity(path: Path, new_column: str) -> set[str]:
    """Event IDs whose Mid and Low already carry a rewrite, so a run can resume."""
    fields, rows, _ = _read(path)
    if new_column not in fields:
        return set()
    done: dict[str, int] = {}
    for r in rows:
        if r["Literacy_Level"] in ("Mid Literacy", "Low Literacy") and (r.get(new_column) or "").strip():
            done[r["ID"]] = done.get(r["ID"], 0) + 1
    return {k for k, v in done.items() if v == 2}


def write_parity_column(path: Path, results: dict[str, dict], new_column: str = "parity_answer",
                        after_column: str = "cleaned_answer") -> int:
    """Insert `new_column` directly after `after_column`.

    Mid and Low rows get the rewrite. High rows carry their own unchanged text, so the
    column is complete and the three levels stay directly comparable downstream.
    """
    fields, rows, sep = _read(path)
    if new_column not in fields:
        fields.insert(fields.index(after_column) + 1, new_column)

    n = 0
    for r in rows:
        eid, lvl = r["ID"], r["Literacy_Level"]
        if lvl == "High Literacy":
            r[new_column] = r.get(after_column) or ""
        else:
            key = "mid" if lvl == "Mid Literacy" else "low"
            got = results.get(eid, {}).get(key)
            if got:
                r[new_column] = got
                n += 1
            else:
                r.setdefault(new_column, r.get(new_column) or "")
    _write(path, fields, rows, sep)
    return n


# ---------------------------------------------------------------- cheap verification

_ENTITY = re.compile(
    r"\b(?:Article|Art\.|Section|Sec\.|Clause|Recital|Regulation|Directive|Paragraph)\s*\d+[A-Za-z0-9().\-]*"
    r"|[€$£]\s?[\d,]+(?:\.\d+)?"
    r"|\b\d+(?:\.\d+)?\s?%"
    r"|\b\d+\s+(?:days?|weeks?|months?|years?|hours?|minutes?)\b"
    r"|\b(?:19|20)\d{2}\b"
    r"|\b\d[\d,]*(?:\.\d+)?\b",
    re.IGNORECASE,
)


def entity_proxy(text: str) -> set[str]:
    """Regex stand-in for the paper's rubric extractor -- free, and good enough to gate a
    rewrite loop. The authoritative count still comes from the Gemini extractor."""
    return {re.sub(r"\s+", " ", m).strip().lower().rstrip(".") for m in _ENTITY.findall(text or "")}


def coverage(high: str, candidate: str) -> float:
    """Share of the High response's entity-like tokens that survive into the rewrite."""
    h = entity_proxy(high)
    return 1.0 if not h else len(h & entity_proxy(candidate)) / len(h)


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(n, 1)


def fk_grade(text: str) -> float:
    """Flesch-Kincaid grade. Uses textstat when installed, else an equivalent estimate."""
    try:
        import textstat
        return float(textstat.flesch_kincaid_grade(text))
    except Exception:
        pass
    words = re.findall(r"[A-Za-z']+", text or "")
    sents = [s for s in re.split(r"[.!?]+", text or "") if s.strip()]
    if not words or not sents:
        return 0.0
    syl = sum(_syllables(w) for w in words)
    return 0.39 * (len(words) / len(sents)) + 11.8 * (syl / len(words)) - 15.59


def reset_column(path: Path, column: str = "parity_answer",
                 backup_to: str | None = "parity_answer_v1") -> int:
    """Clear `column` (optionally copying it aside first) so a rerun regenerates everything.

    Without this the resume logic sees 250 completed groups and does nothing.
    """
    fields, rows, sep = _read(path)
    if column not in fields:
        return 0
    if backup_to:
        if backup_to not in fields:
            fields.insert(fields.index(column) + 1, backup_to)
        for r in rows:
            r[backup_to] = r.get(column, "")
    for r in rows:
        r[column] = ""
    _write(path, fields, rows, sep)
    return len(rows)
