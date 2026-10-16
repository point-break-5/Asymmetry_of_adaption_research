# Project handoff: literacy-adaptive Qwen fine-tuning data

Last checked: **17 October 2026, Asia/Dhaka**.

This is a portable operational handoff for another assistant (Claude, Gemini, Codex, etc.). It records the user's goals, decisions, files, actual progress, limitations and next steps. It is not a transcript, hidden reasoning, or a claim that unfinished work is complete. Repository files and a fresh validation run take precedence over this snapshot.

## 1. Current instruction: pause before continuing

The latest user request is to create this `codex.md` context file, commit it and push it. **Do not continue generating/revising the dataset merely as part of this handoff.** Resume the underlying task only when the user asks to continue.

The underlying unfinished request is to regenerate responses for **all 250 topic groups** directly with the assistant, not Qwen. Each group has High, Mid and Low answers: 750 targets in total, including 500 Mid/Low rewrites. High may be corrected against authoritative sources where necessary. Preserve the existing CSV answer columns; assemble the new set into its own column.

## 2. User's research goal

Adapt answers to the user's literacy level while preserving informational access:

- Keep lower-literacy language easier to read, with a statistically significant aggregate High > Mid > Low readability gap.
- Preserve accurate facts, entities, technical identifiers, numbers, dates, conditions, exceptions, risks, remedies and practical steps across levels.
- Improve semantic similarity, ROUGE-Lsum and informational/entity coverage relative to the High reference, without copying hallucinations or adding irrelevant entities.
- Preserve the established readability constraint: **each Mid/Low FK grade must stay within ±1 of its original same-level `Answer_only_cleaned` value**. This is not ±1 of High.
- Plain-language answers can be longer than High when definitions are needed. Do not impose decreasing length as a goal.
- No thinking tags or reasoning traces in answer text. The current manual batches are plain paragraphs without Markdown tables, emojis or embedded newlines.

The user explicitly authorized parallel assistant agents using the same model to help author the set. They did not authorize replacing direct assistant authorship with a Qwen/API generation loop. A different assistant can continue the unfinished prose itself or delegate if the user's authorization and its environment permit.

Do not promise a mathematical global maximum of similarity, or statistical equivalence of information scores. No fixed ROUGE/cosine/NLI acceptance thresholds were prospectively established. A non-significant difference is not proof of equivalence.

## 3. Project and environment

- Repository: <https://github.com/point-break-5/Asymmetry_of_adaption_research>
- Local project root: `/home/anirban/Desktop/Research/qwen_before_after_audit_package_fixed_v2/qwen_before_after_audit`
- Shell: Bash.
- Existing interpreter: `venv/bin/python` (previous runs used Python 3.14).
- User GPU: NVIDIA RTX 5060 Ti, 16 GB VRAM.
- Local model targeted in earlier generation notebooks: Qwen3.5-4B. The unfinished manual-authoring task does **not** use that model to generate targets.
- Dependencies: `requirements.txt`; the existing environment has pandas, textstat, scipy, transformers, torch and evaluation dependencies installed.
- The latest date supplied by the user/client is 17 October 2026. Earlier source checks were mostly conducted on 15 October 2026. Do not silently describe dated legal explanations as current law forever.

Git state immediately before this handoff edit:

- Local branch `master` tracks **`origin/main`**, not `origin/master`.
- Both local HEAD and remote `main` were `a512eaf0c094cc84e0a994bf2114d06cb113916d` (`in the middle of generation 1`).
- Previous commit `a4c609c` published earlier research data, manual samples, evaluations and documentation.
- Worktree was clean. The current drafts and helper scripts were already committed in `a512eaf`.
- The safe intended push destination for this handoff is `git push origin HEAD:main`. Never force-push or reset user work.

## 4. Earlier workflow and important files

The user previously generated 750 explicit-condition answers locally, removed thinking text into `Answer_only`, cleaned presentation into `Answer_only_cleaned`, and generated a separate Qwen-based fine-tuning candidate column. Those older candidates were evaluated, then the user requested stronger direct assistant rewrites.

Primary files:

| Path | Role |
| --- | --- |
| `newly_generated_answers/explicit_answers_local_knowledge.csv` | Main 750-row dataset; 250 IDs, three literacy levels each |
| `notebooks/00_generate_all_explicit_answers_local_qwen_nonthinking.ipynb` | Earlier full local-Qwen generation notebook |
| `notebooks/01_generate_fine_tuning_answers_local_qwen_nonthinking.ipynb` | Earlier Mid/Low regeneration, separate prompts and nonthinking workflow |
| `notebooks/02_evaluate_original_and_fine_tuning_paper_metrics.ipynb` | Earlier paper-metric evaluation workflow/results |
| `notebooks/old/` | Archived notebooks; do not treat as controlling current workflow |
| `8397_The_Asymmetry_of_Adaptati.pdf` | User's source paper |
| `8397_The_Asymmetry_of_Adaptation_understanding.md` | Detailed reading/interpretation of the paper |
| `domain_knowledge/` | Topic/source inventory across domains; curated summaries are not automatically reliable ground truth |
| `docs/literacy_adaptation_metric_ranges.md` | Established metric definitions, actual ±1 FK rule, earlier three-topic sample results and caveats |
| `newly_generated_answers/manual_source_corrected_first_3_groups.json` | Earlier reviewed DIG_01–03 manual sample |
| `src/current_answer_metrics.py` | Existing scoring-model implementation reused by the new evaluator |

Main CSV fields include `prompt_uid`, `ID`, `Domain`, `Topic`, `Topic_Details`, `Source_Law`, `Condition`, `Literacy_Level`, `System_Prompt`, `User_Prompt`, `Answer`, `Answer_only`, `Answer_only_cleaned`, `For_fine_tuning`, `For_fine_tuning_cleaned`, and earlier manual sample columns. Inspect the real schema before editing.

Example UID: `DIG_13|Explicit|Low`. Literacy field values are `High Literacy`, `Mid Literacy`, `Low Literacy`. Join by UID or topic/level, not assumed row numbers.

## 5. What the paper means for this task

The central problem is **information stratification**, not successful adaptation of readability itself. Lower-literacy users often receive fewer concrete facts, exceptions, deadlines, entities and actionable details, even when answers are not contradictory. The paper's NLI pattern is mainly omission/neutrality rather than contradiction.

Its High answers are **relative references, not external truth**. This repository's original High answers and some prompt premises contained substantial errors. The new set corrects those errors before simplification. Do not maximize overlap with a false High answer.

The paper uses readability/length, ROUGE-Lsum, specific entities, BGE-M3 semantic divergence, bidirectional NLI, comprehensiveness/formality posture, and toxicity checks in the project's implementation. These are imperfect proxies. Human comprehension and downstream model performance are not established by a good score alone.

## 6. Manual authoring artifacts and ownership history

All authored answers live in `newly_generated_answers/manual_full_set/`. There are **28 JSON batch files containing 250 unique groups and 750 nonempty answer strings**.

Each file has `authoring` and `groups`. Each group has:

```json
{
  "ID": "DIG_13",
  "high": "Source-corrected High response",
  "mid": "Directly authored Mid response",
  "low": "Directly authored Low response",
  "sources": ["https://primary-source.example/..."],
  "source_review": "What was checked and any access/version limitations",
  "notes": "Substantive corrections and review notes"
}
```

Batch map:

- Root first 40 topics: `root_seed_DIG_01_03.json`, `root_batch_DIG_04_10.json`, `root_batch_DIG_11_14.json`, `root_batch_DIG_15_20.json`, `root_batch_LAB_01_08.json`, `root_batch_LAB_09_15.json`, `root_batch_MTS_01_05.json`.
- `author_a_batch_01.json`: food/nuclear safety; `02`: REF; `03`: DIS; `04`: CRI; `05`: ENV; `06`: IND; `07`: CON. Seventy topics total.
- `author_b_batch_01.json` through `07`: HUM, EFA, FIN, TEC, SEC, IMM, POL, respectively. Seventy topics total.
- `author_c_batch_01.json` through `07`: SCI, SAF, SOC, HOU, FRG/IPM, HEA, EDU, respectively. Seventy topics total.

The DIG_01–03 seed reuses previously directly authored and reviewed responses. It is explicitly marked as reused, not represented as newly generated.

Cross-reviews already applied:

- Root revised A's DIS batch for FK without changing its High references.
- B revised root LAB_09–15, A's ENV batch and A's IND batch.
- Root reviewed low-NLI HUM_01, added the family-of-four arithmetic example to High, and explicitly retained response-stage, access-monitoring and vulnerable-group details in Mid/Low.
- A read-only second review led root to retain “rather than replacing local groups” in HUM_05 Low, maintenance responsibility in HUM_08 Low, and phone-version variability in SEC_05 Low.
- C finished its own 70 groups and intended to revise A's consumer-rights batch, but **the saved CON batch still has 18 FK failures**. Do not assume that intended work happened.
- Earlier agents encountered usage limits. At the handoff check, no child agents were running. Another model must not assume their processes or memory survive migration.

## 7. Exact current state: not assembled, not finished

Read-only validation on 17 October 2026:

```bash
venv/bin/python src/assemble_manual_full_set.py --validate-only
```

Results: **250 groups drafted, 750 answers present; 19 Mid/Low FK failures remain**. The other **481 of 500** Mid/Low answers satisfy the ±1 band. Failures are only in:

- `author_a_batch_04.json`: `CRI_10` Low.
- `author_a_batch_07.json`: 18 consumer-rights responses listed below.

Snapshot values (recompute after every edit; don't round before testing):

| Topic | Level | Current FK | Allowed FK interval |
| --- | --- | ---: | ---: |
| CRI_10 | Low | 4.759703 | 2.630929–4.630929 |
| CON_01 | Mid | 9.200896 | 6.625751–8.625751 |
| CON_02 | Mid | 7.896190 | 5.029231–7.029231 |
| CON_02 | Low | 6.783548 | 3.047752–5.047752 |
| CON_03 | Mid | 9.182509 | 4.856471–6.856471 |
| CON_03 | Low | 7.606174 | 4.568933–6.568933 |
| CON_04 | Mid | 10.100797 | 5.050403–7.050403 |
| CON_04 | Low | 7.967630 | 3.979390–5.979390 |
| CON_05 | Mid | 8.095333 | 5.194441–7.194441 |
| CON_05 | Low | 5.471789 | 3.146095–5.146095 |
| CON_06 | Mid | 8.671222 | 5.320000–7.320000 |
| CON_06 | Low | 6.447768 | 2.823538–4.823538 |
| CON_07 | Low | 4.573651 | 2.572838–4.572838 |
| CON_08 | Mid | 8.107566 | 4.294793–6.294793 |
| CON_08 | Low | 6.010000 | 2.472941–4.472941 |
| CON_09 | Mid | 10.430687 | 5.794286–7.794286 |
| CON_09 | Low | 7.415791 | 4.512266–6.512266 |
| CON_10 | Mid | 9.429795 | 5.547855–7.547855 |
| CON_10 | Low | 8.868072 | 3.960969–5.960969 |

Current cross-level FK ordering is High > Mid > Low in **249 groups**. The only exception is `IND_06`: High 16.865878, Mid 8.985409, Low 11.286985. Its original Mid baseline is 8.175522 and Low baseline is 10.436002. Thus Mid's maximum allowed 9.175522 is below Low's minimum allowed 9.436002. Both the ±1 bands and Low<Mid cannot be satisfied together. Retain the declared bands and flag this case; excluding/relabeling it before training is a user decision, not an automatic silent change.

Crucially:

- `For_fine_tuning_manual_full` **does not yet exist** in the main CSV.
- The main CSV's existing values remain unchanged.
- `newly_generated_answers/manual_full_set_exports/` currently contains **only `README.md`**. No final JSONL split has been created.
- `evaluation_results/manual_full_set/` does not yet exist. No completed final 250-group metric tables or statistical claims have been produced.
- No Qwen fine-tuning or held-out post-training evaluation has been run for this candidate set.

Integrity checkpoint: reading the original CSV with `dtype=str, keep_default_na=False`, dropping `For_fine_tuning_manual_full` if present, serializing `to_csv(index=False)` and hashing UTF-8 yielded SHA-256:

`2bc813a2edeaa7b0b1932dad7f611d0dc700f369ecb3c103b6771e9bef79b82a`

Use that to check preservation of all pre-existing cell values after assembly. It is a normalized cell-value digest, not the raw file's byte hash.

## 8. Assembly and candidate export helper

`src/assemble_manual_full_set.py` does not generate answers. It:

1. Reads every manual JSON batch and rejects duplicate/unknown topics, empty answers, missing provenance, thinking tags and FK violations.
2. Checks 750 unique source UIDs and preserves all existing columns.
3. Creates/populates **`For_fine_tuning_manual_full`** and atomically replaces the source CSV only after validation succeeds.
4. Writes `evaluation_results/manual_full_set_readability_audit.csv` and `manual_full_set_progress.json`.
5. When all 250 groups pass, runs topic-paired one-sided FK t-tests (High>Mid, High>Low, Mid>Low), Bonferroni correction across three contrasts and paired Cohen's d.
6. Exports all 750 SFT candidate records and deterministic 200/25/25 topic train/validation/test splits (600/75/75 responses), a topic split manifest and `source_provenance.json`.

Use `--require-complete` for final assembly. Never bypass the FK gate, fill missing targets with old answers, or treat the helper's success as expert factual certification. The current helper's hard acceptance gate is the same-level FK bound; inspect ordering separately.

Each JSONL record contains original system/user prompts, the new assistant target, identifiers and split metadata. Some training libraries require stripping non-`messages` fields. The export is only a candidate dataset, not a training run.

## 9. Metric evaluator and cached work

`src/evaluate_manual_full_set.py` requires the assembled complete manual column. It uses the existing `src/current_answer_metrics.py` scorers, not an answer-generation model.

The fair baseline is **original `Answer_only_cleaned` Mid/Low paired with the same corrected High used for the new answers**. It is named `Original_lower_with_corrected_High`. Do not compare new rewrites to a corrected High while comparing original lower answers to a different, erroneous High and call that a controlled before/after comparison.

Metrics/implementation:

- FK: installed `textstat.flesch_kincaid_grade`; word count is whitespace splitting, not token count.
- ROUGE-Lsum precision/recall/F1: `rouge_score`, no stemming; sentence boundaries restored from punctuation after cleaning flattened newlines.
- Semantic similarity: `BAAI/bge-m3`, normalized CLS embeddings and cosine. Semantic loss = 1−cosine; mathematical range 0–2.
- NLI: `dleemiller/ModernCE-large-nli`, average both directions. **Checkpoint config labels are wrong**; probe-verified mapping is contradiction=0, entailment=1, neutral=2. Preserve the verification probes and corrected cache version.
- Posture: `MoritzLaurer/bge-m3-zeroshot-v2.0`, binary entailment-logit softmax for comprehensive/detailed versus minimal/simplified and formal/professional versus casual/conversational. Template: `This text is {label}.` These are classifier scores, not retained-fact percentages.
- Toxicity: `adobe-codemay2025/ModernBERT-base_Toxic_comment_detector`, configured toxic label 1. Also stores both raw class probabilities.
- Entities: `gemini-3.1-flash-lite`, temperature zero, 17-category rubric and canonical-string deduplication. Exact prompt and categories are in `src/current_answer_metrics.py`.

High self-comparisons remain blank. Text inputs are not silently truncated; the existing helpers reject inputs exceeding their explicit 8,192-token policy. Posture tokenizer metadata says 512, but the checked XLM-R model config has 8,194 positional embeddings; earlier full-input scoring completed without truncation. Do not silently switch to a 512-token truncation policy and reuse identical cache keys.

Local cache warm-ups scored finalized batches while remaining prose was revised. They did **not** assemble the CSV or create final tables. As of this handoff:

- `evaluation_results/manual_full_set_metric_cache.json`: exists locally, **8,903 entries**, **46,175,028 bytes**. Content-addressed keys mean changed texts need new scores.
- That cache is ignored/untracked by Git. A fresh clone may not have it and must recompute scores. Do not commit large model caches or expect old tool sessions to resume.
- The older `evaluation_results/paper_metric_cache.json` can supply unchanged baseline scores if present.
- Early partial NLI values were used only to select a few claim-level spot reviews, not as final results. Low NLI did not automatically imply missing facts; do not promote those exploratory scores to the final summary.

Final evaluator outputs under `evaluation_results/manual_full_set/` include per-row new/baseline metrics, level summaries, paired before/after changes with 95% CIs, paper-style contrasts/baseline tests/repeated-measures ANOVA, evaluated-text hashes and limitations metadata.

The default evaluator makes **no paid API calls**; entity counts come only from cache and otherwise remain missing. `--run-entity-api` explicitly enables the existing Gemini extractor with `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the environment and may incur charges. Its module docstring currently describes the default no-paid-API behavior; the CLI option is an explicit exception. `--cpu-only` writes only CPU-derived metrics; it is not a completed GPU-metric evaluation.

## 10. Source accuracy and limitations to preserve

Every batch retains per-topic source links and review notes. Read the actual group before revising it. Important corrections already made include:

- GDPR Article 22: conditional scope and three exceptions, safeguards, and distinct Article 21 objections; not a blanket profiling ban.
- GDPR breach rules: authority notification generally within 72 hours where feasible with a risk exception; high-risk individual communication without undue delay is a different duty.
- Bangladesh PDPO 2025: historical/consolidated instrument, later 2026 repeal; criminal sections had delayed commencement. Wrong original section numbers and automatic penalties were corrected.
- MFS 2018 records: at least six years from origination, not invented five-to-ten years after account closure.
- Bangladesh labour: actual sections, amended maternity periods/pay formula, permanent/temporary notice distinctions, specified overtime components rather than every gross-pay allowance.
- ILO C155: Articles 13, 16, 19(f), 21, not invented attributions; reasonably-practicable and national-implementation qualifications retained.
- Migrant legal remedies: civil suit/legal aid and other routes are not automatic universal extraterritorial Labour Court jurisdiction.
- UNCLOS assistance has serious-danger and reasonably-expected qualifications. SOLAS survival-craft arrangements depend on voyage and approved configuration.
- Battery carriage: not an absolute ban on all spares above 100 Wh; airline approval, upper limits, quantity and special-device/power-bank distinctions matter.
- FAA pressure-altitude design criteria are not a guaranteed unconsciousness countdown or safe waiting period. Yellow-fever certificate lifetime validity is not a universal current itinerary rule.
- OpenAI API no-training default is distinct from consumer controls, retention, deletion and historical model contributions.
- Many science, safety, financial, housing and education High answers also required corrections. Do not restore an old generated claim merely to improve overlap.

Material source limitations are recorded for, among others, blocked Facebook terms, unavailable Amazon notice, unspecified Foodpanda country/edition clauses, full paid IEC/ASME texts and blocked French legal-deposit text. Conditional explanations are intentional. They are not evidence that every current policy was independently verified. Some older rejected claims appear only as explicit corrections; do not add those false-original entities to every level merely to raise raw counts.

## 11. Resume checklist after user authorization

1. Read this file, `docs/literacy_adaptation_metric_ranges.md`, the relevant batches, and applicable repository/assistant instructions. Check Git status; preserve unrelated user changes.
2. Re-run read-only assembly validation to refresh the remaining-failure list.
3. Directly revise only `CRI_10` Low and the failing CON Mid/Low prose. Keep High and the source-corrected factual brief intact unless a demonstrated factual correction is needed. Define dense terms and use genuinely simpler sentences; do not delete exceptions or add filler to game FK. Leave enough margin that a tiny edit does not fail the bound.
4. Validate all 500 Mid/Low bounds and all 250 cross-level orders, retaining the explicit IND_06 exception. Check duplicates, formatting, thinking tags, numbers and practical safeguards. Describe claim-level reviews as spot checks unless all claims are actually checked.
5. Assemble and evaluate:

```bash
venv/bin/python src/assemble_manual_full_set.py --validate-only
venv/bin/python src/assemble_manual_full_set.py --require-complete
venv/bin/python src/evaluate_manual_full_set.py
```

6. Check original-column digest, new-column completeness, JSONL counts, topic-disjoint splits, exact evaluated-text hashes and actual metric results. Do not substitute zeros for unavailable entities.
7. Report observed readability effects and information-retention changes honestly. Readability significance is descriptive because it was constrained during authoring. No claim of equivalence, human comprehension improvement or successful fine-tuning follows automatically.
8. Deliver the CSV column, candidate exports and reproducible scores with material caveats. Do not start training, invoke paid extraction, publish further changes or push future work without the appropriate user authorization.

## 12. Security and collaboration practices

- A Gemini credential was exposed in an earlier chat. **It is intentionally omitted here. Never recover, repeat, commit, or embed it.** Use a fresh environment credential only if the user chooses an API workflow; advise rotation of exposed credentials where appropriate.
- No external API was used to author these manual responses. Local evaluation models only score text.
- Use `apply_patch` for source/data-draft edits in this workspace; generated CSV/JSONL serialization is handled by the helper scripts. Avoid destructive Git commands and broad deletion.
- Do not run generation notebooks or overwrite old answer columns to resume this manual task.
- Keep brief progress updates during long work. Do not label drafts, a warm cache, or unrun scripts as completed final outputs.
- The original environment offered data-analysis/notebook/validation skills; another runtime should follow its own applicable skill instructions, not depend on inaccessible local skill paths or old agent IDs.

Suggested restart message for another assistant: “Read `codex.md` and the cited project files. Continue the unfinished direct-authored 250-group dataset from the saved batches. Fix the remaining readability violations, preserve the factual brief and original CSV columns, then assemble and evaluate. Do not regenerate everything from scratch or use Qwen to write the targets.”
