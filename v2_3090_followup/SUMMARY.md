# Qwen3.6-35B-A3B · 3090 spec-decode follow-up bench (v2)

In response to Oleg-dM's comment on HF discussion #14.

## Setup

- **Tested at two llama.cpp commits** (to rule out stale-commit artefact):
  - `97895129e` — original bench's commit (same as short-hash `9789512`)
  - `bcb5eeb64` — current master at time of bench, includes PR #22227
    `speculative-simple : add checkpoint support`
- RTX 3090 24 GB, single GPU, driver 580.126, CUDA 12.0
- GPU at **stock clocks** (graphics 1965 MHz current / 2100 max;
  memory 9751 MHz; power limit 350 W default — no overclocking)
- gcc 13.3.0, Ubuntu 24.04
- common flags: `-ngl 999 -c 16384 -fa on -ctk q8_0 -ctv q8_0 -n 200
  --temp 0.5 --seed 42 -no-cnv -st`
- 5 prompts spanning reasoning / code / factual / procedural / creative,
  with `/no_think` appended to disable Qwen3 reasoning for
  apples-to-apples tok/s measurement
- Draft model: `unsloth/Qwen3.5-0.8B-Q4_K_M.gguf` (508 MB,
  vocab-matched to Qwen3.6-35B-A3B)

## Results on `97895129e` (tok/s, N=5 per config)

| Config | mean | min | max |
|---|---:|---:|---:|
| baseline (no spec-decode) | 139.9 | 139.7 | 140.0 |
| `-md --draft-max 8` (default `--draft-min=5`) | 56.5 | 51.5 | 63.0 |
| `-md --draft-max 16` (default `--draft-min=5`) | 55.7 | 53.3 | 62.7 |
| `-md --draft-max 32` (default `--draft-min=5`) | 55.3 | 52.9 | 63.1 |
| `-md` (full defaults) | 55.5 | 52.8 | 62.3 |
| **Oleg: `--draft-min 2 --draft-max 32`** | **65.0** | 61.0 | 75.8 |
| `-md --draft-min 2 --draft-max 16` | 66.3 | 60.6 | 76.6 |
| `-md --draft-min 2 --draft-max 64` | 64.7 | 60.6 | 75.3 |
| srogmann-style: `--draft-min 48 --draft-max 64` | **85.6** | 81.3 | 88.0 |

## Cross-validation on current master `bcb5eeb64`

Same config, same prompts, same hardware, same session:

| Config | `97895129e` | `bcb5eeb64` master | Δ |
|---|---:|---:|---:|
| baseline | 139.9 | 139.5 | −0.3 % (noise) |
| Oleg `--draft-min 2 --draft-max 32` | 65.0 | 65.2 | +0.3 % |
| srogmann `--draft-min 48 --draft-max 64` | 85.6 | 85.6 | 0 % |

**Master gives the same results** — PR #22227 does not change the
behaviour for this workload. The regression is not a stale-commit
artefact.

## Conclusions

1. **100 % `n_acc_tokens / n_gen_tokens` is genuine**. Verified by
   source read of `common/speculative.cpp` (counter incremented in
   `common_speculative_accept()` as `n_acc_tokens += n_accepted`,
   post-verify) and a `--verbose` run emitting
   `draft acceptance rate = 1.00000 (115 accepted / 115 generated)`.
2. **No draft-model spec-decode configuration beats baseline on this
   box.** Losses range from −39 % (srogmann recipe) to −60 % (default
   `--draft-min=5` with small `--draft-max`).
3. Oleg's `--draft-min 2 --draft-max 32` suggestion beats the default
   by ~10 tok/s (65 vs 55) but is still −54 % vs baseline 139.9.
4. **Aggressive draft windows (`--draft-min 48 --draft-max 64`) are
   the least bad** — contrary to the "wasted compute" intuition,
   larger draft windows amortise the verify / KV-management
   overhead enough to partially hide the cost.
5. The original bench's "mean 120 / bimodal tail 59" is the
   mixture of two regimes — v2's consistent 55–85 is the
   "spec-decode always active" regime isolated.

## Files

- `v2_oleg_suggestions/` — 4 configs × 5 prompts + `verbose.log`
- `v2_controls/` — 5 control configs × 5 prompts (A-E)
- `v2_master_cross_check/` — 3 configs × 5 prompts on master
  `bcb5eeb64`
- `bench_3090_oleg.sh` — reproducible script
