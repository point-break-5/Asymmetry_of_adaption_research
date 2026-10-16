"""Validate directly authored batches and assemble them without model generation."""
from pathlib import Path
import argparse
import hashlib
import json
import os

import pandas as pd
import textstat
from scipy.stats import ttest_rel

ROOT = Path(__file__).resolve().parent.parent
COLUMN = "For_fine_tuning_manual_full"
LEVELS = {"high": "High Literacy", "mid": "Mid Literacy", "low": "Low Literacy"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    path = ROOT / "newly_generated_answers/explicit_answers_local_knowledge.csv"
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert len(frame) == 750 and frame.prompt_uid.is_unique
    original = frame.copy(deep=True)
    batch_dir = ROOT / "newly_generated_answers/manual_full_set"
    authored = {}
    for batch in sorted(batch_dir.glob("*.json")):
        payload = json.loads(batch.read_text())
        for group in payload["groups"]:
            assert group["ID"] not in authored, f"Duplicate topic: {group['ID']}"
            assert all(isinstance(group[k], str) and group[k].strip() for k in LEVELS)
            assert group.get("sources") and group.get("source_review"), group["ID"]
            authored[group["ID"]] = {**group, "batch_file": str(batch.relative_to(ROOT))}
    expected = frame.ID.drop_duplicates().tolist()
    assert set(authored).issubset(expected), "Unknown topic IDs"
    failures, audit = [], []
    for row in frame.itertuples():
        group = authored.get(row.ID)
        baseline = float(textstat.flesch_kincaid_grade(row.Answer_only_cleaned))
        key = next(k for k, v in LEVELS.items() if v == row.Literacy_Level)
        text = group[key].strip() if group else ""
        grade = float(textstat.flesch_kincaid_grade(text)) if text else None
        passes = bool(text) and (key == "high" or abs(grade - baseline) <= 1)
        if text and not passes:
            failures.append({"uid": row.prompt_uid, "FK": grade, "baseline": baseline,
                             "allowed": [baseline - 1, baseline + 1]})
        if text and ("<think>" in text or "</think>" in text):
            failures.append({"uid": row.prompt_uid, "error": "Thinking tags"})
        audit.append({"prompt_uid": row.prompt_uid, "ID": row.ID,
                      "Literacy_Level": row.Literacy_Level, "Original_FK": baseline,
                      "FK_Grade": grade, "Word_Count": len(text.split()) if text else None,
                      "FK_Passes": passes, "Status": "authored" if group else "pending",
                      "Source_Review": group["source_review"] if group else "",
                      "Notes": group.get("notes", "") if group else "",
                      "Batch_File": group["batch_file"] if group else ""})
    print(json.dumps({"groups_authored": len(authored), "groups_required": 250,
                      "responses_authored": 3 * len(authored), "FK_failures": failures}, indent=2))
    if failures:
        raise SystemExit("Revise the reported answers before assembling; no source CSV changed.")
    if args.require_complete and len(authored) != 250:
        raise SystemExit("Full set is incomplete; no source CSV changed.")
    if args.validate_only:
        return
    if COLUMN not in frame:
        frame[COLUMN] = ""
    for row in frame.itertuples():
        if row.ID in authored:
            key = next(k for k, v in LEVELS.items() if v == row.Literacy_Level)
            frame.at[row.Index, COLUMN] = authored[row.ID][key].strip()
    untouched = [c for c in original if c != COLUMN]
    pd.testing.assert_frame_equal(original[untouched], frame[untouched])
    temporary = path.with_suffix(".csv.tmp")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)
    out = ROOT / "evaluation_results"
    out.mkdir(exist_ok=True)
    pd.DataFrame(audit).to_csv(out / "manual_full_set_readability_audit.csv", index=False)
    manifest = {"column": COLUMN, "authoring": "Direct assistant-authored batches; no Qwen generation",
                "complete": len(authored) == 250, "groups_authored": len(authored),
                "responses_authored": 3 * len(authored),
                "pending_topics": [topic for topic in expected if topic not in authored],
                "readability_rule": "Mid/Low within original same-level cleaned FK +/-1",
                "known_feasibility_exception": "IND_06: cannot also impose Low<Mid within both original bounds",
                "statistics": "Not run on an incomplete set"}
    if len(authored) == 250:
        scores = pd.DataFrame(audit).pivot(index="ID", columns="Literacy_Level", values="FK_Grade")
        tests = []
        for first, second in [("High Literacy", "Mid Literacy"), ("High Literacy", "Low Literacy"), ("Mid Literacy", "Low Literacy")]:
            test = ttest_rel(scores[first], scores[second], alternative="greater")
            delta = scores[first] - scores[second]
            tests.append({"contrast": first + " > " + second, "n": len(delta),
                          "mean_difference": delta.mean(), "t": test.statistic,
                          "p_one_sided": test.pvalue, "p_Bonferroni": min(1., test.pvalue * 3),
                          "Cohen_d_paired": delta.mean() / delta.std(ddof=1)})
        manifest["statistics"] = tests
        # Export candidates only: this does not start training. Splitting by
        # topic prevents three literacy variants of one topic leaking across sets.
        export_dir = ROOT / "newly_generated_answers/manual_full_set_exports"
        export_dir.mkdir(exist_ok=True)
        ordered = sorted(expected, key=lambda topic: hashlib.sha256(("manual-full-v1:" + topic).encode()).hexdigest())
        splits = {topic: ("train" if i < 200 else "validation" if i < 225 else "test")
                  for i, topic in enumerate(ordered)}
        records = []
        for row in frame.itertuples():
            records.append({
                "prompt_uid": row.prompt_uid, "topic_id": row.ID,
                "literacy_level": row.Literacy_Level, "split": splits[row.ID],
                "messages": [{"role": "system", "content": row.System_Prompt},
                             {"role": "user", "content": row.User_Prompt},
                             {"role": "assistant", "content": getattr(row, COLUMN)}],
            })
        assert len(records) == 750 and all(len(r["messages"]) == 3 for r in records)
        for split in ("all", "train", "validation", "test"):
            selected = records if split == "all" else [r for r in records if r["split"] == split]
            (export_dir / f"assistant_authored_{split}.jsonl").write_text(
                "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in selected))
        pd.DataFrame({"ID": ordered, "Split": [splits[topic] for topic in ordered]}).to_csv(
            export_dir / "topic_split_manifest.csv", index=False)
        (export_dir / "source_provenance.json").write_text(json.dumps(
            {topic: {k: v for k, v in authored[topic].items() if k not in LEVELS}
             for topic in expected}, ensure_ascii=False, indent=2))
        manifest["candidate_exports"] = str(export_dir.relative_to(ROOT))
        manifest["split_topics"] = {"train": 200, "validation": 25, "test": 25}
        manifest["training_status"] = "Candidates only; no fine-tuning run or model-quality claim"
    (out / "manual_full_set_progress.json").write_text(json.dumps(manifest, indent=2))
    print("Saved", COLUMN, "and progress/readability audit. Pending entries are not filled with old answers.")


if __name__ == "__main__":
    main()
