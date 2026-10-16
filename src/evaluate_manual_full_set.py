"""Evaluate assistant-authored answers against a matched, corrected High reference.

This runs scoring models only. It never generates or edits answer text and does
not call a paid API. Missing paper entity extractions stay explicitly missing.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, t
import torch

from current_answer_metrics import (
    Cache, cpu_metrics, semantic_metrics, nli_metrics, posture_metrics,
    toxicity_metrics, paper_statistics, atomic_csv, ENTITY_MODEL, entity_metrics,
)

ROOT = Path(__file__).resolve().parent.parent
COLUMN = "For_fine_tuning_manual_full"
BASELINE = "Original_lower_with_corrected_High"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-only", action="store_true")
    parser.add_argument("--run-entity-api", action="store_true",
                        help="Explicitly allow Gemini entity extraction using an environment credential; may incur charges")
    args = parser.parse_args()
    source = ROOT / "newly_generated_answers/explicit_answers_local_knowledge.csv"
    frame = pd.read_csv(source, dtype=str, keep_default_na=False)
    assert len(frame) == 750 and frame.prompt_uid.is_unique
    assert frame.ID.nunique() == 250 and frame.groupby("ID").size().eq(3).all()
    assert COLUMN in frame and frame[COLUMN].str.strip().ne("").all(), "Assemble the complete validated set first"
    assert frame.groupby("ID").Literacy_Level.nunique().eq(3).all()
    batches = list((ROOT / "newly_generated_answers/manual_full_set").glob("*.json"))
    groups = [g for path in batches for g in json.loads(path.read_text())["groups"]]
    assert len(groups) == 250 and len({g["ID"] for g in groups}) == 250

    frame[BASELINE] = frame.Answer_only_cleaned
    high = frame.Literacy_Level.eq("High Literacy")
    frame.loc[high, BASELINE] = frame.loc[high, COLUMN]
    results = [cpu_metrics(frame, col) for col in (COLUMN, BASELINE)]
    out = ROOT / "evaluation_results/manual_full_set"
    out.mkdir(parents=True, exist_ok=True)
    cache = Cache(ROOT / "evaluation_results/manual_full_set_metric_cache.json")
    # Reuse already-computed baseline scores without mutating an older cache.
    previous = Cache(ROOT / "evaluation_results/paper_metric_cache.json")
    cache.data = {**previous.data, **cache.data}
    before_scores = len(cache.data)
    print(f"750 rows; 250 paired topics; cached scoring entries={before_scores}", flush=True)

    def save():
        for result, name in zip(results, ("assistant_authored_metrics.csv", "matched_original_metrics.csv")):
            atomic_csv(result, out / name)

    save()
    if not args.cpu_only:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch.set_num_threads(4)
        for scorer in (semantic_metrics, nli_metrics, posture_metrics):
            print(scorer.__name__, device, flush=True)
            scorer(results, cache, device)
            save()
        toxicity_metrics(results, cache, device, toxic_label_id=1)
        save()

    # Default: cached extractions only. No implicit API spending or pasted keys.
    stage = ENTITY_MODEL + ":rubric17:v1"
    for result in results:
        for index, row in result.iterrows():
            key = cache.key(stage, row.Evaluated_Text)
            if key in cache.data:
                entities = {e["canonical"].strip().casefold() for e in cache.data[key] if e["canonical"].strip()}
                result.loc[index, "Specific_Entity_Count"] = len(entities)
                result.loc[index, "Entity_Status"] = "complete_cached"
            else:
                result.loc[index, "Entity_Status"] = "not_run_no_paid_API_call"
    if args.run_entity_api:
        entity_metrics(results, cache)
    save()
    combined = pd.concat(results, ignore_index=True)
    metrics = ["FK_Grade", "Word_Count", "ROUGE_Lsum_F1", "ROUGE_Lsum_Recall", "Semantic_Similarity",
               "NLI_Entailment", "NLI_Contradiction", "P_Comprehensive_Detailed", "P_Formal_Professional",
               "Toxicity_Probability", "Specific_Entity_Count"]
    summary = combined.groupby(["Text_Column", "Literacy_Level"])[metrics].agg(["count", "mean", "std"])
    summary.to_csv(out / "summary_by_level.csv")
    contrasts, baselines, anovas = paper_statistics(results)
    for table, name in [(contrasts, "paper_paired_contrasts"), (baselines, "paper_baseline_tests"),
                        (anovas, "paper_repeated_measures_anova")]:
        table.to_csv(out / (name + ".csv"), index=False)

    # The observational unit is the topic, not 500 independent lower-level rows.
    comparisons = []
    for level in ("Mid Literacy", "Low Literacy"):
        new = results[0][results[0].Literacy_Level.eq(level)].set_index("ID")
        old = results[1][results[1].Literacy_Level.eq(level)].set_index("ID").reindex(new.index)
        for metric in metrics:
            paired = pd.DataFrame({"new": new[metric], "old": old[metric]}).dropna()
            if len(paired) < 2:
                continue
            delta = paired.new - paired.old
            sem = delta.std(ddof=1) / np.sqrt(len(delta))
            radius = t.ppf(.975, len(delta) - 1) * sem
            test = ttest_rel(paired.new, paired.old)
            comparisons.append({"Literacy_Level": level, "Metric": metric, "n_topics": len(paired),
                                "New_mean": paired.new.mean(), "Original_mean": paired.old.mean(),
                                "Change": delta.mean(), "Change_95CI_low": delta.mean() - radius,
                                "Change_95CI_high": delta.mean() + radius,
                                "p_two_sided": test.pvalue})
    comparisons = pd.DataFrame(comparisons)
    family = comparisons.p_two_sided.notna().sum()
    comparisons["p_Bonferroni_all_changes"] = (comparisons.p_two_sided * family).clip(upper=1)
    comparisons.to_csv(out / "paired_before_after_changes.csv", index=False)

    # Preserve a text-level fingerprint so a later answer edit cannot masquerade
    # as having been evaluated by this run.
    fingerprints = frame[["prompt_uid", "ID", "Literacy_Level"]].copy()
    fingerprints["Manual_SHA256"] = frame[COLUMN].map(digest)
    fingerprints["Original_lower_corrected_High_SHA256"] = frame[BASELINE].map(digest)
    fingerprints.to_csv(out / "evaluated_text_fingerprints.csv", index=False)
    metadata = {
        "complete_dataset": True, "rows": 750, "topics": 250,
        "manual_column": COLUMN, "baseline": BASELINE,
        "baseline_definition": "Original Answer_only_cleaned Mid/Low, identical corrected High for both conditions",
        "entity_API_requested": args.run_entity_api, "cpu_only": args.cpu_only,
        "entity_status": "See row statuses; missing values are not zero and are not replaced by regex proxies",
        "limitations": [
            "Readability constrained during authoring; significance is descriptive, not independent confirmation of comprehension",
            "Overlap, embeddings, NLI and posture are model-based proxies, not guarantees of factual or proposition completeness",
            "Non-significant differences do not establish equivalence; no equivalence margin was prospectively specified",
            "IND_06 original grade bands are incompatible with within-topic Low<Mid; retain the declared +/-1 bounds",
            "Source access/version limitations remain in each authoring batch; no blanket expert verification claimed",
            "No Qwen fine-tuning or post-training model evaluation has been performed",
        ],
    }
    (out / "evaluation_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(summary.to_string(), flush=True)
    print("Saved scoring tables in", out, flush=True)


if __name__ == "__main__":
    main()
