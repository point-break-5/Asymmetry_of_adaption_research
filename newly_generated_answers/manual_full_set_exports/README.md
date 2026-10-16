# Assistant-authored literacy adaptation candidates

## Contents

The source CSV gains `For_fine_tuning_manual_full` only after all 250 topic groups pass assembly validation. The existing answer columns are preserved. This column contains 750 plain-text responses: a source-reviewed High reference and directly assistant-authored Mid and Low responses for each topic. Qwen and generation APIs did not author these responses. The three previously reviewed DIG_01–03 groups are reused seeds, explicitly identified in their batch metadata.

`assistant_authored_all.jsonl` contains all 750 candidates. The other JSONL files use a deterministic topic-level split: 200 training topics, 25 validation topics, and 25 test topics, with all three literacy variants kept together. The messages preserve the corresponding original system/user prompts and use the new response as the assistant target. Additional record identifiers and split metadata may need removing for a trainer that accepts only `messages`.

These files are **candidates**, not evidence of a successful fine-tune. No training has been started. Keep the test topics out of training and model-selection decisions; shared laws and concepts can still span topics, so this is not a guarantee of domain-level independence.

## Authoring constraints

- Preserve the verified factual brief: conditions, exceptions, rights, duties, practical steps, entities, technical identifiers, numbers and uncertainty. Correct unsupported High claims rather than teaching their errors equally at all levels.
- Keep every Mid/Low Flesch–Kincaid grade within ±1 of its original same-level `Answer_only_cleaned` baseline, using the installed `textstat` implementation.
- Prefer High > Mid > Low difficulty within each topic, without silently relaxing the baseline bands. `IND_06` has incompatible original Mid/Low intervals: its Low minimum exceeds its Mid maximum. The audit records this exception; review whether to exclude or relabel it before training.
- Use plain language, shorter sentences and definitions rather than deleting substantive conditions. More accessible wording may require **more**, not fewer, words.
- Do not treat ROUGE or entity count as permission to repeat false claims, add unrelated names, or pad the answer.

FK is a surface estimate, not a human comprehension test. The statistical readability contrasts are descriptive because readability was constrained during authoring. No numerical ROUGE, embedding, NLI or entity-equivalence threshold was prospectively imposed; the evaluation must not claim otherwise.

## Sources and limits

`source_provenance.json` and the authoring batches retain per-topic source links, correction notes, retrieval/version limitations and authorship. Some primary pages were blocked, unavailable, or paywalled; some exact country-specific agreements were unspecified. Those explanations use qualified claims rather than invented current terms. They still need appropriate specialist review before high-stakes deployment.

Several prompts contain inaccurate premises or refer to historical instruments. The targets correct those premises and identify historical scope where relevant. They must not be presented as a comprehensive, up-to-date legal or medical knowledge base. Source review is not a blanket expert certification of all statements.

## Reproduce assembly and evaluation

From the repository root, using the project's environment:

```bash
venv/bin/python src/assemble_manual_full_set.py --require-complete
venv/bin/python src/evaluate_manual_full_set.py
```

The first command validates and assembles the handwritten batches; it does not generate text. The second runs existing local scoring models and writes tables under `evaluation_results/manual_full_set/`. It compares both new and original Mid/Low answers against the **same corrected High** references. It records exact evaluated-text hashes, paired topic-level changes, confidence intervals and paper-style contrasts. High self-comparisons are blank, not trivial scores of one.

Entity extraction defaults to cached results only. Missing counts stay missing, not zero. To explicitly request the existing Gemini extractor, set a fresh `GEMINI_API_KEY` or `GOOGLE_API_KEY` in the environment and add `--run-entity-api`; that option sends answer text to the configured API and may incur charges. Never put credentials in notebooks, commits or datasets.

Overlap, embeddings, whole-response NLI, posture and raw entity counts are imperfect proxies. Similar scores do not establish identical facts, and a non-significant gap does not demonstrate statistical equivalence. A claim-level audit and reader comprehension checks remain useful before training; held-out model generation must be evaluated after training.
