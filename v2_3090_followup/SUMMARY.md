# Qwen3.6-35B-A3B · 3090 spec-decode follow-up bench (v2)

In response to Oleg-dM's comment on HF discussion.

## Setup
- llama.cpp commit 97895129e (master, post PR #19493)
- RTX 3090 24 GB, single GPU, driver 580.126, CUDA 12.0
- GPU at stock clocks (graphics 1965 MHz current / 2100 max; memory 9751 MHz; power limit 350W default)
- gcc 13.3.0, Ubuntu 24.04
- common flags: -ngl 999 -c 16384 -fa on -ctk q8_0 -ctv q8_0 -n 200 --temp 0.5 --seed 42 -no-cnv -st
- 5 diverse prompts, /no_think appended to disable Qwen3 reasoning

## Results (tok/s, N=5 per config)

| Config | mean | min | max |
|---|---:|---:|---:|
| baseline (no spec-decode) | 139.9 | 139.7 | 140.0 |
| -md --draft-max 8 (default --draft-min=5) | 56.5 | 51.5 | 63.0 |
| -md --draft-max 16 (default --draft-min=5) | 55.7 | 53.3 | 62.7 |
| -md --draft-max 32 (default --draft-min=5) | 55.3 | 52.9 | 63.1 |
| -md (full defaults) | 55.5 | 52.8 | 62.3 |
| **Oleg: --draft-min 2 --draft-max 32** | **65.0** | 61.0 | 75.8 |
| -md --draft-min 2 --draft-max 16 | 66.3 | 60.6 | 76.6 |
| -md --draft-min 2 --draft-max 64 | 64.7 | 60.6 | 75.3 |
| srogmann-style: --draft-min 48 --draft-max 64 | 85.6 | 81.3 | 88.0 |

Draft model: Qwen3.5-0.8B-Q4_K_M (508 MB), vocab-matched to Qwen3.6-35B-A3B.

## Conclusion
- 100% acceptance is genuine (verbose log confirms 115 accepted / 115 generated).
- NO draft-model configuration on this 3090 box beats baseline 139.9 tok/s.
- Aggressive draft windows (min=48/max=64) give 85.6 tok/s -- least bad, still -39%.
- Oleg's suggestion beats the defaults but still -54%.
