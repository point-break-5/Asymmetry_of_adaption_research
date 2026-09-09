# Qwen Before/After Literacy-Stratification Audit

This package is a Qwen-only reproduction/extension of the supplied *The Asymmetry of Adaptation* audit.

## What it does

1. Loads only the supplied Qwen3.6-27B response files and Qwen-specific entity extractions.
2. Splits the 250 event IDs into an **80/20 event-level train/test split**. No test event is used during fine-tuning.
3. Evaluates the historical Qwen3.6-27B responses on the held-out events.
4. Generates a **pre-fine-tuning baseline** from a local Qwen model.
5. Fine-tunes that same local Qwen model with LoRA/QLoRA on the Qwen response demonstrations from the training events.
6. Generates responses again on the exact same held-out explicit and implicit prompts.
7. Re-runs the paper-aligned evaluation metrics.
8. Produces before/after tables, paired statistics, figures, and a compact report.

## Local training target

Default: `Qwen/Qwen3-4B-Instruct-2507`.

The supplied audit's Qwen3.6-27B is the historical reference system. It is not assumed to be trainable on a 16 GB consumer GPU. The 4B instruct model is a deliberately smaller local target so the full experiment can be executed on the RTX 5060 Ti 16 GB.

The notebook supports both 4-bit QLoRA and a 16-bit LoRA fallback. The fallback is useful if a quantization backend is unavailable on the local machine.

## Recommended environment

Linux + NVIDIA driver + CUDA-enabled PyTorch. Python 3.10–3.12 is recommended.

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then start Jupyter:

```bash
jupyter lab
```

Open:

`notebooks/01_qwen_before_after_audit.ipynb`

## Run order

Execute the notebook top-to-bottom. The default `SMOKE_TEST=True` is designed to verify the pipeline on a tiny subset before spending GPU time. Turn it off only after the smoke test succeeds.

The intended full flow is:

```text
supplied Qwen responses
        ↓
held-out historical evaluation
        ↓
local Qwen base generation (before fine-tune)
        ↓
LoRA/QLoRA training on train events only
        ↓
local Qwen fine-tuned generation (after)
        ↓
paper-aligned metrics
        ↓
before/after comparison
```

## Metrics

The notebook implements the measurement families used in the supplied paper:

- Flesch–Kincaid grade + word count
- ROUGE-Lsum vs the High-literacy reference
- Specific Entity Count (historical Qwen counts are supplied; new generations can optionally be extracted with the supplied Gemini-based extractor if `GEMINI_API_KEY` is configured)
- BGE-M3 semantic loss: `1 - cosine(high, target)`
- ModernCE-large-NLI bidirectional entailment / neutral / contradiction
- BGE-M3 zero-shot posture: comprehensive-and-detailed; formal-and-professional

The statistical notebook section uses event-ID paired comparisons. This follows the supplied paper rather than treating High/Mid/Low responses as independent samples.

## Important scientific interpretation

The primary causal question here is intentionally modest: **does fine-tuning change the local model's literacy-conditioned response stratification?** Improvement is not assumed. In particular, shorter responses are not treated as harm by themselves; the content metrics are interpreted together.

The historical Qwen3.6-27B scores are shown as a contextual reference. The main before/after comparison is **Local Base Qwen3-4B vs Local Fine-Tuned Qwen3-4B on the same held-out event IDs**.

## Entity extraction

The original supplied Qwen extraction TSVs are included and are used directly for the historical Qwen3.6-27B baseline.

For new local generations, exact paper-style Specific Entity Count requires the external extractor used by the original package. Set:

```python
USE_GEMINI_ENTITY_EXTRACTOR = True
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

otherwise the notebook will keep the entity metric as `NaN` for new generations and will still complete all non-API metrics.

## Outputs

The notebook writes to `results/`:

```text
before_after_raw.csv
before_after_summary.csv
paired_statistics.csv
historical_qwen_summary.csv
training_manifest.json
split_event_ids.csv
figures/*.png
```

The final cell prints the key before/after table and saves `results/BEFORE_AFTER_REPORT.md`.

## Source provenance

Only Qwen samples from the supplied `Data.zip` are used as experiment data. Relevant Qwen collection and extraction files from `Software.zip` are copied into `original_relevant/`.

The methodology and metric framing are derived from the supplied paper. The package does not add other model response data from the supplied archives.
