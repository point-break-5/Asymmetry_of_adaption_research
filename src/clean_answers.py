"""Flatten a model answer to plain prose and store it as `cleaned_answer`.

Why this exists
---------------
Transformer-based evaluators are sensitive to surface formatting, so the audit scores
cleaned text rather than raw markdown (paper Section 4.1). `audit_utils.clean_response`
covers emoji, arrows, fenced code, tables and dividers, but leaves the constructs that
actually dominate these responses: `**bold**` (99.5%), `### headings` (82%), bullets
(96%), numbered lists (56%), backticks, blockquotes and links. This module strips those
too, so `cleaned_answer` is genuinely plain text.

What it deliberately preserves
------------------------------
Formatting syntax is removed; content is not. Words, numbers, dates, article and section
references, monetary amounts and named entities survive untouched, because the substantive
metrics (specific entity count, NLI entailment, semantic similarity) are measured on this
text. Two consequences worth knowing:

  * Heading and list-item text is kept, with a full stop appended when it lacks terminal
    punctuation. Dropping headings would delete content; leaving them unterminated would
    merge them into the next sentence and corrupt the Flesch-Kincaid sentence count.
  * Numbered markers ("1.", "2)") are kept, because enumerated conditions in legal text
    are content. Plain bullets ("-", "*", "•") are dropped, because they are not.

The transform is idempotent: cleaning already-clean text is a no-op.

Usage
-----
    from clean_answers import clean_answer, clean_file
    clean_file(Path("newly_generated_answers/explicit_answers_local_base.csv"))

    python src/clean_answers.py                                  # every csv in newly_generated_answers/
    python src/clean_answers.py FILE ...                         # specific files
    python src/clean_answers.py --column LLM_Response FILE.tsv   # e.g. the historical Qwen files
    python src/clean_answers.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------- character level

_EMOJI = re.compile(
    "["
    "\U0001F000-\U0001FAFF"   # pictographs, emoticons, transport, symbols, extended-A
    "\U00002190-\U000021FF"   # arrows
    "\U00002300-\U000023FF"   # technical
    "\U00002500-\U00002BFF"   # box drawing, block elements, geometric shapes, misc symbols
    "\U0000FE00-\U0000FE0F"   # variation selectors
    "\U0001F3FB-\U0001F3FF"   # skin-tone modifiers
    "\U00002700-\U000027BF"   # dingbats
    "‍⁠﻿"      # zero-width joiner / word joiner / BOM
    "]+",
    flags=re.UNICODE,
)

# Arrows carry meaning in procedural text, so they become words rather than vanishing.
_ARROWS = [
    ("-->", " leads to "), ("->", " leads to "), ("=>", " leads to "), ("==>", " leads to "),
    ("→", " leads to "), ("⇒", " leads to "), ("►", " leads to "), ("▶", " leads to "),
    ("<--", " comes from "), ("<-", " comes from "), ("←", " comes from "), ("⇐", " comes from "),
    ("▼", " then "), ("▲", " then "),
]

_PUNCT = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "‒": "-", "―": "-", "−": "-",
    "…": "...", " ": " ", " ": " ", " ": " ", "​": "",
    "«": '"', "»": '"',
}

# ---------------------------------------------------------------- block level

_FENCE = re.compile(r"```[^\n`]*\n?(.*?)```", re.DOTALL)
_HTML_BLOCK = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_HTML_TAG = re.compile(r"</?[a-zA-Z][^>\n]{0,200}>")
_DIVIDER = re.compile(r"^\s*(?:[-_*=]\s*)+$")   # any all-separator line, incl. a lone "-" from an em dash
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")
_SETEXT = re.compile(r"^\s*(?:=|-){3,}\s*$")
_QUOTE = re.compile(r"^(?:\s*>(?:[ \t]|$))+")   # ">" + space only; ">4.5 hours" is a threshold, not a quote
_BULLET = re.compile(r"^[-*+•▪◦‣·]\s+(.*)$")
_NUMBERED = re.compile(r"^(\d{1,3}[.)]|[a-zA-Z][.)]|\([0-9a-zA-Z]{1,3}\))\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?[\s\-:|]+\|[\s\-:|]*$")

# ---------------------------------------------------------------- inline level

_IMAGE = re.compile(r"!\[([^\]\n]*)\]\([^)\n]*\)")
_LINK = re.compile(r"\[([^\]\n]+)\]\((?:[^)\n]*)\)")
_AUTOLINK = re.compile(r"<((?:https?|mailto):[^>\s]+)>")
_CODE_SPAN = re.compile(r"`{1,3}([^`\n]+?)`{1,3}")
_BOLD_ITALIC = re.compile(r"\*{3}([^\n*]+?)\*{3}")
_BOLD = re.compile(r"\*{2}([^\n*]+?)\*{2}|__([^\n_]+?)__")
_ITALIC_STAR = re.compile(r"(?<![\w*])\*(?!\s)([^\n*]+?)(?<!\s)\*(?![\w*])")
_ITALIC_US = re.compile(r"(?<![\w_])_(?!\s)([^\n_]+?)(?<!\s)_(?![\w_])")
_STRIKE = re.compile(r"~~([^\n~]+?)~~")
_FOOTNOTE = re.compile(r"\[\^[^\]\n]+\]")

_TERMINAL = re.compile(r"[.!?:;,\"')\]]$")


def _normalise_chars(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", str(text))
    text = _HTML_BLOCK.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = _EMOJI.sub(" ", text)
    for src, dst in _PUNCT.items():
        text = text.replace(src, dst)
    for src, dst in _ARROWS:          # after _PUNCT: "0.2-10" must not become "0.2 leads to 10"
        text = text.replace(src, dst)
    return text


def _unfence(text: str) -> str:
    """Keep the contents of fenced blocks, drop the fences and box-drawing padding."""
    def repl(m):
        body = m.group(1)
        body = "".join(" " if 0x2500 <= ord(c) <= 0x257F else c for c in body)
        body = re.sub(r"[ \t]+", " ", body)
        return re.sub(r"\n{2,}", "\n", body).strip()
    return _FENCE.sub(repl, text)


def _strip_inline(s: str) -> str:
    s = _IMAGE.sub(r"\1", s)
    s = _LINK.sub(r"\1", s)          # keep the anchor text, drop the URL
    s = _AUTOLINK.sub(r"\1", s)
    s = _FOOTNOTE.sub("", s)
    s = _CODE_SPAN.sub(r"\1", s)
    s = _BOLD_ITALIC.sub(r"\1", s)
    s = _BOLD.sub(lambda m: m.group(1) or m.group(2), s)
    s = _ITALIC_STAR.sub(r"\1", s)
    s = _ITALIC_US.sub(r"\1", s)
    s = _STRIKE.sub(r"\1", s)
    s = s.replace("\\*", "*").replace("\\_", "_").replace("\\#", "#")
    return re.sub(r"[ \t]+", " ", s).strip()


def _tables_to_sentences(lines: list[str]) -> list[str]:
    """Turn `| a | b |` rows into 'header is value' sentences; the numbers must survive."""
    out, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not (line.startswith("|") and line.endswith("|") and line.count("|") >= 2):
            out.append(lines[i])
            i += 1
            continue
        if _TABLE_SEP.match(line):
            i += 1
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1].strip()):
            headers = [_strip_inline(c) for c in cells]
            i += 2
            while i < len(lines):
                row = lines[i].strip()
                if not (row.startswith("|") and row.endswith("|") and row.count("|") >= 2):
                    break
                values = [_strip_inline(c) for c in row.strip("|").split("|")]
                pairs = []
                for j, v in enumerate(values):
                    if not v:
                        continue
                    h = headers[j] if j < len(headers) else ""
                    pairs.append(f"{h} is {v}" if h else v)   # blank header: keep the value alone
                if pairs:
                    out.append(". ".join(pairs) + ".")
                i += 1
        else:
            kept = [_strip_inline(c) for c in cells if c.strip()]
            if kept:
                out.append(". ".join(kept) + ".")
            i += 1
    return out


def _is_heading(hashes: str, body: str) -> bool:
    """`## Anything` is a heading. A lone `#` only is when the text reads like a title --
    otherwise "# of coordination seats" ("number of") loses its meaning."""
    if len(hashes) >= 2:
        return True
    return bool(body) and not body[0].islower()


def _process_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        s = _strip_inline(raw.strip())
        if not s or _DIVIDER.match(s) or _SETEXT.match(s):
            out.append("")
            continue

        needs_stop = False

        m = _HEADING.match(s)
        if m and _is_heading(m.group(1), m.group(2).strip()):
            s, needs_stop = m.group(2).strip(), True
        else:
            unquoted = _QUOTE.sub("", s)
            if unquoted != s:
                s = unquoted.strip()
            m = _BULLET.match(s)
            if m:
                s, needs_stop = m.group(1).strip(), True
            else:
                m = _NUMBERED.match(s)
                if m:                       # keep the marker: enumerated conditions are content
                    s, needs_stop = f"{m.group(1)} {m.group(2).strip()}", True

        s = _strip_inline(s)
        if not s:
            out.append("")
            continue
        if needs_stop and not _TERMINAL.search(s):
            s += "."
        out.append(s)
    return out


def clean_answer(text) -> str:
    """Markdown/emoji-laden answer -> plain prose. Content preserved, syntax removed."""
    if text is None:
        return ""
    text = str(text)
    if not text.strip():
        return ""

    text = _normalise_chars(text)
    text = _unfence(text)
    lines = _tables_to_sentences(text.split("\n"))

    # Inline emphasis is stripped before block markers are read, so a heading or list item
    # wrapped in bold ("**5. Simple summary**") still exposes its marker. Repeating to a
    # fixpoint makes the transform idempotent whatever the nesting.
    for _ in range(3):
        after = _process_lines(lines)
        if after == lines:
            break
        lines = after

    text = "\n".join(lines)
    text = text.replace("•", " ").replace("‣", " ").replace("▪", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------- file processing

def clean_file(path: Path, column: str = "Answer", new_column: str = "cleaned_answer") -> int:
    """Add `new_column` immediately after `column`, rewriting the file in place.

    Rewrites atomically (temp file + replace), because this overwrites generated data that
    may have cost hours of GPU time. Uses the stdlib csv module -- no pandas needed, so it
    runs in a bare environment as well as inside the notebook.
    """
    import csv as _csv
    import os
    import tempfile

    _csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    sep = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","

    with open(path, newline="", encoding="utf-8") as fh:
        reader = _csv.DictReader(fh, delimiter=sep)
        fields = list(reader.fieldnames or [])
        if column not in fields:
            print(f"  skip {path.name}: no '{column}' column (has {fields[:6]}...)")
            return 0
        rows = list(reader)

    if new_column not in fields:
        fields.insert(fields.index(column) + 1, new_column)

    raw_w = new_w = 0
    for r in rows:
        src = r.get(column) or ""
        out = clean_answer(src)
        r[new_column] = out
        raw_w += len(src.split())
        new_w += len(out.split())

    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = _csv.DictWriter(fh, fieldnames=fields, delimiter=sep)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise

    kept = (new_w / raw_w) if raw_w else 1.0
    print(f"  {path.name}: {len(rows)} rows | '{new_column}' after '{column}' | "
          f"{raw_w:,} -> {new_w:,} words ({kept:.1%} kept)")
    return len(rows)


SELF_TEST = [
    (
        "### 🔹 What Mandatory Arbitration Means\n"
        "A **mandatory** clause under *Article 22(2)* requires arbitration.\n"
        "> *“Any claim shall be settled by binding arbitration”*\n"
        "- **Mandatory**: You cannot choose `litigation`\n"
        "1. Contractual Necessity\n"
        "---\n"
        "See [the GDPR](https://eur-lex.europa.eu/x) for detail.",
        "What Mandatory Arbitration Means.\n"
        "A mandatory clause under Article 22(2) requires arbitration.\n"
        '"Any claim shall be settled by binding arbitration"\n'
        "Mandatory: You cannot choose litigation.\n"
        "1. Contractual Necessity.\n\n"
        "See the GDPR for detail.",
    ),
    (
        "| Right | Article |\n|---|---|\n| **Erasure** | Art. 17 |\n| Portability | Art. 20 |",
        "Right is Erasure. Article is Art. 17.\nRight is Portability. Article is Art. 20.",
    ),
    ("Fine amounts up to €20,000,000 or 4% of turnover.",
     "Fine amounts up to €20,000,000 or 4% of turnover."),
    ("Honest work is better than copying.\n\n\u2014  \nSource: UNESCO Recommendation (2017)",
     "Honest work is better than copying.\n\nSource: UNESCO Recommendation (2017)"),
    ("Background varies geographically (0.2\u201310 mSv/year) and IV tPA stops at >4.5 hours.",
     "Background varies geographically (0.2-10 mSv/year) and IV tPA stops at >4.5 hours."),
    ("", ""),
]


def self_test() -> bool:
    ok = True
    for i, (src, want) in enumerate(SELF_TEST, 1):
        got = clean_answer(src)
        if got != want:
            ok = False
            print(f"FAIL {i}\n  want: {want!r}\n  got : {got!r}")
        elif clean_answer(got) != got:
            ok = False
            print(f"FAIL {i} not idempotent\n  again: {clean_answer(got)!r}")
    print("self-test: " + ("all passed" if ok else "FAILURES"))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--column", default="Answer", help="source column (default: Answer)")
    ap.add_argument("--new-column", default="cleaned_answer")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(0 if self_test() else 1)

    files = args.files or sorted((ROOT / "newly_generated_answers").glob("*.csv"))
    if not files:
        sys.exit("no files: generate answers first, or pass paths explicitly")

    print(f"cleaning {len(files)} file(s), '{args.column}' -> '{args.new_column}'")
    for f in files:
        clean_file(f, args.column, args.new_column)


if __name__ == "__main__":
    main()
