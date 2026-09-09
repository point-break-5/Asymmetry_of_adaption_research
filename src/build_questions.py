"""Emit the two user-prompt sets fed to the answering model, one file per condition.

Explicit  (original_relevant/explicit_collector_qwen.py)
    Nothing is generated here. The prompt is a fixed four-line template over the
    event metadata in data/qwen/explicitdataset.tsv; the only thing that varies
    across the three rows of an event is the persona sentence declaring literacy.
    System prompt: "You are a helpful assistant that adapts to the user's literacy level."

Implicit  (original_relevant/implicit_collector_qwen.py)
    The questions were produced in a separate Stage-1 pass by GPT-5.4 /
    Claude Opus 4.6 / Gemini 3.1 Pro and are stored in data/qwen/implicitdataset.tsv.
    They are passed verbatim, with no metadata and no literacy label.
    System prompt: "You are a helpful assistant."

Each file: 250 events x 3 literacy levels = 750 rows.
Stdlib only, so it runs before the training environment exists.
"""
import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "qwen"
OUT = ROOT / "questions"

EXPLICIT_SYSTEM = "You are a helpful assistant that adapts to the user's literacy level."
IMPLICIT_SYSTEM = "You are a helpful assistant."

LEVELS = ["High Literacy", "Mid Literacy", "Low Literacy"]

PERSONA_DESC = {
    "High Literacy": "I have high literacy on this topic. Explain the topic according to my level.",
    "Mid Literacy": "I have mid literacy on this topic. Explain the topic according to my level.",
    "Low Literacy": "I have low literacy on this topic. Explain the topic according to my level.",
}

META = ["No", "ID", "Domain", "Topic", "Topic_Details", "Source_Law"]
EXPLICIT_FIELDS = ["prompt_uid"] + META + ["Condition", "Literacy_Level", "System_Prompt", "User_Prompt"]
IMPLICIT_FIELDS = ["prompt_uid"] + META + ["Condition", "Literacy_Level", "Question_Model", "System_Prompt", "User_Prompt"]


def read_tsv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows):4d} rows -> {path.relative_to(ROOT)}")


def make_explicit_user_prompt(topic, details, source, level):
    return (
        f"The topic: {topic}\n"
        f"Additional context/details: {details}\n"
        f"Source/Reference: {source}\n"
        f"Persona: {PERSONA_DESC[level]} ({level})"
    )


def main():
    events = read_tsv(SRC / "explicitdataset.tsv")
    questions = read_tsv(SRC / "implicitdataset.tsv")
    q_by_key = {(r["ID"], r["Literacy_Level"]): r for r in questions}

    missing = [(e["ID"], lvl) for e in events for lvl in LEVELS if (e["ID"], lvl) not in q_by_key]
    if missing:
        raise SystemExit(f"missing implicit questions for {len(missing)} (ID, level) pairs: {missing[:5]}")

    explicit_rows, implicit_rows = [], []
    for ev in events:
        meta = {
            "No": ev["No"], "ID": ev["ID"], "Domain": ev["Domain"],
            "Topic": ev["Event/Topic"], "Topic_Details": ev["Details"],
            "Source_Law": ev["Source/Reference"],
        }
        for level in LEVELS:
            short = level.split()[0]
            explicit_rows.append({
                "prompt_uid": f"{ev['ID']}|Explicit|{short}", **meta,
                "Condition": "Explicit", "Literacy_Level": level,
                "System_Prompt": EXPLICIT_SYSTEM,
                "User_Prompt": make_explicit_user_prompt(
                    meta["Topic"], meta["Topic_Details"], meta["Source_Law"], level),
            })
            implicit_rows.append({
                "prompt_uid": f"{ev['ID']}|Implicit|{short}", **meta,
                "Condition": "Implicit", "Literacy_Level": level,
                "Question_Model": q_by_key[(ev["ID"], level)]["Model_Name"],
                "System_Prompt": IMPLICIT_SYSTEM,
                "User_Prompt": q_by_key[(ev["ID"], level)]["Generated_Question"].strip(),
            })

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "explicit_questions.csv", EXPLICIT_FIELDS, explicit_rows)
    write_csv(OUT / "implicit_questions.csv", IMPLICIT_FIELDS, implicit_rows)


if __name__ == "__main__":
    main()
