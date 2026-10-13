"""Score the nine directly authored, source-corrected sample answers."""
from pathlib import Path
import argparse
import getpass
import json
import os

import numpy as np
import pandas as pd
import torch

from current_answer_metrics import (
    Cache, atomic_csv, cpu_metrics, semantic_metrics, nli_metrics,
    posture_metrics, toxicity_metrics, entity_metrics,
)


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", default="newly_generated_answers/manual_source_corrected_first_3_groups.json")
    parser.add_argument("--entity-key-input", action="store_true", help="Read a Gemini key securely without saving it")
    args = parser.parse_args()
    if args.entity_key_input:
        os.environ["GEMINI_API_KEY"] = getpass.getpass("Gemini key (not saved): ")
    csv_path = root / "newly_generated_answers/explicit_answers_local_knowledge.csv"
    authored_path = root / args.answers
    authored = json.loads(authored_path.read_text())
    column = authored["column"]
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    ids = frame.ID.drop_duplicates().head(3).tolist()
    assert ids == ["DIG_01", "DIG_02", "DIG_03"]
    sample = frame[frame.ID.isin(ids)].reset_index(drop=True).copy()
    assert len(sample) == 9 and sample.prompt_uid.is_unique
    assert sample.set_index("prompt_uid")[column].to_dict() == authored["responses"]
    for _, group in sample.groupby("ID"):
        assert set(group.Literacy_Level) == {"High Literacy", "Mid Literacy", "Low Literacy"}

    out_dir = root / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    output = out_dir / f"{authored_path.stem}_metrics.csv"
    cache = Cache(out_dir / f"{authored_path.stem}_cache.json")
    # Reuse unchanged High scores without altering the earlier version's cache.
    original_cache = out_dir / "manual_source_corrected_first_3_groups_cache.json"
    if cache.path != original_cache and original_cache.exists():
        cache.data.update(json.loads(original_cache.read_text()))
    tone_cache = out_dir / "manual_conversational_cache.json"
    if authored_path.stem == "manual_source_corrected_conversational_first_3_groups" and tone_cache.exists():
        cache.data.update(json.loads(tone_cache.read_text()))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Scoring 9 responses against their corrected High references on", device, flush=True)
    result = cpu_metrics(sample, column)
    baseline = cpu_metrics(sample, "Answer_only_cleaned")
    result["Original_FK_Grade"] = baseline.FK_Grade
    result["FK_Delta_vs_Original"] = result.FK_Grade - baseline.FK_Grade
    result["Reference_Scope"] = "Corrected High from the same topic, not the old High"
    atomic_csv(result, output)
    for stage in (semantic_metrics, nli_metrics, posture_metrics):
        print("Running", stage.__name__, flush=True)
        stage([result], cache, device)
        atomic_csv(result, output)
    print("Running toxicity", flush=True)
    toxicity_metrics([result], cache, device, toxic_label_id=1)
    atomic_csv(result, output)
    entity_metrics([result], cache)
    atomic_csv(result, output)

    row_metrics = ["FK_Grade", "Word_Count", "P_Comprehensive_Detailed",
                   "P_Formal_Professional", "Toxicity_Probability"]
    pair_metrics = ["ROUGE_Lsum_Precision", "ROUGE_Lsum_Recall", "ROUGE_Lsum_F1",
                    "Semantic_Similarity", "Semantic_Loss", "NLI_Entailment",
                    "NLI_Neutral", "NLI_Contradiction"]
    lower = result.Literacy_Level.ne("High Literacy")
    assert result[row_metrics].notna().all().all()
    assert result.loc[lower, pair_metrics].notna().all().all()
    assert result.loc[~lower, pair_metrics].isna().all().all()
    assert (result.loc[lower, "FK_Delta_vs_Original"].abs() <= 1).all()
    assert np.allclose(result.loc[lower, ["NLI_Entailment", "NLI_Neutral", "NLI_Contradiction"]].sum(axis=1), 1, atol=1e-5)
    print(result[["prompt_uid", *row_metrics, *pair_metrics, "Specific_Entity_Count", "Entity_Status"]].round(5).to_string(index=False))
    print("Means by literacy level:")
    print(result.groupby("Literacy_Level")[[*row_metrics, *pair_metrics]].mean().round(5).to_string())
    print("Saved:", output, flush=True)
    if args.entity_key_input:
        os.environ.pop("GEMINI_API_KEY", None)


if __name__ == "__main__":
    main()
