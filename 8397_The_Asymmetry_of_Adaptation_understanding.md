# Understanding *The Asymmetry of Adaptation: A Literacy-Conditioned Stratification Audit of LLMs*

## The paper's central point

The paper is about a failure of **information parity**, not a failure of readability adaptation.

LLMs correctly notice or are told that users have different literacy levels, and they respond by changing vocabulary, sentence structure, length, formality, and explanatory style. That part works. The problem is that the models also change **what information they provide**. As the user's apparent literacy decreases, answers generally contain fewer concrete facts, named laws and organizations, article or section references, dates, thresholds, exceptions, procedural conditions, and other actionable details. The answers do not merely become easier to read; they become substantively thinner.

The paper calls this **the asymmetry of adaptation**: linguistic complexity is reduced, but the model does not preserve an equivalent informational core. Users who may have the greatest need for a clear explanation can therefore receive the least complete version of it.

The desired behavior is:

> Change the form of the answer to match the reader, while keeping the essential substance and actionable information available across literacy levels.

The behavior observed in the paper is:

> Change both the form and the amount or scope of information according to the reader's apparent literacy.

## Where the problem exists

The problem appears at several connected levels.

### 1. In the model's content-selection behavior

The primary failure occurs when the model decides which facts to include. Lower-literacy answers tend to omit details that appear in the same model's high-literacy answer. This means the issue is not simply difficult wording. It is a difference in the model's response planning or content selection conditioned on its perception of the user.

The omissions may include:

- legal provisions and article numbers;
- exceptions and qualifying conditions;
- deadlines, durations, monetary values, and quantitative thresholds;
- named organizations, standards, policies, and procedures;
- safeguards, remedies, and steps a user can take;
- technical identifiers and domain-specific facts.

The GDPR example makes the distinction concrete. The high-literacy answer explains Article 22, related Articles 13, 14, and 15, Recital 71, the three exceptions under Article 22(2), safeguards under Article 22(3), special-category data, meaningful human intervention, and transparency obligations. The low-literacy answer preserves the broad idea that a person can request human review, but drops most of that legal structure. It is easier to understand, but it is not an informationally equivalent rendering.

### 2. Across both explicit and inferred literacy signals

The effect occurs in two settings:

- **Explicit condition:** the scenario, details, source, system instruction, and prompt structure are held constant, while the persona says High, Mid, or Low literacy. This is the cleanest evidence that the literacy label itself changes the answer.
- **Implicit condition:** the answering model receives only a naturally phrased question and a neutral system prompt. It is not given a literacy label. The model infers something about the user's competence from the wording of the question and still changes the substantive scope of the answer.

The implicit result is particularly important ethically. A user does not have to ask for a simplified or shortened answer. The model may infer low expertise from spelling, vocabulary, brevity, or question structure and silently provide less information. In this condition, however, the generated questions also vary in focus and wording, so it is a more realistic but less tightly controlled causal comparison than the explicit condition.

### 3. Across models, domains, and model families

The main audit tests GPT-5.4, Claude Opus 4.6, and Gemini 3.1 Pro on 250 scenarios covering 32 legal, regulatory, medical, civic, financial, scientific, and safety-critical domains. The direction of the effect is consistent across all main model-condition cells.

The appendix repeats the audit with Llama 4 Scout and Qwen3.6-27B. Both reproduce the central pattern. Qwen3.6-27B produces longer, more entity-rich answers than Llama 4 Scout, but its content still contracts as the signalled literacy level falls. Therefore, the problem is not presented as a peculiarity of one provider or only of closed models.

The per-domain analysis shows that the overall High > Mid > Low pattern holds in the great majority of domains. A few implicit-condition domain cells do not follow it, sometimes because a narrowly worded lower-literacy question elicits a denser answer than a broader high-literacy question. These exceptions matter, but they do not reverse the aggregate cross-model pattern.

### 4. Most seriously in high-stakes information access

This behavior matters most where omitted information changes what a person can understand or do: legal rights, medical guidance, digital privacy, public benefits, financial regulation, immigration, cybersecurity, and safety procedures. A missing exception, threshold, deadline, or remedy may make an otherwise readable answer less actionable.

The equity concern is therefore a **service asymmetry**. Apparent literacy becomes a basis for allocating different levels of substantive informational access. The user receiving the reduced answer may not know that a fuller version exists and may be less able to obtain it elsewhere.

## What the experiment actually measures

The paper separates three dimensions that should not be conflated.

| Dimension | Measures | What it is intended to show |
|---|---|---|
| Linguistic register | Flesch-Kincaid grade, word count, ROUGE-Lsum | Whether wording, difficulty, length, and lexical structure change with literacy |
| Substantive preservation | Specific entity count, BGE-M3 semantic loss, bidirectional NLI | Whether concrete information, overall meaning, and inferential content remain aligned |
| Informational and stylistic posture | Probability of “comprehensive and detailed” and “formal and professional” | Whether the answer presents itself as a full, authoritative treatment or a minimal, conversational one |

For each model and topic, the high-literacy answer is used as the within-model reference. Mid- and Low-literacy answers are compared with it. This is a controlled way to detect differential treatment, but it is crucial that the high-literacy answer is **not external ground truth**.

The specific-entity extractor uses Gemini 3.1 Flash Lite at temperature 0 and counts distinct items across 17 categories, with rules to prevent duplicate counting. The semantic metric is `1 - cosine similarity` using BGE-M3. The NLI analysis compares the two answers in both directions and averages the entailment, neutral, and contradiction probabilities.

## What the results demonstrate

### The models adapt the linguistic register

Every model-condition cell shows a monotonic High-to-Mid-to-Low reduction in Flesch-Kincaid grade and response length. For example, Claude's explicit-condition mean falls from grade 15.81 and 647 words at High literacy to grade 5.49 and 384 words at Low literacy. This establishes that the manipulation successfully changes the answers' register.

### Concrete informational specificity collapses

Specific entity counts fall sharply with literacy. In the same Claude explicit condition, the mean is 23.14 entities at High, 7.75 at Mid, and 4.87 at Low—about a 79% reduction from High to Low. Similar contractions occur for GPT and Gemini. The open-source replication has the same direction; for example, Qwen3.6-27B's explicit-condition means are 24.47, 8.92, and 3.77.

### Meaning diverges before the lowest level

BGE-M3 semantic loss is already significantly above the identical-response baseline for High-to-Mid comparisons and increases further for High-to-Low comparisons. Thus, substantive drift is not confined to an extreme “Low” persona. It begins as soon as the literacy signal weakens.

### The main mechanism looks like omission, not contradiction

The most important diagnostic result is the NLI decomposition. Entailment between the high-literacy answer and the lower-literacy answer falls, while contradiction generally remains very low—below 0.05 in the main models. The lost entailment is replaced mainly by higher **neutral** probability.

In practical terms, lower-literacy answers usually do not say the opposite of the high-literacy answers. They say less. This supports the paper's interpretation that content is being omitted rather than systematically falsified.

### Informational posture changes together with style

Lower-literacy responses are classified as less comprehensive and less formal. For Claude in the explicit condition, the probability of “comprehensive and detailed” falls from 0.80 at High literacy to 0.11 at Low. The paper interprets the co-occurrence of easier language, reduced factual specificity, weaker semantic alignment, lower entailment, and a more minimal posture as convergent evidence of stratification.

### The effects are statistically strong

The study uses paired comparisons by event ID, repeated-measures ANOVA, effect sizes, and Bonferroni correction. Most effects are large to huge, and the reported within-cell contrasts remain significant after correction. The argument therefore does not rest on a few illustrative responses or only on mean differences.

## What the paper is not claiming

The paper carefully limits its conclusion.

- It does not claim that every shorter answer is worse.
- It does not claim that every named entity is useful or that a larger entity count automatically means higher quality.
- It does not claim that formal, technical language should be given to every user.
- It does not claim that simplification itself is harmful. Plain-language communication is treated as a public good.
- It does not claim that the high-literacy answer is always correct, complete, or ideal.
- It does not directly establish that a particular omitted item causes real-world harm.
- It does not evaluate actual comprehension or task success with real users.
- It does not argue that safety restrictions should be removed or that harmful or restricted information must be distributed uniformly. Its claim concerns lawful, appropriate, high-stakes information.

The demonstrated claim is narrower and defensible: changing only—or inferring—a literacy signal systematically co-varies with the substantive scope of the answer.

## Important limitations

### The high-literacy response is a relative reference

Because the paper compares lower-literacy outputs with the same model's high-literacy output, it detects asymmetry but cannot by itself determine the ideal answer. The high-literacy response could contain unnecessary detail, errors, or hallucinated specifics. A stronger evaluation would compare every level with an expert-verified, level-appropriate answer containing a shared canonical fact set.

### Length is a major confound

ROUGE recall, raw entity count, and some NLI omission patterns are sensitive to length. The models voluntarily make lower-literacy answers shorter, so brevity is part of the observed behavior, but this design does not fully separate the causal effect of shorter length from the effect of literacy-conditioned content removal. The authors explicitly propose matched-length generation, length-normalized entity rates, and content-preserving simplification prompts as future tests.

### The metrics are useful proxies, not final judgments

- Flesch-Kincaid measures sentence length and syllables, not true comprehension, domain knowledge, or accessibility.
- ROUGE can miss valid paraphrases and reward copied wording.
- Embedding distance detects broad semantic movement but cannot identify the missing fact.
- The NLI model is trained on general-domain data, not each of the 32 specialist domains.
- The automated entity extractor may miss equivalent expressions or misclassify details.
- Binary posture labels reduce continuous and culturally variable communication styles to broad categories.

The strength of the paper is triangulation across these imperfect measures, not the infallibility of any one metric.

### Literacy is simplified into three abstract labels

Real literacy and domain expertise are continuous, multidimensional, and context-dependent. The study deliberately separates literacy from race, gender, and socioeconomic status and does not make claims about real demographic groups. Its personas are experimental abstractions.

### The dataset and decoding setup bound generalization

The dataset is broad but still curated, English-language, non-adversarial, and focused on publicly available high-stakes information. The models are tested with provider-default decoding settings and without repeated generations across seeds. Results may differ under other prompts, languages, sampling settings, fine-tuning methods, or conversational histories.

### Real-user consequences remain untested

The paper demonstrates differential informational service, not downstream behavioral harm. Human studies are needed to determine which omissions are consequential, whether users understand and retain the answers, and whether a content-equivalent plain-language answer improves decisions.

## What the actual research and engineering target should be

For the present kind of literacy-adaptive generation task, the goal should not be to make High, Mid, and Low answers lexically identical. That would defeat adaptation. The goal is to preserve a **shared informational floor** while permitting controlled differences in expression.

Across levels, the following should remain stable:

- the core factual claims;
- rights, duties, risks, and available remedies;
- critical exceptions and eligibility conditions;
- deadlines, thresholds, and safety limits;
- the procedural steps needed to act;
- uncertainty and important qualifications;
- source identity when it is necessary for verification or action.

The following can appropriately change:

- vocabulary and sentence complexity;
- paragraph structure and amount of scaffolding;
- whether a technical term is defined immediately;
- use of examples, analogies, headings, and step-by-step presentation;
- tone and formality;
- repetition used to support comprehension.

This also means that no single optimization metric is sufficient. Maximizing ROUGE-Lsum alone can discourage legitimate paraphrasing; maximizing raw entity count can reward irrelevant detail or hallucinated names; maximizing answer length can preserve neither correctness nor usefulness. A suitable objective needs readability constraints **and** content-fidelity constraints, ideally measured against a verified canonical fact set rather than only against the high-literacy generation.

The clearest operational interpretation of the paper is:

> Simplify the language, not the user's entitlement to the information.

## Overall understanding

The paper identifies a systematic mismatch between the democratic promise of adaptive LLMs and their observed behavior. The systems appear helpful because they successfully make answers easier and friendlier, but beneath that surface adaptation they often allocate less substantive information to users they perceive as less literate. The disparity is mainly created through silent omission, is visible even at the middle literacy level, occurs when literacy is explicitly stated or merely inferred, spans many high-stakes domains, and persists in both proprietary and open-source model families.

The appropriate remedy is not to stop adapting language. It is to decouple **linguistic difficulty** from **informational completeness**: establish a domain-specific minimum content set, express that content at the requested reading level, disclose when a shortened rendering is being provided, offer access to the fuller version, and use domain experts to determine which omissions would matter in practice.
