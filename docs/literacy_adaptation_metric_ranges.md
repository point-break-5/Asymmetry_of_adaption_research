# Metric ranges for High-to-Mid/Low literacy adaptation

Updated: 13 October 2026.

## 1. Scope and what was actually used

This document describes the nine manually authored responses for `DIG_01`, `DIG_02`, and `DIG_03`: three corrected High answers and six Mid/Low rewrites. It covers both the initial source-corrected version and the later conversational version.

The goal is to **adapt language difficulty and the intended register without reducing access to important, accurate information**.

There are three different meanings of “range” below:

1. **Metric scale:** the mathematical range of a score.
2. **Acceptance range:** a numerical constraint actually enforced while checking the rewrites.
3. **Observed range:** the smallest and largest scores in these three topics. This is not a recommended cutoff, confidence interval, or population-wide range.

### Actual generation and checking process

- The assistant wrote these answers directly. Qwen did not generate these manual versions.
- High was corrected against the supplied 2025 legal source before Mid/Low were rewritten. The conversational version kept those corrected High answers unchanged.
- The factual brief required preservation of verified conditions, exceptions, named entities, numbers, dates, penalties, and practical steps. Unsupported claims from the old High answers were not preserved.
- **The fixed numerical acceptance range was FK grade within ±1 of the original answer at the same literacy level.** This was checked after drafting and used to revise the text.
- Formality scores were used to evaluate and revise the conversational drafts. The final six scores are lower than their corresponding initial manual scores. No absolute formality band or minimum reduction was established.
- ROUGE, embeddings, NLI, comprehensiveness, toxicity, and entity counts were evaluations, not an automated generation objective with preset acceptance thresholds. Some tone checks were performed during revision; the final content-alignment scores were calculated afterward.
- The document does **not** retroactively claim that thresholds such as cosine ≥0.90, entailment ≥0.90, or formality ≤0.50 governed generation. They did not.

The answers explain the historical, consolidated 2025 ordinance, which the official source identifies as replaced by a 2026 Act. They should not be used as unqualified statements of current law.

## 2. Reference and comparison rules

For topic `i`:

- `H_i`: the corrected High response.
- `M_i`: its Mid rewrite.
- `L_i`: its Low rewrite.
- `O_Mi`, `O_Li`: the original cleaned Mid/Low answers, used for readability baselines only.

ROUGE, semantic similarity/loss, and NLI compare `H_i` with `M_i` or `L_i`. They do not compare against the old, incorrect High answer.

FK grade, word count, entity count, posture, and toxicity are measured independently for each response. Their differences from High can then be calculated within a topic.

High self-comparison scores are deliberately blank in the result files. An embedding self-similarity of 1 or ROUGE self-overlap of 1 would be trivial, not evidence of successful adaptation. NLI self-entailment is model-dependent and is not guaranteed to equal 1.

## 3. Metric scales and intended behavior

| Metric / CSV field | Mathematical scale | Better direction or intended behavior | Fixed acceptance cutoff used? |
|---|---|---|---|
| `FK_Grade` | Real-valued; can be negative or exceed 18 | Appropriate difficulty for each audience; generally High > Mid > Low | Yes: original same-level grade ±1 for Mid/Low |
| `Word_Count` | Nonnegative integer; positive for these nonempty answers | Enough space to preserve and explain information | No |
| `ROUGE_Lsum_Precision` | 0–1 | Higher overlap, subject to natural rewriting | No |
| `ROUGE_Lsum_Recall` | 0–1 | Higher reference-word overlap, without copying errors | No |
| `ROUGE_Lsum_F1` | 0–1 | Higher balanced overlap, subject to readability | No |
| `Specific_Entity_Count` | Nonnegative integer; no fixed upper bound | Preserve relevant entities; raw count alone is insufficient | No |
| `Semantic_Similarity` | −1 to 1 | Higher similarity to corrected High | No |
| `Semantic_Loss` | 0–2 | Lower divergence from corrected High | No |
| `NLI_Entailment` | 0–1 | Strong logical alignment with corrected High | No |
| `NLI_Neutral` | 0–1 | Inspect unexplained increases; added explanations may legitimately be neutral | No |
| `NLI_Contradiction` | 0–1 | Low contradiction; inspect potentially conflicting claims | No |
| `P_Comprehensive_Detailed` | 0–1 | No substantial loss of informational completeness toward Low | No |
| `P_Formal_Professional` | 0–1 | Match the intended register; lower for the conversational rewrites | Relative reduction checked; no absolute band |
| `Toxicity_Probability` | 0–1 | Low at every literacy level | No |

`Toxicity_Class_0` and `Toxicity_Class_1` are the two classifier probabilities. In this implementation, class 1 is configured as toxic, so `Toxicity_Class_1` duplicates `Toxicity_Probability`; class 0 is its complement. These are not three independent metrics.

`Original_FK_Grade` stores the same-level baseline. `FK_Delta_vs_Original = FK_Grade − Original_FK_Grade`. Its mathematical scale is unbounded, but accepted Mid/Low values had to be in **[−1, +1]**. The corrected High answers were not subject to that constraint.

## 4. Details of each metric

### 4.1 Flesch–Kincaid reading grade

Formula:

`FK = 0.39 × (words / sentences) + 11.8 × (syllables / words) − 15.59`

The implementation uses `textstat.flesch_kincaid_grade`. Larger values generally indicate harder text. It is a surface readability estimate, not a direct test of comprehension, reader dignity, or factual quality.

The actual acceptance rule was:

`abs(FK(rewrite_i) − FK(original_same_level_i)) ≤ 1.0`

It was **not** `abs(FK(rewrite_i) − FK(H_i)) ≤ 1.0`. That would make the simpler versions nearly as difficult as High.

| Topic | Mid baseline | Allowed Mid interval | Low baseline | Allowed Low interval |
|---|---:|---:|---:|---:|
| DIG_01 | 6.878 | 5.878–7.878 | 6.802 | 5.802–7.802 |
| DIG_02 | 7.848 | 6.848–8.848 | 6.698 | 5.698–7.698 |
| DIG_03 | 6.726 | 5.726–7.726 | 7.787 | 6.787–8.787 |

The original DIG_03 Low grade was higher than its Mid grade. Therefore preserving each baseline alone does not guarantee sensible cross-level ordering. Check both the baseline interval and actual High/Mid/Low difficulty. Both manual versions had High > Mid > Low for these three topics.

### 4.2 Word count

The code counts whitespace-separated words with `.split()`. This is not a tokenizer-based token count.

There was no word-count acceptance band for the manual responses. Mid and Low may need more words than High to define technical terms and explain conditions. A mandatory High > Mid > Low length pattern could reintroduce information loss.

### 4.3 ROUGE-Lsum precision, recall, and F1

ROUGE-Lsum measures lexical overlap using summary-level longest-common-subsequence matching. The evaluator uses `rouge_score.RougeScorer`, without stemming. Because the cleaned text has flattened newlines, sentence boundaries are reconstructed using punctuation before scoring.

- **Precision:** matched overlap relative to the candidate wording.
- **Recall:** matched overlap relative to the High reference wording.
- **F1:** harmonic balance of precision and recall: `2PR / (P + R)`, or 0 when both are 0.

All three scores lie in [0, 1]. Higher scores indicate stronger lexical overlap, not guaranteed factual coverage or accuracy. Explanatory additions can reduce precision; valid paraphrases can reduce recall.

There was no minimum ROUGE threshold. Equal Mid and Low ROUGE scores were not required. Maximizing ROUGE by retaining difficult wording would conflict with the adaptation goal.

### 4.4 Specific entity count

The extractor uses `gemini-3.1-flash-lite` at temperature 0 and the paper's 17-category rubric: laws/policies, sections/articles, organizations, penalties, amounts, durations/deadlines, quantitative measures, scientific terms, standards/protocols, case citations, medical conditions, people, standalone dates, geography, technical identifiers, numeric safety/operational thresholds, and other specific real-world entities.

The prompt requests canonical entities and deduplication of repeated or equivalent mentions. It excludes generic references, separate years embedded in law titles, and names already subsumed by larger citations. The code additionally deduplicates stripped, case-folded canonical strings.

The result is a nonnegative count, with no universal upper bound. No numerical entity-count acceptance band was imposed.

The initial source-corrected version has complete counts for all nine responses. In the conversational version, only the unchanged High counts are available; the six rewritten Mid/Low counts remain pending. Their old counts cannot be carried forward as measurements of changed text.

Equal counts do not prove equal entities. Extra definitions may introduce additional entities without improving retention of the original ones.

### 4.5 Semantic similarity and loss

The evaluator uses `BAAI/bge-m3`, takes the CLS embedding, normalizes it, and computes cosine similarity between each rewrite and its corrected High response.

`similarity = cosine(e_H, e_target)`

`loss = 1 − similarity`

The mathematical ranges are [−1, 1] for cosine and [0, 2] for loss. Loss is **not mathematically restricted to [0, 1]**, although the observed losses here fall within that interval.

Higher similarity and lower loss are preferred. Neither proves that a critical exception or number was retained. There was no similarity floor or loss ceiling used as an acceptance gate.

### 4.6 Natural language inference

The evaluator uses `dleemiller/ModernCE-large-nli` and averages probabilities in both directions:

`p_label = (p_label(H → target) + p_label(target → H)) / 2`

Entailment, neutral, and contradiction each lie in [0, 1] and sum to approximately 1 for each pair. The checkpoint's metadata mapping was inconsistent with its publisher's example. The implementation uses the probe-verified mapping: contradiction = 0, entailment = 1, neutral = 2.

- **Entailment:** support/alignment between the texts. Prefer strong alignment for both Mid and Low.
- **Neutral:** insufficient support in one or both directions. Added definitions can increase neutrality without losing a reference fact.
- **Contradiction:** potentially conflicting content. Prefer low values and review suspicious claims.

Whole-response averaged NLI is not a claim-by-claim factual audit. No NLI cutoff was used to accept or reject the manual samples.

### 4.7 Informational comprehensiveness

`MoritzLaurer/bge-m3-zeroshot-v2.0` compares “comprehensive and detailed” with “minimal and simplified.” The hypothesis template is `This text is {label}.`; the two entailment logits are softmax-normalized to obtain `P_Comprehensive_Detailed`.

The score lies in [0, 1]. Its complement represents the other label within this binary comparison. It is not a percentage of retained facts or a calibrated probability that the response is complete.

The goal is to avoid systematic informational disadvantage for Low. No absolute cutoff was established, and this classifier should support—not replace—entity and claim coverage checks.

### 4.8 Formality / register

The same zero-shot model compares “formal and professional” with “casual and conversational,” using the same hypothesis template and binary normalization.

`P_Formal_Professional` lies in [0, 1]. Lower values favor the conversational label. It measures perceived register, not reading difficulty or respectfulness.

The conversational revision sought warmer, more direct language while retaining the legal details. Each final Mid/Low score is lower than its corresponding initial manual score. There was no absolute target such as Mid = 0.70 or Low = 0.40, and no minimum reduction was enforced. One Mid reduction was very small.

A desired High > Mid > Low register pattern is a goal, not a demonstrated universal result: in conversational DIG_02, Low scores about 0.836 and Mid about 0.776, reversing their desired order. All six rewritten scores remain relatively high. Plain language can also legitimately remain professional, so human review of the intended tone matters.

### 4.9 Toxicity

The evaluator uses `adobe-codemay2025/ModernBERT-base_Toxic_comment_detector`, with class 1 identified as toxic using the publisher's example.

The probability lies in [0, 1]. Prefer low values at all literacy levels. A lower score does not establish factual correctness, legal safety, or absence of every kind of harm. No toxicity cutoff was used as a generation gate.

## 5. Observed ranges: initial source-corrected version

Each interval below is the minimum–maximum across **three** responses at the indicated level. Pairwise metrics use the corrected High answer from the same topic.

| Metric | Mid range | Low range |
|---|---:|---:|
| FK grade | 6.383–7.620 | 5.758–7.027 |
| Word count | 381–509 | 391–548 |
| ROUGE precision | 0.4882–0.6196 | 0.4155–0.5642 |
| ROUGE recall | 0.5672–0.6716 | 0.5262–0.6335 |
| ROUGE-Lsum F1 | 0.5248–0.6372 | 0.4643–0.5968 |
| Specific entity count | 13–21 | 12–21 |
| Semantic similarity | 0.8817–0.9387 | 0.8583–0.9144 |
| Semantic loss | 0.0613–0.1183 | 0.0856–0.1417 |
| NLI entailment | 0.7970–0.9712 | 0.7596–0.9523 |
| NLI neutral | 0.0283–0.2009 | 0.0464–0.2379 |
| NLI contradiction | 0.00044–0.00211 | 0.00068–0.00248 |
| Comprehensive/detailed | 0.3422–0.4641 | 0.3436–0.4758 |
| Formal/professional | 0.9103–0.9307 | 0.8999–0.9266 |
| Toxicity | 0.00031–0.00150 | 0.00031–0.00145 |
| FK delta vs original same-level answer | −0.941 to +0.894 | −0.956 to −0.761 |

## 6. Observed ranges: conversational version

These are measured outcomes, **not acceptance bands**.

| Metric | Mid range | Low range |
|---|---:|---:|
| FK grade | 6.826–7.622 | 5.745–6.797 |
| Word count | 403–567 | 421–575 |
| ROUGE precision | 0.4388–0.5845 | 0.3914–0.5326 |
| ROUGE recall | 0.5558–0.6605 | 0.5376–0.6314 |
| ROUGE-Lsum F1 | 0.4905–0.6202 | 0.4530–0.5766 |
| Specific entity count | Pending | Pending |
| Semantic similarity | 0.8603–0.9256 | 0.8622–0.9027 |
| Semantic loss | 0.0744–0.1397 | 0.0973–0.1378 |
| NLI entailment | 0.7427–0.9091 | 0.6972–0.9220 |
| NLI neutral | 0.0901–0.2550 | 0.0770–0.3000 |
| NLI contradiction | 0.00080–0.00233 | 0.00106–0.00357 |
| Comprehensive/detailed | 0.2462–0.4281 | 0.2829–0.3388 |
| Formal/professional | 0.7756–0.9241 | 0.7813–0.8509 |
| Toxicity | 0.00028–0.00142 | 0.00034–0.00159 |
| FK delta vs original same-level answer | −0.954 to +0.895 | −0.990 to −0.952 |

### Corrected High reference ranges, unchanged between versions

| Row-level metric | High range |
|---|---:|
| FK grade | 14.073–14.983 |
| Word count | 358–456 |
| Specific entity count | 12–22 |
| Comprehensive/detailed | 0.2919–0.4912 |
| Formal/professional | 0.9267–0.9657 |
| Toxicity | 0.00028–0.00318 |

### Actual paired differences from High: conversational version

For each topic, `delta = target score − corrected High score`. The intervals summarize those three paired differences; they are **not** obtained by subtracting unrelated endpoints of the range tables.

| Row-level metric | Mid − High range | Low − High range |
|---|---:|---:|
| FK grade | −8.157 to −6.803 | −9.167 to −7.628 |
| Word count | +45 to +111 | +63 to +151 |
| Comprehensive/detailed | −0.0632 to −0.0312 | −0.2083 to +0.0469 |
| Formal/professional | −0.1511 to −0.0152 | −0.1844 to −0.0885 |
| Toxicity | −0.001765 to +0.000002 | −0.001595 to +0.000154 |
| Specific entity count | Pending | Pending |

More words are not inherently a failure: explanations can be longer. Lower comprehensiveness scores deserve investigation, but are not direct measurements of missing facts.

## 7. Important coverage measures not yet scored

These were discussed as desired safeguards, but are not numerical columns in the current evaluator:

- **Entity coverage/recall:** the fraction of relevant canonical High entities preserved in a rewrite. Scale: [0, 1]. Critical names, amounts, deadlines, and thresholds should be retained; actual matching needs contextual review. Raw entity-count equality is not this metric.
- **Entity precision:** the fraction of a rewrite's relevant entities supported by the source or legitimate explanations. Scale: [0, 1]. New unsupported entities should not be rewarded.
- **Claim coverage:** the fraction of verified important High claims retained, including conditions and exceptions. Scale: [0, 1] once a claim inventory and matching rubric are defined. No inventory-based numerical score has been calculated.
- **Sentence complexity/length:** an optional language diagnostic. No dedicated complexity measure or mean-sentence-length column was recorded for these manual samples; sentence length contributes indirectly to FK grade.

Full retention of critical verified facts is the qualitative requirement. A broader entity/claim coverage threshold, weighting scheme, or permissible loss margin has **not** been agreed or validated.

## 8. Statistical interpretation and future acceptance ranges

Desired language differences should be practically meaningful, not merely statistically significant. Readability and register differences can be tested with topic-paired contrasts, effect sizes, and multiple-testing adjustment once a sufficiently broad evaluation set is available.

For information preservation, “no significant difference” is not proof of equality. Use predefined **equivalence margins** for differences that may go either way, or **non-inferiority margins** to test whether Low is not meaningfully worse than Mid. Margins must be chosen using reviewed examples and task consequences before testing; the current observed min–max values should not become those margins automatically.

For pairwise metrics, compare `score(H, M)` with `score(H, L)`, rather than testing simpler responses against a perfect High self-score. Semantic similarity should be high at both levels, but need not equal 1. ROUGE equality is not mandatory because legitimate changes in wording affect it. NLI neutrality may increase with explanations; review critical claims rather than demanding all probabilities match exactly.

Only three closely related topics have been manually rewritten here. No claim of statistical equivalence, generalization, or validated universal acceptance cutoffs is supported by this sample.

The conversational revision reduced average formality (Mid 0.9222 → 0.8660; Low 0.9172 → 0.8226), but also reduced average entailment (Mid 0.8985 → 0.8241; Low 0.8659 → 0.7964). This trade-off remains visible; the samples are not evidence that every adaptation objective has been achieved.

## 9. Reproducibility and evidence

- [Metric implementation](../src/current_answer_metrics.py)
- [Manual-sample evaluation script](../src/evaluate_manual_sample.py)
- [Initial manual responses and provenance](../newly_generated_answers/manual_source_corrected_first_3_groups.json)
- [Conversational manual responses](../newly_generated_answers/manual_source_corrected_conversational_first_3_groups.json)
- [Initial manual scores](../evaluation_results/manual_source_corrected_first_3_groups_metrics.csv)
- [Conversational scores](../evaluation_results/manual_source_corrected_conversational_first_3_groups_metrics.csv)
- [Full-data evaluation notebook](../notebooks/02_evaluate_original_and_fine_tuning_paper_metrics.ipynb)
- [Paper](../8397_The_Asymmetry_of_Adaptati.pdf)

The measurement choices are an operational replication. The paper does not specify every preprocessing and classifier-hypothesis detail. Models are run without silent truncation and the evaluator enforces an 8192-token ceiling. Score caches are keyed by text, model, and method version. Credentials are not part of this document.

To reproduce the latest version's scores from the workspace root:

```bash
venv/bin/python src/evaluate_manual_sample.py \
  --answers newly_generated_answers/manual_source_corrected_conversational_first_3_groups.json
```

To also finish the six pending entity extractions, supply a valid key through the script's secure input option; do not put it in the command, notebook, or documentation:

```bash
venv/bin/python src/evaluate_manual_sample.py \
  --answers newly_generated_answers/manual_source_corrected_conversational_first_3_groups.json \
  --entity-key-input
```
