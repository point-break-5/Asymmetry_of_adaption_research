# Source notes

This package was assembled from the user-supplied `Data.zip`, `Software.zip`, and paper PDF. Only Qwen-specific response/extraction files and directly relevant Qwen collection/extraction scripts were copied into this package.

The original paper's statistical design uses event-ID paired comparisons and three literacy levels. The notebook keeps that structure but adds an event-level holdout so the local model is evaluated on unseen events after fine-tuning.

Current model references used by the notebook:
- Qwen/Qwen3-4B-Instruct-2507
- BAAI/bge-m3
- dleemiller/ModernCE-large-nli
- MoritzLaurer/bge-m3-zeroshot-v2.0
