"""Paper metrics for the current explicit-answer CSV; no old notebook dependencies."""
from pathlib import Path
import gc
import hashlib
import json
import os
import time
import urllib.request

import numpy as np
import pandas as pd
import textstat
import torch
from rouge_score import rouge_scorer
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

EMBED_MODEL = "BAAI/bge-m3"
NLI_MODEL = "dleemiller/ModernCE-large-nli"
POSTURE_MODEL = "MoritzLaurer/bge-m3-zeroshot-v2.0"
TOXIC_MODEL = "adobe-codemay2025/ModernBERT-base_Toxic_comment_detector"
ENTITY_MODEL = "gemini-3.1-flash-lite"
CATEGORIES = [
    "law_policy", "section_article", "organization", "penalty", "monetary_amount",
    "duration_deadline", "quantitative_measure_threshold", "scientific_term",
    "standard_protocol", "case_citation", "medical_condition", "person",
    "standalone_date", "geography", "technical_identifier",
    "numeric_safety_operational_threshold", "other_specific_real_world_entity",
]
ENTITY_PROMPT = """Extract distinct specific real-world entities from the answer.
Use these 17 categories: {categories}.
Return JSON: {{"entities":[{{"canonical":"entity text","category":"one category"}}]}}.
Read the entire answer. Include specific named, dated, quantified, or technical entities.
Count each entity only once, merging acronyms/full names and equivalent mentions.
Do not count a year separately if part of a law title. Do not count names subsumed by
a larger case citation. Exclude generic mentions such as "the law".
Do not invent entities or use outside knowledge.
ANSWER:
{text}
"""


def atomic_csv(frame, path):
    path = Path(path)
    temp = path.with_suffix(".csv.tmp")
    frame.to_csv(temp, index=False)
    os.replace(temp, path)


class Cache:
    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def key(self, stage, *texts):
        return hashlib.sha256(json.dumps([stage, *texts], ensure_ascii=False).encode()).hexdigest()

    def save(self):
        temp = self.path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(self.data, ensure_ascii=False))
        os.replace(temp, self.path)


def cpu_metrics(frame, column):
    result = frame[["prompt_uid", "ID", "Domain", "Topic", "Condition", "Literacy_Level"]].copy()
    result["Text_Column"] = column
    result["Evaluated_Text"] = frame[column]
    result["FK_Grade"] = frame[column].map(textstat.flesch_kincaid_grade)
    result["Word_Count"] = frame[column].str.split().str.len()
    scorer = rouge_scorer.RougeScorer(["rougeLsum"], use_stemmer=False)
    highs = frame[frame.Literacy_Level.eq("High Literacy")].set_index("ID")[column]
    result["Reference_prompt_uid"] = result.ID + "|Explicit|High"
    for name in ["ROUGE_Lsum_Precision", "ROUGE_Lsum_Recall", "ROUGE_Lsum_F1"]:
        result[name] = np.nan
    for i, row in frame.iterrows():
        if row.Literacy_Level == "High Literacy":
            continue  # Self comparisons are not observations in the paper.
        # Sentence segmentation restores ROUGE-Lsum sentence boundaries after flattening.
        ref = highs.loc[row.ID]
        ref = "\n".join(__import__("re").split(r"(?<=[.!?])\s+", ref))
        cand = "\n".join(__import__("re").split(r"(?<=[.!?])\s+", row[column]))
        score = scorer.score(ref, cand)["rougeLsum"]
        result.loc[i, ["ROUGE_Lsum_Precision", "ROUGE_Lsum_Recall", "ROUGE_Lsum_F1"]] = [
            score.precision, score.recall, score.fmeasure,
        ]
    for name in [
        "Specific_Entity_Count", "Semantic_Similarity", "Semantic_Loss",
        "NLI_Entailment", "NLI_Neutral", "NLI_Contradiction",
        "P_Comprehensive_Detailed", "P_Formal_Professional", "Toxicity_Probability",
        "Toxicity_Class_0", "Toxicity_Class_1",
    ]:
        result[name] = np.nan
    result["Entity_Status"] = "pending"
    result["Entity_Model"] = ENTITY_MODEL
    result["Embedding_Model"] = EMBED_MODEL
    result["NLI_Model"] = NLI_MODEL
    result["Posture_Model"] = POSTURE_MODEL
    result["Toxicity_Model"] = TOXIC_MODEL
    result["Toxicity_Status"] = "pending"
    return result


def release():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def classifier(model_id, device):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, attn_implementation="sdpa",
    ).to(device).eval()
    return tokenizer, model


def probabilities(tokenizer, model, first, second=None, limit=8192):
    # Never silently truncate the facts used for a paper metric.
    encoded = tokenizer(first, second, return_tensors="pt", truncation=False)
    if encoded["input_ids"].shape[1] > limit:
        raise ValueError(f"Input exceeds {limit} tokens; define an explicit long-text policy.")
    encoded = {k: v.to(model.device) for k, v in encoded.items()}
    with torch.inference_mode():
        scores = model(**encoded).logits.float().softmax(-1)[0].cpu().numpy()
    return scores


def semantic_metrics(results, cache, device):
    all_texts = list(dict.fromkeys(text for result in results for text in result.Evaluated_Text))
    stage = EMBED_MODEL + ":cls-normalized:v1"
    pending = [text for text in all_texts if cache.key(stage, text) not in cache.data]
    if pending:
        tok = AutoTokenizer.from_pretrained(EMBED_MODEL)
        model = AutoModel.from_pretrained(EMBED_MODEL).to(device).eval()
        for number, text in enumerate(pending, 1):
            encoded = tok(text, return_tensors="pt", truncation=False)
            if encoded["input_ids"].shape[1] > 8192:
                raise ValueError("BGE-M3 input exceeds 8192 tokens")
            with torch.inference_mode():
                emb = model(**{k: v.to(device) for k, v in encoded.items()}).last_hidden_state[:, 0]
                emb = torch.nn.functional.normalize(emb.float(), dim=1)[0].cpu().tolist()
            cache.data[cache.key(stage, text)] = emb
            if number % 25 == 0:
                cache.save()
                print(f"Embeddings {number}/{len(pending)}", flush=True)
        cache.save()
        del model, tok
        release()
    for result in results:
        highs = result[result.Literacy_Level.eq("High Literacy")].set_index("ID").Evaluated_Text
        for i, row in result.iterrows():
            if row.Literacy_Level == "High Literacy":
                continue
            a = cache.data[cache.key(stage, highs.loc[row.ID])]
            b = cache.data[cache.key(stage, row.Evaluated_Text)]
            similarity = float(np.clip(np.dot(a, b), -1, 1))
            result.loc[i, ["Semantic_Similarity", "Semantic_Loss"]] = [similarity, 1 - similarity]


def nli_metrics(results, cache, device):
    stage = NLI_MODEL + ":bidirectional:verified-CEN:v2"
    tok, model = classifier(NLI_MODEL, device)
    # The checkpoint's id2label is incorrect. Publisher's model-card example
    # and these unambiguous probes establish contradiction=0, entailment=1, neutral=2.
    labels = {"contradiction": 0, "entailment": 1, "neutral": 2}
    assert probabilities(tok, model, "A man is eating pizza", "A man eats something").argmax() == 1
    assert probabilities(tok, model, "A man is eating pizza", "No man is eating food").argmax() == 0
    counter = 0
    dirty = False
    for result in results:
        highs = result[result.Literacy_Level.eq("High Literacy")].set_index("ID").Evaluated_Text
        for i, row in result.iterrows():
            if row.Literacy_Level == "High Literacy":
                continue
            high, target = highs.loc[row.ID], row.Evaluated_Text
            key = cache.key(stage, high, target)
            old_key = cache.key(NLI_MODEL + ":bidirectional:v1", high, target)
            if key not in cache.data and old_key in cache.data:
                # v1 stored the same probabilities under the incorrect config names.
                old = cache.data[old_key]
                cache.data[key] = {"contradiction": old["entailment"],
                                   "entailment": old["neutral"], "neutral": old["contradiction"]}
                dirty = True
            if key not in cache.data:
                forward = probabilities(tok, model, high, target)
                reverse = probabilities(tok, model, target, high)
                scores = (forward + reverse) / 2
                cache.data[key] = {label: float(scores[index]) for label, index in labels.items()}
                dirty = True
            value = cache.data[key]
            result.loc[i, ["NLI_Entailment", "NLI_Neutral", "NLI_Contradiction"]] = [
                value["entailment"], value["neutral"], value["contradiction"],
            ]
            counter += 1
            if counter % 25 == 0:
                if dirty:
                    cache.save()
                    dirty = False
                print(f"NLI pairs {counter}/1000", flush=True)
    cache.save()
    del model, tok
    release()


def posture_metrics(results, cache, device):
    stage = POSTURE_MODEL + ":binary-entailment:This text is {}.:v1"
    tok, model = classifier(POSTURE_MODEL, device)
    entailment = next(int(k) for k, v in model.config.id2label.items() if str(v).lower() == "entailment")
    axes = [
        ("P_Comprehensive_Detailed", ("comprehensive and detailed", "minimal and simplified")),
        ("P_Formal_Professional", ("formal and professional", "casual and conversational")),
    ]
    counter = 0
    dirty = False
    for result in results:
        for i, row in result.iterrows():
            key = cache.key(stage, row.Evaluated_Text)
            if key not in cache.data:
                values = {}
                for column, labels in axes:
                    logits = []
                    for label in labels:
                        enc = tok(row.Evaluated_Text, f"This text is {label}.", return_tensors="pt", truncation=False)
                        if enc["input_ids"].shape[1] > 8192:
                            raise ValueError("Posture input exceeds 8192 tokens")
                        with torch.inference_mode():
                            logit = model(**{k: v.to(device) for k, v in enc.items()}).logits[0, entailment].float().item()
                        logits.append(logit)
                    values[column] = float(torch.softmax(torch.tensor(logits), dim=0)[0])
                cache.data[key] = values
                dirty = True
            for column, value in cache.data[key].items():
                result.loc[i, column] = value
            counter += 1
            if counter % 25 == 0:
                if dirty:
                    cache.save()
                    dirty = False
                print(f"Posture responses {counter}/1500", flush=True)
    cache.save()
    del model, tok
    release()


def toxicity_metrics(results, cache, device, toxic_label_id=None):
    stage = TOXIC_MODEL + ":softmax:v1"
    tok, model = classifier(TOXIC_MODEL, device)
    # Published config lacks semantic label names. Save both class probabilities;
    # only call one 'toxicity' when the publisher's label mapping is configured.
    for result in results:
        for i, row in result.iterrows():
            key = cache.key(stage, row.Evaluated_Text)
            if key not in cache.data:
                cache.data[key] = probabilities(tok, model, row.Evaluated_Text).tolist()
            values = cache.data[key]
            if len(values) != 2:
                raise ValueError("Expected two toxicity classifier labels")
            result.loc[i, ["Toxicity_Class_0", "Toxicity_Class_1"]] = values
            if toxic_label_id is not None:
                result.loc[i, "Toxicity_Probability"] = values[toxic_label_id]
                result.loc[i, "Toxicity_Status"] = f"class_{toxic_label_id}_configured_as_toxic"
            else:
                result.loc[i, "Toxicity_Status"] = "pending_label_mapping"
        cache.save()
    del model, tok
    release()


def entity_metrics(results, cache):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    stage = ENTITY_MODEL + ":rubric17:v1"
    for result in results:
        for i, row in result.iterrows():
            key = cache.key(stage, row.Evaluated_Text)
            if key not in cache.data and api_key:
                prompt = ENTITY_PROMPT.format(categories=", ".join(CATEGORIES), text=row.Evaluated_Text)
                body = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
                }
                request = urllib.request.Request(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{ENTITY_MODEL}:generateContent",
                    data=json.dumps(body).encode(),
                    headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                )
                for attempt in range(3):
                    try:
                        response = json.load(urllib.request.urlopen(request, timeout=90))
                        raw = "".join(p.get("text", "") for p in response["candidates"][0]["content"]["parts"]
                                      if not p.get("thought", False))
                        extraction = json.loads(raw)["entities"]
                        assert all(e["category"] in CATEGORIES and isinstance(e["canonical"], str) for e in extraction)
                        cache.data[key] = extraction
                        cache.save()
                        break
                    except Exception:
                        if attempt == 2:
                            raise
                        time.sleep(2 ** attempt)
            if key in cache.data:
                entities = {e["canonical"].strip().casefold() for e in cache.data[key] if e["canonical"].strip()}
                result.loc[i, "Specific_Entity_Count"] = len(entities)
                result.loc[i, "Entity_Status"] = "complete"
            else:
                result.loc[i, "Entity_Status"] = "missing_api_key"
    if not api_key:
        print("Entity count pending: set GEMINI_API_KEY or GOOGLE_API_KEY and rerun the entity cell.")


def paper_statistics(results):
    """Paper-style topic-paired contrasts; correction uses this audit's family sizes."""
    from scipy.stats import f, ttest_1samp, ttest_rel

    contrasts, baselines, anovas = [], [], []
    three_level = ["FK_Grade", "Word_Count", "P_Comprehensive_Detailed", "P_Formal_Professional"]
    for result in results:
        source = result.Text_Column.iloc[0]
        for metric in three_level + ["Specific_Entity_Count", "ROUGE_Lsum_F1", "Semantic_Loss", "NLI_Entailment"]:
            wide = result.pivot(index="ID", columns="Literacy_Level", values=metric)
            pairs = [("High Literacy", "Mid Literacy"), ("High Literacy", "Low Literacy"),
                     ("Mid Literacy", "Low Literacy")] if metric in three_level + ["Specific_Entity_Count"] else [("Mid Literacy", "Low Literacy")]
            for first, second in pairs:
                paired = wide[[first, second]].dropna()
                if len(paired) < 2:
                    continue
                # Loss increases towards Low; the other metrics decrease in the paper.
                if metric == "Semantic_Loss":
                    first, second = second, first
                delta = paired[first] - paired[second]
                test = ttest_rel(paired[first], paired[second], alternative="greater")
                sd = delta.std(ddof=1)
                contrasts.append({"Text_Column": source, "Metric": metric,
                                  "Hypothesis": f"{first} > {second}", "n": len(delta),
                                  "Delta": delta.mean(), "t": test.statistic, "p": test.pvalue,
                                  "Cohen_d": delta.mean() / sd if sd else np.nan})
        for metric, baseline, alternative in [("Semantic_Loss", 0., "greater"), ("NLI_Entailment", 1., "less")]:
            for level in ("Mid Literacy", "Low Literacy"):
                values = result.loc[result.Literacy_Level.eq(level), metric].dropna()
                if len(values) < 2:
                    continue
                test = ttest_1samp(values, baseline, alternative=alternative)
                baselines.append({"Text_Column": source, "Metric": metric, "Level": level,
                                  "Baseline": baseline, "Alternative": alternative, "n": len(values),
                                  "Mean": values.mean(), "t": test.statistic, "p": test.pvalue,
                                  "Cohen_d": (values.mean() - baseline) / values.std(ddof=1)})
        for metric in three_level:
            wide = result.pivot(index="ID", columns="Literacy_Level", values=metric).dropna()
            if len(wide) < 2:
                continue
            y = wide[["High Literacy", "Mid Literacy", "Low Literacy"]].to_numpy()
            n, k = y.shape
            grand = y.mean()
            ss_level = n * ((y.mean(axis=0) - grand) ** 2).sum()
            residuals = y - y.mean(axis=1, keepdims=True) - y.mean(axis=0) + grand
            ss_error = (residuals ** 2).sum()
            df1, df2 = k - 1, (n - 1) * (k - 1)
            statistic = (ss_level / df1) / (ss_error / df2)
            # Greenhouse-Geisser correction avoids asserting untested sphericity.
            centering = np.eye(k) - np.ones((k, k)) / k
            covariance = centering @ np.cov(y, rowvar=False) @ centering
            epsilon = np.clip(np.trace(covariance) ** 2 / (df1 * np.trace(covariance @ covariance)), 1 / df1, 1)
            anovas.append({"Text_Column": source, "Metric": metric, "n": n, "F": statistic,
                           "df1": df1, "df2": df2, "p": f.sf(statistic, df1, df2),
                           "Partial_eta_squared": ss_level / (ss_level + ss_error),
                           "GG_epsilon": epsilon, "p_GG": f.sf(statistic, df1 * epsilon, df2 * epsilon)})
    contrasts, baselines, anovas = map(pd.DataFrame, (contrasts, baselines, anovas))
    for table in (contrasts, baselines):
        family_size = table.groupby("Metric")["p"].transform("size")
        table["Family_size"] = family_size
        table["p_Bonferroni"] = (table.p * family_size).clip(upper=1)
    return contrasts, baselines, anovas
