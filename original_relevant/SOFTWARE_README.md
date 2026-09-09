# Supplementary Materials

## Section 1: Licensing and Terms of Use

### 1.1 This package
The contents of this package (dataset and code) are
released under the [CC BY 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
 See the accompanying `LICENSE` file for the full text.

### 1.2 External evaluation models — licenses
- **BGE-M3** (`BAAI/bge-m3`) — [MIT License](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/mit.md)
- **ModernCE-large-NLI** (`dleemiller/ModernCE-large-nli`) — [MIT License](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/mit.md) built on ModernBERT-large.
- **bge-m3-zeroshot-v2.0** (`MoritzLaurer/bge-m3-zeroshot-v2.0`) — [MIT License](https://huggingface.co/datasets/choosealicense/licenses/blob/main/markdown/mit.md), NLI-based zero-shot classifier.

## 1.3 Evaluated LLMs & Terms of Use

All response generation utilized official provider APIs or open-weight releases in accordance with each provider's published terms of service and licensing agreements.

### Audited Models

- **GPT-5.4** (OpenAI) was accessed via OpenAI's official API and used in accordance with its [terms of use](https://openai.com/policies/terms-of-use).

- **Claude Opus 4.6** (Anthropic) was accessed via Anthropic's official API and used in accordance with its [commercial terms of service](https://www.anthropic.com/legal/commercial-terms).

- **Gemini 3.1 Pro** (Google DeepMind) was accessed via Google's official API and used in accordance with its [generative AI terms](https://policies.google.com/terms/generative-ai).

- **Llama 4 Scout** (Meta) was accessed under its open-weights release and used in accordance with the [Llama community license](https://www.llama.com/llama4/license/).

- **Qwen3.6-27B** (Qwen Team, Alibaba Group) was accessed under its open-weights release and used in accordance with the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).

### Entity Extractor

- **Gemini 3.1 Flash Lite** (Google DeepMind) was accessed via Google's official API (configured at temperature 0) and used as a category-driven extractor for the Specific Entity Count metric, in accordance with Google's [generative AI terms](https://policies.google.com/terms/generative-ai).

### 1.4 Dataset source materials
The 250-event dataset is composed of publicly available authoritative
documents drawn from:
- International conventions and treaties (UN, ICRC, regional bodies)
- National legislation and regulatory instruments (Bangladesh, EU, US,
  UK, India, Canada, Germany, France, Philippines)
- International organisations and monitoring bodies (WHO, ILO, IAEA,
  ICAO, IATA, FATF, UNHCR, etc.)
- Regulatory and technical standards (OSHA, NEC, ASME, ICRP, ICH, NIST,
  IEEE/NERC, IETF, IEC, Codex Alimentarius, etc.)
- Scientific and clinical guidelines (WHO IHR, AHA, ADA, IPCC, etc.)
- Service-provider terms of service and privacy policies (Meta, TikTok,
  WhatsApp, Telegram, Amazon, OpenAI, PayPal, Uber, Foodpanda).
- Statistical and indicator reports (UNHCR Global Trends, WFP, ILO/Walk
  Free, World Inequality Lab/Oxfam, etc.).

Full categorised list is provided in Appendix of the paper. No
private or restricted material is included. All sources are publicly
accessible and used in accordance with their respective terms.

### 1.5 Data privacy and content safety
No personally identifying information appears in any prompt, response,
or intermediate artifact. References to named individuals (researchers
cited in scientific guidelines; named entities in legal source
materials) appear only as part of publicly cited source documentation. A supplementary toxicity check (Appendix E of the paper) used a
publicly available ModernBERT-base classifier under Apache 2.0.


## Section 2: Model Sizes and Computational Resources

### 2.1 LLMs evaluated (response generation)
No model was trained or fine-tuned. All response generation used
proprietary or open-weight APIs on their default settings.

| Model | Provider | Parameters |
|---|---|---|
| GPT-5.4 | OpenAI | Not publicly disclosed |
| Claude Opus 4.6 | Anthropic | Not publicly disclosed |
| Gemini 3.1 Pro | Google DeepMind | Not publicly disclosed |
| Llama 4 Scout | Meta | Mixture-of-Experts; 17B active / 109B total |
| Qwen3.6-27B | Qwen Team | ~27B |

### 2.2 Evaluation models (downstream metrics)
| Model | Use | Parameters |
|---|---|---|
| BGE-M3 | Semantic similarity | ~570M |
| ModernCE-large-NLI | Bidirectional NLI | ~395M (ModernBERT-large backbone) |
| bge-m3-zeroshot-v2.0 | Zero-shot info + style classification | ~570M (BGE-M3 backbone) |
| Gemini 3.1 Flash Lite | Specific-entity extractor (temperature 0) | Not publicly disclosed |

### 2.3 Compute infrastructure
All local inference used a NVIDIA  RTX 5060Ti 16GB.
LLM response generation and entity extraction were performed via API calls.
Semantic Similarity, NLI inference, Zero Shot Posture analysis used the NVIDIA  RTX 5060Ti 16GB GPU. CPU-only steps (statistics,
plotting, dataset construction) ran on a standard laptop.

### 2.4 Total GPU usage
Approximately **3–4 hours** of NVIDIA  RTX 5060Ti 16GB GPU time across all evaluation passes
(embedding generation, NLI scoring, zero-shot classification). No
repeated runs or random-seed averaging were performed; each reported
result reflects a single API call run, consistent with the audit
framing.

### 2.5 Data preprocessing
Minimal preprocessing was applied. Markdown artifacts and web-specific
formatting were stripped from all model responses prior to evaluation,
since transformer-based evaluators are demonstrably sensitive to surface
format features. MInimal blank row removal , sorting was applied during experiment.


## Section 3: AI Writing Assistance Declaration

In line with ACL 2023 guidelines on AI writing assistants (https://2023.aclweb.org/blog/ACL-2023-policy/), we disclose the limited use of generative AI tools in the preparation of this paper. AI was used for grammar and fluency enhancement, predictive text suggestions during drafting, and literature search assistance. According to ACL guidelines, these specific uses do not require formal disclosure; we provide this information voluntarily for completeness and transparency. No AI-generated content or ideas were used in research design, analysis, or writing of results and conclusions. All references and data were manually verified for accuracy.

## Section 4: Package Contents

```
 Software/                          # cleaned analysis code
   ├── questiongenerator_implicit/  # question generators code for implicit response collection
   ├── responsecollector_explicit/  # Response Collection code across LLMs (explicit)
   ├── responsecollector_implicit/  # Response Collection across LLMs (implicit)
   ├── factextract.py              # specific-entity extractor
   ├── fk_grade.ipynb              # FK + word count
   ├── rougelsum.ipynb               # ROUGE-Lsum
   ├── semanticsimilarity.ipynb       # BGE-M3 semantic similarity
   ├── nli.ipynb                   # ModernCE-large-NLI
   └── postureanalysis.ipynb       # bge-m3-zeroshot-v2.0 posture analysis
Data/
    ├── responses/                  #  explicit + implicit responses across LLMs
    ├── extractions/                # per-response entity extractions
    └── globaldata/                 # explicit dataset + implicit question
```

## Section 5: Reproducing the Analysis
**Python version:** 3.10+ required

1. Install dependencies: `pandas`, `numpy`, `scipy`, `textstat`,
   `rouge_score`, `sentence-transformers`, `transformers`, `python-dotenv`, `matplotlib` and the
   provider-specific SDKs.
2. Configure API keys for the four required providers (OpenAI,
   Anthropic, Google, Meta/Qwen open-weight) via environment variables.
3. Run each notebook in to reproduce per-metric
   outputs.
4. Statistical analyses (paired tests, Cohen's d, Bonferroni, RM-ANOVA,
   single-sample tests) follow the framework described in Appendix B.1
   of the paper.

Random seeds were not used for averaging (single-run audit, as noted in
Section 2.4). All paired tests are one-tailed and paired by event ID.
